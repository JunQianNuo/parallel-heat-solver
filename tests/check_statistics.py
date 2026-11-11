"""Synthetic statistics unit checks; these numbers are never performance evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze_performance import analyze
from benchmark import configurations, require

protocol = json.loads((Path(__file__).resolve().parents[1] / 'results/performance/baseline/protocol.json').read_text())
matrix = configurations(protocol)
rows = []
for c in matrix:
    rows.append(dict(validation=c['id'], D_inf=0, discrete_mode_diff=0, E_inf=1e-6))
    for rep, value in enumerate([9, 5, 1, 3, 2, 100]):
        # Warmup=9 excluded. Median=3; min=1, max=100, no outlier removal.
        seconds = value / c['p']
        err = (f'N={c["N"]} M={c["M"]} T={c["T"]} alpha={c["alpha"]} r=.16 E_inf=1e-6\n'
               f'loop_seconds={seconds}\n')
        if c['kind'] == 'mpi':
            err += f'P_actual={c["p"]}\n'
        elif c['kind'] == 'openmp':
            err += f'Q_requested={c["p"]} Q_actual={c["p"]}\n'
        rows.append(dict(config=c, repetition=rep, warmup=rep == 0,
                         revision='synthetic-test-only', returncode=0, stderr=err))
with tempfile.TemporaryDirectory(prefix='heat-statistics-') as tmp:
    d = Path(tmp)
    (d/'metadata.json').write_text(json.dumps(dict(protocol=protocol, revision='synthetic-test-only')))
    (d/'matrix.json').write_text(json.dumps(matrix))
    (d/'complete.json').write_text(json.dumps(dict(measured_samples=len(matrix)*5, source_and_binary_hashes_unchanged=True)))
    def write(data):
        (d/'samples.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in data))
    write(rows)
    actual = analyze(d)
    for r in actual:
        require(r['median_seconds'] == 3/r['p'], r)
        require(r['min_seconds'] == 1/r['p'] and r['max_seconds'] == 100/r['p'], r)
        require(r['speedup_serial'] == r['p'] and r['efficiency_serial'] == 1, r)
        if r['suite'] == 'scaled':
            require(abs(r['throughput_ratio_own_p1'] - r['work_ratio']*r['p']) < 1e-12, r)
    for fault in ('missing', 'duplicate', 'version', 'team', 'parameters', 'nan', 'error', 'missing-validation'):
        broken = deepcopy(rows)
        if fault == 'missing': broken.pop()
        elif fault == 'duplicate': broken.append(broken[-1])
        elif fault == 'version': broken[-1]['revision'] = 'other'
        elif fault == 'team': broken[-1]['stderr'] = broken[-1]['stderr'].replace('Q_actual=4', 'Q_actual=2')
        elif fault == 'parameters': broken[-1]['stderr'] = broken[-1]['stderr'].replace('N=362', 'N=361')
        elif fault == 'nan': broken[-1]['stderr'] = broken[-1]['stderr'].replace('loop_seconds=25.0', 'loop_seconds=nan')
        elif fault == 'error': broken[-1]['stderr'] = broken[-1]['stderr'].replace('E_inf=1e-6', 'E_inf=2e-6')
        elif fault == 'missing-validation': broken.pop(0)
        write(broken)
        try:
            analyze(d)
        except RuntimeError:
            print('STATISTICS correctly rejected', fault)
        else:
            raise RuntimeError('accepted corrupted synthetic data: '+fault)
print('STATISTICS median/range/baseline/work normalization and eight corruption cases passed (synthetic only)')
