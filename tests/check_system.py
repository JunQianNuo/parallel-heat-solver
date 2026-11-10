"""M3 full-field verification and joint refinement; Python standard library only."""
import argparse
import csv
import io
import json
import math
import os
import signal
import subprocess


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def run(command, env):
    # Kill ranks as well as their launcher on timeout; never leave MPI waiting.
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, env=env, start_new_session=True) as child:
        try:
            out, err = child.communicate(timeout=25)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            raise AssertionError(f'subprocess timed out: {command}')
        return child.returncode, out, err


def field(command, env, n, m, t, alpha, kind, resources, actual):
    args = ['--N', str(n), '--M', str(m), '--T', repr(t), '--alpha', repr(alpha)]
    code, out, err = run([*command, *args], env)
    require(code == 0, (command, args, code, err))
    summary = dict(item.split('=') for item in err.split())
    require(int(summary['N']) == n and int(summary['M']) == m, summary)
    for key, expected in [('T', t), ('alpha', alpha), ('h', 1/n),
                          ('dt', t/m), ('r', alpha*t*n*n/m)]:
        require(math.isclose(float(summary[key]), expected, rel_tol=1e-15), (key, summary))
    if kind == 'mpi':
        require(int(summary['P_actual']) == actual, summary)
    if kind == 'openmp':
        require(int(summary['Q_requested']) == resources and
                int(summary['Q_actual']) == actual, summary)
    reader = csv.DictReader(io.StringIO(out))
    require(reader.fieldnames == ['i', 'j', 'x', 'y', 'u_numeric', 'u_exact', 'abs_error'],
            reader.fieldnames)
    values = []
    error = modal_error = 0.0
    r = alpha*t*n*n/m
    gain = 1 - 8*r*math.sin(math.pi/(2*n))**2
    for k, row in enumerate(reader):
        i, j = divmod(k, n+1)
        require(i <= n and (int(row['i']), int(row['j'])) == (i, j), (k, row))
        x, y, value, exact, reported = [float(row[key]) for key in reader.fieldnames[2:]]
        require(all(math.isfinite(v) for v in (x, y, value, exact, reported)), row)
        require(abs(x-i/n) < 1e-15 and abs(y-j/n) < 1e-15, row)
        boundary = i in (0, n) or j in (0, n)
        initial = 0.0 if boundary else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
        expected = math.exp(-2*alpha*math.pi**2*t)*initial
        require(abs(exact-expected) < 1e-14, row)
        require(abs(reported-abs(value-expected)) < 1e-14, row)
        if boundary:
            require(value == exact == reported == 0, row)
        require(0 <= value <= 1, ('maximum principle', row))
        values.append(value)
        error = max(error, abs(value-expected))
        modal_error = max(modal_error, abs(value-initial*gain**m))
    require(len(values) == (n+1)**2, ('node count', len(values)))
    require(modal_error <= 1e-13, ('discrete mode', modal_error))
    require(abs(float(summary['E_inf'])-error) < 1e-14, summary)
    for i in range(n+1):
        for j in range(n+1):
            v = values[i*(n+1)+j]
            require(abs(v-values[j*(n+1)+i]) <= 1e-13 and
                    abs(v-values[(n-i)*(n+1)+j]) <= 1e-13 and
                    abs(v-values[i*(n+1)+n-j]) <= 1e-13, 'field symmetry')
    return values, error, modal_error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('serial', 'mpi', 'openmp', 'mpiexec', 'npflag'):
        parser.add_argument('--'+key, required=True)
    parser.add_argument('--max-procs', type=int, choices=range(1, 5), required=True)
    parser.add_argument('--max-threads', type=int, choices=range(1, 5), required=True)
    parser.add_argument('--suite', choices=('default', 'low', 'endpoint', 'boundaries'), required=True)
    parser.add_argument('--pre', action='append', default=[])
    parser.add_argument('--post', action='append', default=[])
    a = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('OMP_', 'GOMP_'))}
    env.update(OMP_DYNAMIC='FALSE', OMP_PROC_BIND='FALSE', OMP_THREAD_LIMIT=str(a.max_threads))
    configs = [('serial', 1, 1, [a.serial], env)]
    for p in range(1, a.max_procs+1):
        configs.append(('mpi', p, p, [a.mpiexec, a.npflag, str(p), *a.pre, a.mpi, *a.post], env))
    for q in range(1, a.max_threads+1):
        configs.append(('openmp', q, q, [a.openmp, '--threads', str(q)], env))
    if a.max_threads >= 2:
        limited = dict(env, OMP_THREAD_LIMIT='2')
        configs.append(('openmp', 4, 2, [a.openmp, '--threads', '4'], limited))
    if a.suite != 'boundaries':
        # Avoid r=1/12, where the leading spatial/time errors cancel.
        t, alpha, levels, divisor = {
            'default': (.1, 1., (20, 40, 80), 1),
            'low': (.2, .25, (12, 24, 48), 1),
            'endpoint': (.125, 1., (12, 24, 48), 2),
        }[a.suite]
        previous = {}
        for n in levels:
            m = n*n//divisor
            r = alpha*t*n*n/m
            # Leading O(h^2) error from log(g); factor 2 allows higher terms.
            bound = 2*math.exp(-2*alpha*t*math.pi**2)*alpha*t*math.pi**4*abs(1/6-2*r)/n**2
            reference = None
            for kind, request, actual, command, run_env in configs:
                values, error, modal = field(command, run_env, n, m, t, alpha, kind, request, actual)
                if reference is None:
                    reference = values
                difference = max(abs(v-ref) for v, ref in zip(values, reference))
                require(difference <= 1e-13, ('parallel difference', difference))
                require(0 < error < bound, ('analytic bound', error, bound))
                key = kind, request, actual
                ratio = previous[key]/error if key in previous else None
                if ratio is not None:
                    require(3.8 < ratio < 4.2, ('joint refinement', key, ratio))
                previous[key] = error
                print('RESULT '+json.dumps(dict(suite=a.suite, solver=kind,
                      requested=request, actual=actual, N=n, M=m, T=t, alpha=alpha,
                      r=r, E_inf=error, E_bound=bound, D_inf=difference,
                      modal_error=modal, ratio=ratio,
                      order=math.log2(ratio) if ratio else None)), flush=True)
    else:
        # Exact binary endpoint and adjacent floating-point values: no decimal ambiguity.
        for kind, request, actual, command, run_env in configs:
            n = actual+1 if kind == 'mpi' else 2
            for m in (1, 2, 7, 8):
                t = m/(4*n*n)
                if n & (n-1):
                    t = math.nextafter(t, 0.)  # stay below the strict wider r check
                values, error, modal = field(command, run_env, n, m, t, 1., kind, request, actual)
                ref, _, _ = field([a.serial], env, n, m, t, 1., 'serial', 1, 1)
                difference = max(abs(v-w) for v, w in zip(values, ref))
                require(difference <= 1e-13, difference)
                print(f'BOUNDARY solver={kind} requested={request} actual={actual} '
                      f'N={n} M={m} T={t!r} r={t*n*n/m:.17g} E_inf={error:.17g} D_inf={difference:.17g}')
            # N=4 endpoint T=1/64 is exactly representable for any legal P<=3.
            # For P=4 use N=8 (T=1/256); both divide exactly in binary.
            n = 8 if kind == 'mpi' and actual == 4 else 4
            endpoint = 1/(4*n*n)
            field(command, run_env, n, 1, endpoint, 1., kind, request, actual)
            below = math.nextafter(endpoint, 0.)
            field(command, run_env, n, 1, below, 1., kind, request, actual)
            for bad_t in (math.nextafter(endpoint, math.inf), endpoint*2):
                code, out, err = run([*command, '--N', str(n), '--M', '1',
                                      '--T', repr(bad_t)], run_env)
                require(code == 2 and not out and 'input error:' in err, (command, code, err))
            if kind == 'mpi' and actual > 1:
                code, out, err = run([*command, '--N', str(actual), '--M', '100',
                                      '--T', '.001'], run_env)
                require(code == 2 and not out and 'input error:' in err, (code, err))
            print(f'STABILITY solver={kind} requested={request} actual={actual} '
                  'below=accepted above=rejected twice=rejected; MPI excess P checked when P>1')
    print(f'M3 {a.suite} PASS; requested MPI P=1..{a.max_procs}, OpenMP Q=1..{a.max_threads}; '
          'higher P/Q and multi-node not run; test durations are not performance data')


if __name__ == '__main__':
    main()
