"""Real MPI/serial full-field regression, with bounded launcher lifetimes."""
import argparse
import csv
import io
import math
import os
import signal
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
for name in ('serial', 'solver', 'mpiexec', 'npflag'):
    parser.add_argument('--' + name, required=True)
parser.add_argument('--fault-solver')
parser.add_argument('--processes', type=int, required=True)
parser.add_argument('--pre', action='append', default=[])
parser.add_argument('--post', action='append', default=[])
a = parser.parse_args()
p = a.processes
launch = [a.mpiexec, a.npflag, str(p), *a.pre, a.solver, *a.post]


def run(command, sink=None):
    # A timeout kills the whole launcher process group, including child ranks.
    with subprocess.Popen(command, stdout=subprocess.PIPE if sink is None else sink,
                          stderr=subprocess.PIPE, text=True, start_new_session=True) as child:
        try:
            out, err = child.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            raise AssertionError(f'MPI subprocess timed out: {command}')
        return child.returncode, out, err


def check(n, m, t, alpha=1):
    args = ['--N', str(n), '--M', str(m), '--T', str(t), '--alpha', str(alpha)]
    code, out, err = run([*launch, *args])
    assert code == 0, (code, err)
    serial_code, serial_out, serial_err = run([a.serial, *args])
    assert serial_code == 0, serial_err
    reader = csv.DictReader(io.StringIO(out))
    assert reader.fieldnames == ['i', 'j', 'x', 'y', 'u_numeric', 'u_exact', 'abs_error']
    rows = list(reader)
    reference = list(csv.DictReader(io.StringIO(serial_out)))
    assert len(rows) == len(reference) == (n+1)**2
    summary = dict(item.split('=') for item in err.split())
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
    print(f'P={p} N={n} M={m} T={t} alpha={alpha} D_inf={difference:.17g} E_inf={error:.17g}')


check(20, 400, .1)
# Every rank owns exactly one row; odd and even final buffers.
for m in (1, 2, 7, 8):
    check(p+1, m, .01, .3)
# 2P+1 rows: unequal distribution for each P>1, distinct global coordinates.
for m in (7, 8):
    check(2*p+2, m, .01, .3)
if p == 1:
    check(2, 1, .0625)  # r=1/4 endpoint, sole center goes to zero.

bad = [[], ['--unknown'], ['--N'], ['--N', '2', '--N', '3'],
       ['--N', '1'], ['--M', '0'], ['--T', 'nan'], ['--alpha', 'inf'],
       ['--N', '-2'], ['--N', '2x'], ['--help', '--N', '20'],
       ['--M', '1'], ['--T', '1e-300', '--alpha', '1e-300'],
       # Valid serial-size arithmetic and stability, rejected before allocation
       # because (N-1)(N+1) exceeds INT_MAX.
       ['--N', '46341', '--M', '10000000000'],
       ['--N', '18446744073709551615']]
if p > 1:
    bad[0] = ['--N', str(p), '--M', '100', '--T', '.001']
else:
    bad.pop(0)  # P=1 cannot exceed N-1 for valid N.
for args in bad:
    code, out, err = run([*launch, *args])
    assert code == 2 and not out and 'input error:' in err, (args, code, out, err)
code, out, err = run([*launch, '--help'])
assert code == 0 and out.count('Usage:') == 1
if os.path.exists('/dev/full'):
    # Redirect inside each rank: mpiexec forwards rank output through a pipe,
    # so redirecting only the launcher's stdout does not test solver I/O.
    output_launch = [a.mpiexec, a.npflag, str(p), *a.pre, '/bin/sh', *a.post,
                     '-c', 'exec "$@" > /dev/full', 'heat-mpi-output-test', a.solver]
    code, _, err = run([*output_launch, '--N', str(p+1), '--M', '2', '--T', '.001'])
    assert code == 1 and 'output failed' in err, (code, err)
else:
    print('/dev/full unavailable: output failure not run')
print(f'P={p} PASS; {len(bad)} rejected inputs; help checked')

if a.fault_solver:
    fault_launch = [a.mpiexec, a.npflag, str(p), *a.pre, a.fault_solver, *a.post]
    for mode in ('partition', 'allocation-root', 'allocation-worker'):
        code, out, err = run([*fault_launch, mode])
        assert code == 0 and 'collective_check=1' in out, (mode, code, out, err)
        print(f'P={p} injected-test {out.strip()}')
    code, out, err = run([*fault_launch, 'communication'])
    assert code != 0 and 'MPI error in Sendrecv' in err and 'unexpected solver return' not in err, (code, out, err)
    print(f'P={p} injected Sendrecv error: MPI_Abort exit={code}; no timeout')
else:
    print('Allocation/communication injection not run: requires Linux GNU-compatible linker')
