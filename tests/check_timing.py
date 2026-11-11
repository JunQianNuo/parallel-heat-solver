"""Check timing summaries against full fields, errors and real teams (no speed threshold)."""
import argparse
import math
import os
import re
import signal
import subprocess


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def summary(text):
    return dict(re.findall(r'\b([A-Za-z_]+)=([^\s]+)', text))


def run(command, *, env, timeout, capture_output=False, text=True,
        stdout=None, stderr=None):
    if capture_output:
        stdout = stderr = subprocess.PIPE
    process = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr,
                               text=text, start_new_session=True)
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    return subprocess.CompletedProcess(command, process.returncode, out, err)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('serial', 'mpi', 'openmp', 'mpiexec'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--max-procs', type=int, required=True)
    p.add_argument('--max-threads', type=int, required=True)
    p.add_argument('--pre', action='append', default=[])
    p.add_argument('--post', action='append', default=[])
    p.add_argument('--npflag', default='-n')
    a = p.parse_args()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('OMP_', 'GOMP_'))}
    env.update(OMP_THREAD_LIMIT=str(a.max_threads), OMP_PROC_BIND='FALSE')
    configs = [('serial', [a.serial], 1)]
    configs += [('mpi', [a.mpiexec, a.npflag, str(n), *a.pre, a.mpi, *a.post], n)
                for n in range(1, a.max_procs + 1)]
    configs += [('openmp', [a.openmp, '--threads', str(n)], n)
                for n in range(1, a.max_threads + 1)]
    for kind, command, n in configs:
        for m in (7, 8):
            args = ['--N', '7', '--M', str(m), '--T', '.01', '--alpha', '.3']
            results = [run(command + args + extra, env=env, capture_output=True,
                                      text=True, timeout=20)
                       for extra in ([], ['--summary-only'])]
            for result in results:
                require(result.returncode == 0, result.stderr)
                data = summary(result.stderr)
                require(math.isfinite(float(data['loop_seconds'])) and
                        float(data['loop_seconds']) > 0, data)
                if kind == 'mpi':
                    require(int(data['P_actual']) == n, data)
                if kind == 'openmp':
                    require(int(data['Q_actual']) == int(data['Q_requested']) == n, data)
            require(results[0].stdout.startswith('i,j,'), 'missing field')
            require(results[1].stdout == '', 'summary-only emitted field')
            full, brief = map(lambda r: summary(r.stderr), results)
            full.pop('loop_seconds'); brief.pop('loop_seconds')
            require(full == brief, (full, brief))
        bad = run(command + ['--summary-only', '--summary-only'], env=env,
                             capture_output=True, text=True, timeout=20)
        require(bad.returncode == 2 and not bad.stdout, bad.stderr)
        print(f'TIMING kind={kind} requested={n} actual={n} odd/even summary matches full E_inf')
    if os.path.exists('/dev/full'):
        for kind, command, n in configs:
            # Rank-local redirect: launcher output buffering can hide /dev/full.
            wrapped = (command[:command.index(a.mpi)] +
                       ['sh', '-c', 'exec "$@" 2>/dev/full', 'sh'] +
                       command[command.index(a.mpi):]) if kind == 'mpi' else command
            if kind == 'mpi':
                r = run(wrapped + ['--summary-only'], env=env,
                                   capture_output=True, text=True, timeout=20)
            else:
                with open('/dev/full', 'w') as sink:
                    r = run(wrapped + ['--summary-only'], env=env, stdout=subprocess.PIPE,
                                       stderr=sink, text=True, timeout=20)
            require(r.returncode == 1, f'{kind} summary stderr failure: {r.returncode}')
        print('TIMING summary stderr output failures checked')


if __name__ == '__main__':
    main()
