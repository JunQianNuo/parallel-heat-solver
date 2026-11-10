"""CLI contract checks; only Python standard library is required."""
import csv
import io
import math
import subprocess
import sys

exe = sys.argv[1]

def run(args):
    return subprocess.run([exe, *args], capture_output=True, text=True, timeout=10)

def check(args, n, m, t, alpha):
    result = run(args)
    assert result.returncode == 0, result.stderr
    summary = dict(item.split('=') for item in result.stderr.split())
    assert int(summary['N']) == n and int(summary['M']) == m
    assert float(summary['T']) == t and float(summary['alpha']) == alpha
    assert math.isclose(float(summary['dt']), t/m, rel_tol=1e-15)
    r = alpha*t*n*n/m
    assert math.isclose(float(summary['r']), r, rel_tol=1e-15)
    reader = csv.DictReader(io.StringIO(result.stdout))
    assert reader.fieldnames == ['i','j','x','y','u_numeric','u_exact','abs_error']
    rows = list(reader)
    assert len(rows) == (n+1)**2
    errors = []
    gain = 1 - 8*r*math.sin(math.pi/(2*n))**2
    for k, row in enumerate(rows):
        i, j = divmod(k, n+1)
        assert (int(row['i']), int(row['j'])) == (i,j)
        values = {key: float(row[key]) for key in reader.fieldnames[2:]}
        assert all(math.isfinite(v) for v in values.values())
        assert abs(values['x']-i/n) < 1e-15 and abs(values['y']-j/n) < 1e-15
        boundary = i in (0,n) or j in (0,n)
        initial = 0 if boundary else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
        exact = math.exp(-2*alpha*math.pi**2*t)*initial
        assert abs(values['u_exact'] - exact) < 1e-14
        assert abs(values['u_numeric'] - initial*gain**m) < 1e-13
        if boundary:
            assert values['u_numeric'] == values['u_exact'] == 0
        error = abs(values['u_numeric'] - exact)
        assert abs(values['abs_error'] - error) < 1e-14
        errors.append(error)
    assert abs(float(summary['E_inf']) - max(errors)) < 1e-14
    print(f"CLI N={n} M={m} E_inf={max(errors):.17g}")

check([],20,400,.1,1)
for m in (1,2,3):
    check(['--N','2','--M',str(m),'--T',str(m/32)],2,m,m/32,1)
check(['--N','2','--M','1','--T','.0625'],2,1,.0625,1)
check(['--alpha','.3','--T','.01','--M','7','--N','7'],7,7,.01,.3)

bad = [ ['20'], ['--unknown'], ['--help','--N','2'], ['--N'],
        ['--N','2','--N','3'], ['--N','1'], ['--M','0'],
        ['--N','-2'], ['--N','2.0'], ['--N','+2'], ['--M','1x'],
        ['--N','999999999999999999999999999'],
        ['--N','18446744073709551615'], ['--N','4294967296'],
        ['--T','0'], ['--T','-1'], ['--T','nan'], ['--T','inf'],
        ['--alpha','0'], ['--alpha','-1'], ['--alpha','nan'], ['--alpha','inf'],
        ['--T','1e999'], ['--T','1e-999'], ['--T','0.1junk'], ['--T',' 0.1'],
        ['--N','2','--M','1','--T',str(math.nextafter(.0625,1))],
        ['--M','1'], ['--T','1e308','--alpha','1e308'],
        ['--T','1e-300','--alpha','1e-300'] ]
for args in bad:
    result = run(args)
    assert result.returncode == 2 and not result.stdout and result.stderr.startswith('input error:'), (args,result)
help_result = run(['--help'])
assert help_result.returncode == 0 and 'Usage:' in help_result.stdout
# Linux /dev/full checks a real output error after a successful solve.
try:
    with open('/dev/full','w') as sink:
        failed = subprocess.run([exe,'--N','2','--M','1','--T','.03125'],
                                stdout=sink,stderr=subprocess.PIPE,text=True,timeout=10)
    assert failed.returncode == 1 and 'output failed' in failed.stderr
except FileNotFoundError:
    print('/dev/full unavailable: output-error check not run')
print(f'CLI PASS; {len(bad)} invalid cases rejected')
