"""Run the frozen Linux/Open MPI M4 matrix sequentially; preserve every invocation.

Each configuration's full-field correctness run is its excluded warmup.
Five measured fresh invocations per configuration follow in shuffled rounds.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import time


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command, env, timeout):
    start = time.perf_counter()
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate()
        return -1, out, err + '\nTIMEOUT', time.perf_counter() - start
    return process.returncode, out, err, time.perf_counter() - start


def configurations(protocol):
    result = []
    for grid in protocol['strong']:
        for kind in ('serial', 'mpi', 'openmp'):
            for p in ([1] if kind == 'serial' else protocol['parallelism']):
                result.append(dict(suite='strong', kind=kind, p=p, **grid))
    for grid in protocol['scaled']:
        for kind in ('serial', 'mpi', 'openmp'):
            result.append(dict(suite='scaled', kind=kind, p=1 if kind == 'serial' else grid['p'],
                               target_p=grid['p'], N=grid['N'], M=grid['M']))
    for k, config in enumerate(result):
        config.update(id=k, T=protocol['T'], alpha=protocol['alpha'])
    return result


def parse_summary(text):
    # Open MPI binding diagnostics are deliberately retained but not parsed as solver data.
    result = {}
    for line in text.splitlines():
        if line.startswith(('N=', 'P_actual=', 'Q_requested=', 'loop_seconds=')):
            for item in line.split():
                key, value = item.split('=', 1)
                require(key not in result, f'duplicate summary key {key}')
                result[key] = float(value)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, default=Path('results/performance/baseline/protocol.json'))
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    protocol = json.loads(a.protocol.read_text())
    require(protocol['warmups'] == 1, 'one full-field warmup is supported')
    cache = (a.build / 'CMakeCache.txt').read_text()
    require('CMAKE_BUILD_TYPE:STRING=Release\n' in cache, 'performance sampling requires Release')
    compile_commands = json.loads((a.build / 'compile_commands.json').read_text())
    require(all('-O3' in c['command'] and '-DNDEBUG' in c['command'] and
                not any(flag in c['command'] for flag in ('-ffast-math', '-march=', '-flto'))
                for c in compile_commands), 'build flags differ from frozen protocol')
    source_status = subprocess.check_output(['git', 'status', '--porcelain', '--', 'src',
        'CMakeLists.txt', 'scripts', 'tests', str(a.protocol)], text=True)
    require(not source_status, 'commit source/scripts/protocol before sampling so revision is exact')
    require(set(protocol['cpus']) <= os.sched_getaffinity(0), 'CPU list unavailable')
    require(not a.output.exists(), 'use a new output directory; evidence is never overwritten')
    a.output.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('OMP_', 'GOMP_', 'KMP_', 'OMPI_', 'PMI_', 'PMIX_'))}
    env.update(protocol['env'], OMP_PLACES=','.join('{%d}' % cpu for cpu in protocol['cpus']),
               LC_ALL='C')
    executables = {k: str((a.build / ('heat_' + k)).resolve()) for k in ('serial', 'mpi', 'openmp')}
    sources = [Path('CMakeLists.txt'), a.protocol]
    for directory in ('src', 'scripts', 'tests'):
        sources += sorted(p for p in Path(directory).glob('*') if p.is_file())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    metadata = dict(protocol=protocol, protocol_sha256=sha(a.protocol), revision=revision,
                    started_utc=datetime.now(timezone.utc).isoformat(),
                    git_status=subprocess.check_output(['git', 'status', '--short'], text=True),
                    source_sha256={str(p): sha(p) for p in sources},
                    binary_sha256={k: sha(v) for k, v in executables.items()},
                    tuning_env={k: v for k, v in env.items() if k.startswith(('OMP_', 'GOMP_', 'KMP_', 'OMPI_'))},
                    python=os.sys.version,
                    compile_commands=compile_commands)
    (a.output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    probes = [['uname', '-a'], ['lscpu'], ['lscpu', '-e=CPU,CORE,SOCKET,NODE'],
              ['free', '-h'], ['c++', '--version'], ['cmake', '--version'],
              ['mpiexec', '--version'], ['mpiexec', '--display-allocation', '-n', '1', 'true'],
              ['ompi_info', '--parsable'],
              ['dpkg-query', '-W', 'libgomp1'], ['ldd', executables['openmp']],
              ['ldd', executables['mpi']], ['taskset', '-pc', str(os.getpid())]]
    with (a.output / 'environment.log').open('w') as log:
        for command in probes:
            code, out, err, _ = run(command, env, 20)
            log.write('$ ' + ' '.join(command) + '\n' + out + err + f'\nexit={code}\n')
        for path in ('/proc/self/cgroup', '/proc/self/limits', '/proc/meminfo', '/proc/loadavg',
                     '/sys/fs/cgroup/init.scope/cpu.max', '/sys/fs/cgroup/init.scope/memory.max'):
            log.write('\n' + path + '\n' + (Path(path).read_text() if Path(path).exists() else 'absent\n'))
    configs = configurations(protocol)
    (a.output / 'matrix.json').write_text(json.dumps(configs, indent=2) + '\n')
    references, reference_errors = {}, {}
    with (a.output / 'samples.jsonl').open('w', buffering=1) as log:
        def invoke(config, repetition):
            kind, p, n, m = (config[k] for k in ('kind', 'p', 'N', 'M'))
            command = [executables[kind]]
            if kind == 'mpi':
                command = ['mpiexec', '-n', str(p), *protocol['mpi_flags'], *command]
            elif kind == 'openmp':
                command += ['--threads', str(p)]
            else:
                command = ['taskset', '-c', str(protocol['cpus'][0]), *command]
            command += ['--N', str(n), '--M', str(m), '--T', str(config['T']),
                        '--alpha', str(config['alpha'])]
            if repetition:
                command += ['--summary-only']
            started = datetime.now(timezone.utc).isoformat()
            local_env = dict(env, OMP_DISPLAY_AFFINITY='TRUE' if kind == 'openmp' and repetition == 0 else 'FALSE')
            code, out, err, wall = run(command, local_env, protocol['timeout_seconds'])
            row = dict(config=config, repetition=repetition, warmup=repetition == 0,
                       revision=revision, started_utc=started, command=command, returncode=code,
                       OMP_DISPLAY_AFFINITY=local_env['OMP_DISPLAY_AFFINITY'],
                       wall_seconds=wall, stderr=err, stdout_sha256=hashlib.sha256(out.encode()).hexdigest())
            # Save even failed attempts before rejecting them. No silent retry/outlier removal.
            log.write(json.dumps(row) + '\n')
            require(code == 0, (command, code, err))
            data = parse_summary(err)
            for key in ('N', 'M', 'T', 'alpha'):
                require(data[key] == config[key], (key, data, config))
            actual = int(data.get('P_actual', data.get('Q_actual', 1)))
            require(actual == p and int(data.get('Q_requested', p)) == p, data)
            require(math.isfinite(data['loop_seconds']) and data['loop_seconds'] > 0, data)
            require(0 < data['r'] <= .25 and math.isfinite(data['E_inf']) and data['E_inf'] <= 2e-5, data)
            if repetition:
                require(out == '', 'summary output should be empty')
                require(abs(data['E_inf'] - reference_errors[config['id']]) < 1e-14, 'sample error differs from full-field warmup')
            else:
                rows = list(csv.DictReader(io.StringIO(out)))
                require(len(rows) == (n + 1)**2, 'wrong field size')
                field, max_mode, max_exact = [], 0.0, 0.0
                gain = 1 - 8 * data['r'] * math.sin(math.pi / (2*n))**2
                for k, value in enumerate(rows):
                    i, j = divmod(k, n + 1)
                    require(int(value['i']) == i and int(value['j']) == j, 'field ordering')
                    x = float(value['u_numeric'])
                    require(math.isfinite(x), 'nonfinite field')
                    boundary = i in (0, n) or j in (0, n)
                    initial = 0 if boundary else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
                    require(not boundary or x == 0, 'nonzero boundary')
                    max_mode = max(max_mode, abs(x - gain**m * initial))
                    max_exact = max(max_exact, abs(x - math.exp(-2*config['alpha']*math.pi**2*config['T'])*initial))
                    field.append(x)
                require(max_mode < 2e-11 and abs(max_exact-data['E_inf']) < 1e-14, (max_mode, max_exact, data))
                if kind == 'serial':
                    references[n, m] = field
                require((n, m) in references, 'serial warmup must precede parallel')
                diff = max(abs(x-y) for x, y in zip(field, references[n, m]))
                require(diff <= 1e-12, diff)
                reference_errors[config['id']] = max_exact
                log.write(json.dumps(dict(validation=config['id'], D_inf=diff,
                                          discrete_mode_diff=max_mode, E_inf=max_exact)) + '\n')
            print(f"id={config['id']} {config['suite']} {kind} p={p} N={n} M={m} rep={repetition} loop={data['loop_seconds']:.9g}", flush=True)
        for config in configs:
            invoke(config, 0)
        rng = random.Random(protocol['seed'])
        for repetition in range(1, protocol['repetitions'] + 1):
            ordered = configs.copy()
            rng.shuffle(ordered)
            for config in ordered:
                invoke(config, repetition)
    require(all(sha(p) == digest for p, digest in metadata['source_sha256'].items()), 'source changed during run')
    require(all(sha(executables[k]) == digest for k, digest in metadata['binary_sha256'].items()), 'binary changed during run')
    (a.output / 'complete.json').write_text(json.dumps(dict(finished_utc=datetime.now(timezone.utc).isoformat(),
        configurations=len(configs), measured_samples=len(configs)*protocol['repetitions'],
        source_and_binary_hashes_unchanged=True), indent=2) + '\n')


if __name__ == '__main__':
    main()
