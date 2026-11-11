"""Frozen M4 large-grid experiment, original solvers only; new run IDs only."""
import argparse
from array import array
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import signal
import subprocess
import tempfile
import time

from benchmark import parse_summary, require

SEED = 20261110
REPEATS = 10
GRIDS = (384, 512, 768, 1024)
TEAMS = (1, 2, 4, 8, 16)
CPU_ORDER = tuple(range(0, 28, 2)) + (1, 3)
HEADER = ['i', 'j', 'x', 'y', 'u_numeric', 'u_exact', 'abs_error']


def configurations():
    result = []
    for n in GRIDS:
        for kind in ('serial', 'mpi', 'openmp'):
            for p in ((1,) if kind == 'serial' else TEAMS):
                result.append(dict(id=len(result), kind=kind, p=p, N=n, M=n*n//16,
                                   T=.01, alpha=1., cpus=sorted(CPU_ORDER[:p])))
    return result


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def environment():
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('OMP_', 'GOMP_', 'KMP_', 'OMPI_', 'PMI_', 'PMIX_'))}
    env.update(LC_ALL='C', OMP_DYNAMIC='FALSE', OMP_THREAD_LIMIT='16',
               OMP_PROC_BIND='close', OMP_WAIT_POLICY='ACTIVE')
    return env


def command_for(build, c, warm):
    executable = str((Path(build)/('heat_'+c['kind'])).resolve())
    if c['kind'] == 'mpi':
        # A singleton cpu-list makes Open MPI 4.1.6 report "not bound" even
        # when actual affinity is CPU 0. Two candidates give an explicit rank-0
        # binding report; there is still only one rank and it only uses CPU 0.
        candidates = c['cpus'] if c['p'] > 1 else [0, 2]
        cmd = ['mpiexec', '--use-hwthread-cpus', '--map-by', 'slot', '--bind-to',
               'cpu-list:ordered', '--cpu-list', ','.join(map(str, candidates)),
               '--report-bindings', '-n', str(c['p']), executable]
    elif c['kind'] == 'openmp':
        cmd = [executable, '--threads', str(c['p'])]
    else:
        cmd = ['taskset', '-c', str(c['cpus'][0]), executable]
    cmd += ['--N', str(c['N']), '--M', str(c['M']), '--T', str(c['T']),
            '--alpha', str(c['alpha'])]
    if not warm:
        cmd.append('--summary-only')
    env = environment()
    env.update(OMP_PLACES=','.join('{%d}' % x for x in c['cpus']),
               OMP_DISPLAY_AFFINITY='TRUE' if warm and c['kind'] == 'openmp' else 'FALSE')
    return cmd, env, executable


def task_binding(pid, executable, cpus):
    """One successful /proc snapshot during original serial/OpenMP execution."""
    try:
        if Path(f'/proc/{pid}/exe').resolve() != Path(executable):
            return None
        tids = sorted(int(p.name) for p in Path(f'/proc/{pid}/task').iterdir())
        affinity = [sorted(os.sched_getaffinity(tid)) for tid in tids]
        if len(tids) == len(cpus) and sorted(affinity) == [[x] for x in cpus]:
            return dict(tids=tids, affinity=affinity, mono_ns=time.monotonic_ns())
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        pass
    return None


def process_identity(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().split(') ')[1].split()[19]
    except (FileNotFoundError, ProcessLookupError):
        return None


def terminate_job(child):
    # Open MPI ranks may have separate process groups. Collect descendants while
    # the launcher is alive; only kill matching PID/start-time identities.
    pending = [child.pid]
    owned = {}
    while pending:
        pid = pending.pop()
        if pid in owned:
            continue
        owned[pid] = process_identity(pid)
        try:
            for task in Path(f'/proc/{pid}/task').iterdir():
                try:
                    pending.extend(map(int, (task/'children').read_text().split()))
                except (FileNotFoundError, ProcessLookupError):
                    pass
        except (FileNotFoundError, ProcessLookupError):
            pass
    for pid, identity in reversed(list(owned.items())):
        if identity is not None and process_identity(pid) == identity:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    child.wait()
    return owned


def execute(command, env, directory, timeout=600, probe=None):
    """Disk-backed stdout/stderr; retain files until caller accepts validation."""
    output = tempfile.NamedTemporaryFile(prefix='m4-large-', suffix='.csv', dir=directory, delete=False)
    errors = tempfile.NamedTemporaryFile(prefix='m4-large-', suffix='.stderr', dir=directory, delete=False)
    start = time.monotonic_ns()
    stamp = utc()
    binding = None
    timed_out = False
    cleanup = {}
    try:
        child = subprocess.Popen(command, stdout=output, stderr=errors, env=env, start_new_session=True)
    except OSError as error:
        errors.write((str(error)+'\n').encode())
        output.close()
        errors.close()
        return dict(returncode=127, timed_out=False, cleanup_pids={}, stderr=str(error)+'\n',
                    stdout_path=output.name, stderr_path=errors.name, stdout_sha256=sha(output.name),
                    stdout_bytes=0, binding=None, mono_start_ns=start, mono_end_ns=time.monotonic_ns(),
                    utc_start=stamp, utc_end=utc())
    deadline = time.monotonic()+timeout
    try:
        while probe and binding is None and child.poll() is None:
            binding = task_binding(child.pid, *probe)
            if binding is None:
                child.wait(timeout=min(.01, max(0., deadline-time.monotonic())))
    except subprocess.TimeoutExpired:
        # A short polling wait expired; continue below until binding or deadline.
        while binding is None and child.poll() is None and time.monotonic() < deadline:
            binding = task_binding(child.pid, *probe)
            if binding is None:
                time.sleep(.005)
    try:
        child.wait(timeout=max(0., deadline-time.monotonic()))
    except subprocess.TimeoutExpired:
        cleanup = terminate_job(child)
        timed_out = True
    end = time.monotonic_ns()
    output.close()
    errors.close()
    err = Path(errors.name).read_text(errors='replace')
    return dict(returncode=child.returncode, timed_out=timed_out, cleanup_pids=cleanup, stderr=err,
                stdout_path=output.name, stderr_path=errors.name, stdout_sha256=sha(output.name),
                stdout_bytes=Path(output.name).stat().st_size, binding=binding,
                mono_start_ns=start, mono_end_ns=end, utc_start=stamp, utc_end=utc())


def mpi_bindings(stderr, cpus):
    ranks = {}
    for rank, bits in re.findall(r'MCW rank (\d+) bound.*: \[([B./]+)\]', stderr):
        require(int(rank) not in ranks, 'duplicate MPI binding report')
        flat = bits.replace('/', '')
        require(len(flat) == 28, 'unexpected WSL binding topology')
        ranks[int(rank)] = [i for i, x in enumerate(flat) if x == 'B']
    require(ranks == {i: [cpu] for i, cpu in enumerate(cpus)}, 'MPI binding differs from frozen CPUs')
    return ranks


def validate_summary(c, d):
    require(all(d[k] == c[k] for k in ('N', 'M', 'T', 'alpha')), 'parameter mismatch')
    require(all(math.isclose(d[k], v, rel_tol=1e-15) for k, v in
                [('h', 1/c['N']), ('dt', c['T']/c['M']),
                 ('r', c['alpha']*c['T']*c['N']**2/c['M'])]), 'derived parameter mismatch')
    require(0 < d['r'] <= .25 and math.isfinite(d['E_inf']) and d['E_inf'] >= 0, 'invalid stability/error')
    require(math.isfinite(d['loop_seconds']) and d['loop_seconds'] > 0, 'invalid loop time')
    require(d.get('P_actual', d.get('Q_actual', 1)) == c['p'] and
            d.get('Q_requested', c['p']) == c['p'], 'actual team mismatch')


def validate_field(path, c, d, reference=None):
    n, m = c['N'], c['M']
    gain = 1-8*d['r']*math.sin(math.pi/(2*n))**2
    factor = gain**m
    exact_factor = math.exp(-2*c['alpha']*math.pi**2*c['T'])
    sine = [math.sin(math.pi*i/n) for i in range(n+1)]
    values = array('d') if reference is None else None
    error = modal = difference = 0.
    count = 0
    with Path(path).open() as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == HEADER, 'invalid CSV header')
        for k, row in enumerate(reader):
            i, j = divmod(k, n+1)
            require(i <= n and (int(row['i']), int(row['j'])) == (i, j), 'field ordering')
            x, y, value, exact, reported = [float(row[key]) for key in HEADER[2:]]
            require(all(math.isfinite(v) for v in (x, y, value, exact, reported)), 'nonfinite field')
            require(abs(x-i/n) < 1e-15 and abs(y-j/n) < 1e-15, 'coordinate mismatch')
            boundary = i in (0, n) or j in (0, n)
            initial = 0. if boundary else sine[i]*sine[j]
            expected = initial*exact_factor
            require(abs(exact-expected) < 1e-14 and
                    abs(reported-abs(value-expected)) < 1e-14, 'analytic CSV mismatch')
            require(not boundary or value == exact == reported == 0, 'nonzero boundary')
            require(0 <= value <= 1, 'maximum principle')
            error = max(error, abs(value-expected))
            modal = max(modal, abs(value-initial*factor))
            if reference is None:
                values.append(value)
            else:
                require(k < len(reference), 'serial reference too short')
                difference = max(difference, abs(value-reference[k]))
            count += 1
    bound = abs(factor-exact_factor)+2e-11
    require(count == (n+1)**2, 'field size')
    require(reference is None or len(reference) == count, 'reference size')
    require(difference <= 1e-12 and modal < 2e-11, 'serial/modal difference')
    require(abs(error-d['E_inf']) < 1e-14 and error <= bound, 'analytic error/bound')
    return dict(nodes=count, D_inf=difference, E_inf=error, mode_diff=modal,
                truncation_bound=bound), values


def available_prefix(run_id):
    require(run_id.replace('-', '').isalnum(), 'invalid run ID')
    prefix = Path('docs/validation')/('m4-diagnostic-'+run_id)
    require(not list(prefix.parent.glob(prefix.name+'*')), 'run ID already exists; do not overwrite evidence')
    return prefix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    prefix = available_prefix(args.run_id)
    sources = [Path('CMakeLists.txt')]+[p for folder in ('src', 'tests', 'scripts')
                for p in sorted(Path(folder).glob('*')) if p.is_file()]
    require(not subprocess.check_output(['git', 'status', '--porcelain', '--', 'CMakeLists.txt',
                                        'src', 'tests', 'scripts']), 'commit source before sampling')
    cache = (args.build/'CMakeCache.txt').read_text()
    require('CMAKE_BUILD_TYPE:STRING=Release\n' in cache, 'Release build required')
    commands = json.loads((args.build/'compile_commands.json').read_text())
    require(all('-O3' in x['command'] and '-DNDEBUG' in x['command'] and '-std=c++17' in x['command'] and
                not any(v in x['command'] for v in ('-ffast-math', '-march=', '-flto')) for x in commands),
            'unexpected build flags')
    require(set(CPU_ORDER) <= os.sched_getaffinity(0), 'required CPUs unavailable')
    topology = {str(i): dict(core=Path(f'/sys/devices/system/cpu/cpu{i}/topology/core_id').read_text().strip(),
                            siblings=Path(f'/sys/devices/system/cpu/cpu{i}/topology/thread_siblings_list').read_text().strip())
                for i in range(28)}
    require(all(int(topology[str(i)]['core']) == i//2 for i in range(28)), 'WSL topology changed')
    binaries = {kind: str((args.build/('heat_'+kind)).resolve()) for kind in ('serial', 'mpi', 'openmp')}
    manifest = dict(schema='m4-large-v1', revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    complete=False, started_utc=utc(), seed=SEED, repeats=REPEATS, warmups=1, timeout_seconds=600,
                    matrix=configurations(), cpu_order=CPU_ORDER, topology=topology, environment=environment(),
                    source_sha256={str(p): sha(p) for p in sources}, binary_sha256={k: sha(v) for k, v in binaries.items()},
                    compile_commands=commands, bootstrap=dict(draws=10000, seed=SEED, statistic='ratio of medians; common round indices',
                                                             percentile_indices=[249, 9749]),
                    git_status=subprocess.check_output(['git', 'status', '--short'], text=True),
                    timing='Original loop_seconds; MPI halo/max-rank; OpenMP team entry/exit and synchronization; initialization/gather/validation/output excluded')
    # Store only tuning settings, not arbitrary inherited credentials or personal environment.
    manifest['environment'] = {k: v for k, v in environment().items() if k.startswith('OMP_') or k == 'LC_ALL'}
    Path(str(prefix)+'.json').write_text(json.dumps(manifest, indent=2)+'\n')
    with Path(str(prefix)+'.log').open('w') as log:
        for cmd in [['uname', '-a'], ['lscpu'], ['lscpu', '-e=CPU,CORE,SOCKET,NODE'], ['free', '-h'],
                    ['c++', '--version'], ['cmake', '--version'], ['mpiexec', '--version'],
                    ['ompi_info', '--parsable'], ['dpkg-query', '-W', 'libgomp1']]+[['ldd', x] for x in binaries.values()]:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            log.write('$ '+repr(cmd)+'\n'+r.stdout+r.stderr+f'\nexit={r.returncode}\n')
            require(r.returncode == 0, 'environment probe failed')
        for name in ('/proc/self/cgroup', '/proc/self/limits', '/proc/meminfo', '/proc/loadavg',
                     '/sys/fs/cgroup/init.scope/cpu.max', '/sys/fs/cgroup/init.scope/memory.max'):
            log.write('\n'+name+'\n'+(Path(name).read_text() if Path(name).exists() else 'absent\n'))
    references, warmed, samples = {}, {}, []
    with Path(str(prefix)+'.jsonl').open('w', buffering=1) as log:
        def invoke(c, rep):
            warm = rep == 0
            cmd, env, executable = command_for(args.build, c, warm)
            row = dict(type='attempt', id=len(samples), config=c, repetition=rep, warmup=warm,
                       revision=manifest['revision'], command=cmd,
                       tuning={k: v for k, v in env.items() if k.startswith('OMP_') or k == 'LC_ALL'},
                       **execute(cmd, env, args.build, probe=(executable, c['cpus']) if c['kind'] != 'mpi' else None))
            log.write(json.dumps(row)+'\n')
            require(row['returncode'] == 0 and not row['timed_out'], 'failed invocation; outputs retained')
            d = parse_summary(row['stderr'])
            validate_summary(c, d)
            if c['kind'] == 'mpi':
                row['mpi_bindings'] = mpi_bindings(row['stderr'], c['cpus'])
            else:
                require(row['binding'] is not None, 'missing actual task affinity snapshot')
                if warm and c['kind'] == 'openmp' and c['p'] > 1:
                    affinity = [int(v) for v in re.findall(r'affinity (\d+)\s*$', row['stderr'], re.M)]
                    require(sorted(affinity) == c['cpus'], 'OpenMP runtime affinity mismatch')
            row['summary'] = d
            if warm:
                validation, reference = validate_field(row['stdout_path'], c, d, references.get(c['N']))
                if c['kind'] == 'serial':
                    references[c['N']] = reference
                row['validation'] = validation
                warmed[c['id']] = d['E_inf']
            else:
                require(row['stdout_bytes'] == 0, 'summary stdout not empty')
                require(abs(d['E_inf']-warmed[c['id']]) < 1e-14, 'sample/warmup error mismatch')
            row['type'] = 'sample'
            log.write(json.dumps(row)+'\n')
            samples.append(row)
            Path(row['stdout_path']).unlink()
            Path(row['stderr_path']).unlink()
            print(f"rep={rep:2} {c['kind']:6} p={c['p']:2} N={c['N']:4} M={c['M']:5} t={d['loop_seconds']:.9f}", flush=True)
        for c in manifest['matrix']:
            invoke(c, 0)
        rng = random.Random(SEED)
        for rep in range(1, REPEATS+1):
            ordered = list(manifest['matrix'])
            rng.shuffle(ordered)
            for c in ordered:
                invoke(c, rep)
    require(all(sha(p) == v for p, v in manifest['source_sha256'].items()), 'source changed during sampling')
    require(all(sha(binaries[k]) == v for k, v in manifest['binary_sha256'].items()), 'binary changed during sampling')
    manifest.update(complete=True, finished_utc=utc(), invocations=len(samples), measured=440, warmup_invocations=44,
                    source_and_binary_unchanged=True)
    Path(str(prefix)+'.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('COMPLETE', len(samples), 'invocations; 440 measured', flush=True)


if __name__ == '__main__':
    main()
