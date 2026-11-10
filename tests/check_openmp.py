"""Real OpenMP teams and full-field comparisons against independent serial."""
import argparse
import csv
import io
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--serial', required=True)
parser.add_argument('--solver', required=True)
parser.add_argument('--threads', type=int, required=True)
parser.add_argument('--limit', type=int)
a = parser.parse_args()
q = a.threads
expected_q = a.limit or q
# Isolate tests from inherited OpenMP tuning. Explicit requests override NUM_THREADS;
# production disables dynamic adjustment even though tests enable it in the env.
env = dict(os.environ)
for key in list(env):
    if key.startswith(('OMP_', 'GOMP_')):
        del env[key]
env.update(OMP_NUM_THREADS='3', OMP_DYNAMIC='TRUE',
           OMP_THREAD_LIMIT=str(expected_q), OMP_PROC_BIND='FALSE')

def run(command, **kwargs):
    return subprocess.run(command, capture_output=True, text=True,
                          timeout=10, env=env, **kwargs)

def check(n, m, t, alpha=1):
    args = ['--threads', str(q), '--N', str(n), '--M', str(m), '--T', str(t), '--alpha', str(alpha)]
    result = run([a.solver, *args])
    code, out, err = result.returncode, result.stdout, result.stderr
    assert code == 0, (code, err)
    serial = run([a.serial, *args[2:]])
    serial_code, serial_out, serial_err = serial.returncode, serial.stdout, serial.stderr
    assert serial_code == 0, serial_err
    reader = csv.DictReader(io.StringIO(out))
    assert reader.fieldnames == ['i', 'j', 'x', 'y', 'u_numeric', 'u_exact', 'abs_error']
    rows = list(reader)
    reference = list(csv.DictReader(io.StringIO(serial_out)))
    assert len(rows) == len(reference) == (n+1)**2
    summary = dict(item.split('=') for item in err.split())
    assert int(summary['Q_requested']) == q
    assert int(summary['Q_actual']) == expected_q, ('team resource mismatch', summary)
    assert int(summary['N']) == n and int(summary['M']) == m
    for key, expected in [('T', t), ('alpha', alpha), ('h', 1/n),
                          ('dt', t/m), ('r', alpha*t*n*n/m)]:
        assert math.isclose(float(summary[key]), expected, rel_tol=1e-15)
    difference = error = 0
    gain = 1 - 8*(alpha*t*n*n/m)*math.sin(math.pi/(2*n))**2
    for k, (row, ref) in enumerate(zip(rows, reference)):
        i, j = divmod(k, n+1)
        assert (int(row['i']), int(row['j'])) == (i, j)
        data = [float(row[key]) for key in reader.fieldnames[2:]]
        assert all(math.isfinite(v) for v in data)
        x, y, value, exact, reported_error = data
        assert abs(x-i/n) < 1e-15 and abs(y-j/n) < 1e-15
        boundary = i in (0, n) or j in (0, n)
        initial = 0 if boundary else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
        expected = math.exp(-2*alpha*math.pi**2*t)*initial
        assert abs(value-initial*gain**m) < 1e-13
        assert abs(exact-expected) < 1e-14
        assert abs(reported_error-abs(value-expected)) < 1e-14
        if boundary:
            assert value == exact == 0
        difference = max(difference, abs(value-float(ref['u_numeric'])))
        error = max(error, abs(value-expected))
    assert difference <= 1e-13
    assert abs(float(summary['E_inf'])-error) < 1e-14
    if n == 20 and m == 400 and t == .1:
        assert error < 2e-4
    print(f'Q_requested={q} Q_actual={summary["Q_actual"]} N={n} M={m} T={t} alpha={alpha} D_inf={difference:.17g} E_inf={error:.17g}')


check(20, 400, .1)
# One internal row: Q>rows is legal and idle threads still synchronize.
for m in (1, 2, 3, 9, 10):
    check(2, m, m/32)
check(2, 1, .0625)  # stability endpoint, hand-computable zero center
# Q+1 internal rows are indivisible by Q>1, plus a distinct odd grid.
for n in (expected_q+2, 7):
    for m in (7, 8):
        check(n, m, .01, .3)

bad = [['--threads'], ['--threads', '2', '--threads', '3'],
       ['--threads', '0'], ['--threads', '-1'], ['--threads', '+2'],
       ['--threads', '2.0'], ['--threads', '2x'], ['--threads', ' 2'],
       ['--threads', '2147483648'], ['--threads', '99999999999999999999999'],
       ['--threads', 'nan'], ['--threads', 'inf'],
       ['--help', '--threads', '2'], ['--threads=2']]
for args in bad:
    result = run([a.solver, *args])
    assert result.returncode == 2 and not result.stdout and result.stderr.startswith('input error:'), (args, result)
help_result = run([a.solver, '--help'])
assert help_result.returncode == 0 and '--threads' in help_result.stdout
if Path('/dev/full').exists():
    for args in (['--help'], ['--threads', str(q), '--N', '2', '--M', '1', '--T', '.03125']):
        with open('/dev/full', 'w') as sink:
            result = subprocess.run([a.solver, *args], stdout=sink,
                                    stderr=subprocess.PIPE, text=True, timeout=10, env=env)
        assert result.returncode == 1, result
    with open('/dev/full', 'w') as sink:
        result = subprocess.run([a.solver, '--threads', str(q)], stdout=subprocess.DEVNULL,
                                stderr=sink, timeout=10, env=env)
    assert result.returncode == 1
    print('stdout/stderr and help output failures: exit=1')
else:
    print('/dev/full unavailable: output failure checks not run')

if q == 1 and a.limit is None:
    # Reuse the entire established numeric CLI contract and 30 invalid cases.
    # Run in this controlled environment, also proving the default ignores NUM_THREADS=3.
    os.environ.clear()
    os.environ.update(env)
    saved_argv = sys.argv
    sys.argv = [str(Path(__file__).with_name('check_cli.py')), a.solver]
    try:
        runpy.run_path(sys.argv[0], run_name='__main__')
    finally:
        sys.argv = saved_argv
    default = run([a.solver])
    summary = dict(item.split('=') for item in default.stderr.split())
    assert summary['Q_requested'] == summary['Q_actual'] == '1'
    print('default Q_requested=1 Q_actual=1 with OMP_NUM_THREADS=3')
    if sys.platform.startswith('linux'):
        import resource
        def restrict_address_space():
            # Limits only this child. First 800 MB grid cannot fit in 256 MiB.
            resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
        failed = run([a.solver, '--N', '10000', '--M', '100000000'],
                     preexec_fn=restrict_address_space)
        assert failed.returncode == 1 and not failed.stdout and 'runtime error:' in failed.stderr, failed
        print('RLIMIT_AS=256MiB allocation failure before parallel region: exit=1; ' + failed.stderr.strip())
    else:
        print('allocation failure check not run: requires Linux RLIMIT_AS')
print(f'OpenMP PASS Q_requested={q} Q_actual={expected_q}; {len(bad)} invalid thread inputs rejected')
