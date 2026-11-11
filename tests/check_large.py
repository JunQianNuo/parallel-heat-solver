"""Large-grid harness checks: synthetic statistics plus real original-solver P/Q=8,16."""
import argparse
from array import array
import copy
import csv
import io
import json
import math
import os
from pathlib import Path
import random
import re
import signal
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from benchmark import parse_summary
from benchmark_large import (configurations, command_for, execute, environment, validate_field,
                             validate_summary, mpi_bindings, SEED)
from analyze_large import summarize, speedup_interval, analyze


def reject(fn):
    try:
        fn()
    except (RuntimeError, ValueError, KeyError, IndexError):
        return
    raise AssertionError('damaged input accepted')


def synthetic():
    """Never use these artificial times as project performance evidence."""
    matrix = configurations()
    manifest = dict(schema='m4-large-v1', complete=True, matrix=matrix, revision='synthetic-test-only',
                    seed=SEED, repeats=10, warmups=1, invocations=484, measured=440, warmup_invocations=44,
                    source_and_binary_unchanged=True)
    records = []
    def add(c, rep):
        index = len(records)//2
        value = (10+rep)*(.5 if c['kind'] == 'mpi' else 1.)
        d = dict(N=c['N'], M=c['M'], T=c['T'], alpha=c['alpha'], h=1/c['N'], dt=c['T']/c['M'],
                 r=c['T']*c['N']**2/c['M'], E_inf=0., loop_seconds=value)
        if c['kind'] == 'mpi':
            d['P_actual'] = c['p']
        if c['kind'] == 'openmp':
            d.update(Q_requested=c['p'], Q_actual=c['p'])
        stderr = ' '.join(f'{k}={v}' for k, v in d.items())+'\n'
        # All summary items form one valid N= line, followed by real-format binding text.
        bindings = {}
        if c['kind'] == 'mpi':
            for rank, cpu in enumerate(c['cpus']):
                bits = ''.join('B' if i == cpu else '.' for i in range(28))
                bits = '/'.join(bits[i:i+2] for i in range(0, 28, 2))
                stderr += f'MCW rank {rank} bound to socket: [{bits}]\n'
                bindings[rank] = [cpu]
        tuning = {k: v for k, v in command_for(Path('/synthetic'), c, rep == 0)[1].items()
                  if k.startswith('OMP_') or k == 'LC_ALL'}
        a = dict(type='attempt', id=index, config=c, repetition=rep, warmup=rep == 0,
                 revision=manifest['revision'], returncode=0, timed_out=False, stderr=stderr,
                 mono_start_ns=index*10, mono_end_ns=index*10+5, stdout_bytes=1 if rep == 0 else 0,
                 tuning=tuning, binding=None if c['kind'] == 'mpi' else
                 dict(tids=list(range(c['p'])), affinity=[[x] for x in c['cpus']], mono_ns=index*10+2))
        b = dict(a, type='sample', summary=d)
        if c['kind'] == 'mpi':
            b['mpi_bindings'] = bindings
        if rep == 0:
            gain = 1-8*d['r']*math.sin(math.pi/(2*c['N']))**2
            bound = abs(gain**c['M']-math.exp(-2*c['alpha']*math.pi**2*c['T']))+2e-11
            b['validation'] = dict(nodes=(c['N']+1)**2, D_inf=0., mode_diff=0., E_inf=0., truncation_bound=bound)
        records.extend((a, b))
    for c in matrix:
        add(c, 0)
    rng = random.Random(SEED)
    for rep in range(1, 11):
        order = list(matrix)
        rng.shuffle(order)
        for c in order:
            add(c, rep)
    return manifest, records


def unit_checks(directory):
    m, records = synthetic()
    rows, _ = summarize(m, records)
    assert len(rows) == 44 and all(r['speedup_serial'] == 2. for r in rows if r['kind'] == 'mpi')
    assert all((r['speedup_low'], r['speedup_high']) == (2., 2.) for r in rows if r['kind'] == 'mpi')
    assert speedup_interval([2.]*10, [1.]*10) == (2., 2.)
    reject(lambda: speedup_interval([1.]*9, [1.]*10))
    for v in (0., -1., math.inf, math.nan):
        reject(lambda v=v: speedup_interval([v]*10, [1.]*10))
    for mutate in (
        lambda x: x.pop(),
        lambda x: x.__setitem__(45, copy.deepcopy(x[43])),
        lambda x: x[89].__setitem__('revision', 'wrong'),
        lambda x: x[89]['summary'].__setitem__('loop_seconds', -1.),
        lambda x: x[1]['validation'].__setitem__('D_inf', .1),
        lambda x: x[45].__setitem__('mono_start_ns', -1),
        lambda x: x[1]['binding'].__setitem__('affinity', [[99]]),
    ):
        damaged = copy.deepcopy(records)
        mutate(damaged)
        reject(lambda: summarize(m, damaged))
    prefix = directory/'synthetic-test-only'
    Path(str(prefix)+'.json').write_text(json.dumps(m))
    Path(str(prefix)+'.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    assert len(analyze(prefix, make_plots=False)) == 44
    assert len(list(csv.DictReader(Path(str(prefix)+'-rounds.csv').open()))) == 440
    changed = copy.deepcopy(records)
    for row in changed:
        if row['config']['id'] in (0, 1) and row['repetition']:
            value = ((1., 100.) if row['config']['id'] == 0 else (1., 10.))[(row['repetition']-1) % 2]
            row['stderr'] = re.sub(r'loop_seconds=[^\s]+', f'loop_seconds={value}', row['stderr'])
            if row['type'] == 'sample':
                row['summary']['loop_seconds'] = value
    changed_rows, _ = summarize(m, changed)
    assert changed_rows[1]['speedup_serial'] == 50.5/5.5  # median of per-round ratios would be 5.5
    print('PASS synthetic-only: medians, paired-round bootstrap, 44/440 CSV, damaged journals/fields/bindings rejected')


def alive(pid):
    path = Path(f'/proc/{pid}/stat')
    return path.exists() and path.read_text().split(') ')[1].split()[0] != 'Z'


def timeout_check(directory, command, env, pidfiles):
    result = execute(command, env, directory, timeout=3)
    assert result['timed_out'] and result['returncode'] != 0
    pids = [int(p.read_text()) for p in pidfiles if p.exists()]
    try:
        assert len(pids) == len(pidfiles), 'timeout fixture did not start all children'
        assert not any(alive(pid) for pid in pids), 'timeout left child processes running'
    finally:
        for pid in pids:
            if alive(pid):
                os.kill(pid, signal.SIGKILL)
    print('PASS timeout cleanup:', len(pids), 'child/rank processes; raw files retained in temporary test directory')


def runtime_checks(build, directory):
    failed = execute([str(directory/'missing-executable')], environment(), directory)
    assert failed['returncode'] == 127 and Path(failed['stderr_path']).read_text() == failed['stderr']
    references = {}
    def field(kind, p, n, steps, limited=None, snapshot=False):
        c = dict(kind=kind, p=p, N=n, M=steps, T=.001, alpha=1.,
                 cpus=sorted((list(range(0, 28, 2))+[1, 3])[:p]))
        cmd, env, executable = command_for(build, c, True)
        if limited:
            env['OMP_THREAD_LIMIT'] = str(limited)
        r = execute(cmd, env, directory, timeout=30, probe=(executable, c['cpus']) if snapshot else None)
        assert r['returncode'] == 0 and not r['timed_out'], r
        if snapshot:
            assert r['binding'] is not None, 'live affinity snapshot failed'
        d = parse_summary(r['stderr'])
        if limited:
            assert d['Q_requested'] == p and d['Q_actual'] == limited
            reject(lambda: validate_summary(c, d))
        else:
            validate_summary(c, d)
        if kind == 'mpi':
            mpi_bindings(r['stderr'], c['cpus'])
        key = n, steps
        reference = references.get(key) if kind != 'serial' else None
        if kind != 'serial' and reference is None:
            field('serial', 1, n, steps)
            reference = references[key]
        validation, values = validate_field(r['stdout_path'], c, d, reference)
        if kind == 'serial':
            references[key] = values
        print('RESULT', json.dumps(dict(kind=kind, requested=p, actual=d.get('P_actual', d.get('Q_actual', 1)),
                                        N=n, M=steps, **validation)))
        # Mutations exercise the streaming validator against a real solver field.
        if kind == 'serial' and n == 2:
            original = Path(r['stdout_path']).read_text()
            for broken in (original.replace('u_numeric', 'wrong', 1), original.rsplit('\n', 2)[0]+'\n',
                           original.replace('0,0,0,0,0,0,0', '0,0,0,0,0.1,0,0', 1)):
                bad = directory/'damaged.csv'
                bad.write_text(broken)
                reject(lambda: validate_field(bad, c, d))
            assert isinstance(values, array)
        return c, r
    # Include all launch configurations: Open MPI singleton reporting differs
    # from its multi-rank behavior, even though actual affinity can be correct.
    for p in (1, 2, 4, 8, 16):
        for n in (p+1, p+2):
            for steps in (65, 66):
                for kind in ('mpi', 'openmp'):
                    field(kind, p, n, steps)
        field('openmp', p, 2, 65)
    field('openmp', 16, 18, 65, limited=8)
    for kind, p in [('serial', 1), ('openmp', 1), ('openmp', 8), ('openmp', 16)]:
        field(kind, p, 128, 8192, snapshot=True)
    for kind, p, n in [('mpi', 16, 16), ('openmp', 0, 18), ('serial', 1, 18)]:
        c = dict(kind=kind, p=max(p, 1), N=n, M=1, T=1., alpha=1., cpus=[0])
        if kind == 'mpi':
            c.update(M=65, T=.001, p=16, cpus=sorted(list(range(0, 28, 2))+[1, 3]))
        cmd, env, _ = command_for(build, c, False)
        if kind == 'openmp':
            cmd[cmd.index('--threads')+1] = '0'
        r = execute(cmd, env, directory, timeout=30)
        assert r['returncode'] == 2 and not r['timed_out'] and r['stdout_bytes'] == 0, r
    childfile = directory/'child.pid'
    source = 'import subprocess,time; from pathlib import Path; p=subprocess.Popen(["sleep","60"]); Path('+repr(str(childfile))+').write_text(str(p.pid)); time.sleep(60)'
    timeout_check(directory, [sys.executable, '-c', source], environment(), [childfile])
    c = dict(kind='mpi', p=2, N=3, M=65, T=.001, alpha=1., cpus=[0, 2])
    cmd, env, executable = command_for(build, c, False)
    pidfiles = [directory/f'rank{i}.pid' for i in range(2)]
    source = ('import os,time; from pathlib import Path; '
              'Path('+repr(str(directory))+'+"/rank"+os.environ["OMPI_COMM_WORLD_RANK"]+".pid").write_text(str(os.getpid())); time.sleep(60)')
    timeout_check(directory, cmd[:cmd.index(executable)]+[sys.executable, '-c', source], env, pidfiles)
    print('PASS original-solver extended resources, parity, MPI ownership boundaries, idle OpenMP workers, limited team and invalid inputs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='m4-large-check-', dir=args.build) as tmp:
        directory = Path(tmp)
        unit_checks(directory)
        runtime_checks(args.build, directory)
