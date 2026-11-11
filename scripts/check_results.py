"""Verify migrated evidence, historical ledgers/source identities and recompute statistics.

Run from repository root. No solver or performance sampling is launched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def check_migration():
    manifest = json.loads((ROOT/'results/migration.json').read_text())
    entries = manifest['entries']
    require(len(entries) == 67, 'expected 67 original artifacts')
    require(len({e['old'] for e in entries}) == len({e['new'] for e in entries}) == 67,
            'duplicate migration paths')
    mapping = {e['old']: e for e in entries}
    original_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only',
        manifest['source_revision'], '--', 'docs/performance', 'docs/validation'], cwd=ROOT, text=True).splitlines()
    require(set(mapping) == set(original_paths), 'migration must cover the original Git inventory exactly')
    for e in entries:
        original = subprocess.check_output(['git', 'show', manifest['source_revision']+':'+e['old']], cwd=ROOT)
        require(hashlib.sha256(original).hexdigest() == e['sha256'], 'migration original hash mismatch')
        require(not (ROOT/e['old']).exists(), 'legacy path still exists: '+e['old'])
        require((ROOT/e['new']).is_file(), 'missing destination: '+e['new'])
        require(digest(ROOT/e.get('snapshot', e['new'])) == e['sha256'], 'changed evidence: '+e['old'])
        if 'current_sha256' in e:
            require(digest(ROOT/e['new']) == e['current_sha256'], 'changed explanation: '+e['new'])
    ledgers = 0
    for e in entries:
        if Path(e['old']).suffix != '.sha256' and Path(e['old']).name != 'SHA256SUMS':
            continue
        ledgers += 1
        for line in (ROOT/e['new']).read_text().splitlines():
            expected, name = line.split(maxsplit=1)
            old = posixpath.normpath(posixpath.join(posixpath.dirname(e['old']), name.lstrip('*')))
            require(old in mapping, 'unmapped ledger path: '+old)
            item = mapping[old]
            require(digest(ROOT/item.get('snapshot', item['new'])) == expected, 'old ledger mismatch: '+old)
    require(ledgers == 4, 'expected four original ledgers')
    print('PASS 67 artifacts, two snapshots, four historical ledgers; no legacy duplicates')
    return entries


def check_sources():
    base = ROOT/'results/performance'
    files = [base/'baseline/run-01/metadata.json'] + [base/d/('m4-diagnostic-'+i+'.json')
             for d, i in [('diagnostic-01', '01'), ('large-02', '02'), ('large-02-r1', '02-r1')]]
    total = 0
    for path in files:
        m = json.loads(path.read_text())
        for name, expected in m['source_sha256'].items():
            data = subprocess.check_output(['git', 'show', m['revision']+':'+name], cwd=ROOT)
            require(hashlib.sha256(data).hexdigest() == expected, 'historical source mismatch: '+name)
            total += 1
    require(not json.loads(files[2].read_text())['complete'] and json.loads(files[3].read_text())['complete'],
            'stopped/completed identity mismatch')
    print(f'PASS {total} historical source hashes at four recorded commits; stopped02 excluded')


def run(args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)


def check_statistics():
    with tempfile.TemporaryDirectory(prefix='heat-result-audit-') as temporary:
        out = Path(temporary)
        base = ROOT/'results/performance'
        run(['scripts/analyze_performance.py', base/'baseline/run-01', '--output', out/'baseline', '--no-plots'])
        require((out/'baseline/summary.csv').read_bytes() == (base/'baseline/derived/summary.csv').read_bytes(),
                'baseline CSV differs')
        for directory, identifier, script, suffixes in [
            ('diagnostic-01', '01', 'analyze_diagnostics.py', ['.csv', '-workers.csv']),
            ('large-02-r1', '02-r1', 'analyze_large.py', ['.csv', '-rounds.csv'])]:
            prefix = base/directory/('m4-diagnostic-'+identifier)
            dest = out/directory
            run(['scripts/'+script, prefix, '--output', dest, '--no-plots'])
            for suffix in suffixes:
                require(Path(str(prefix)+suffix).read_bytes() == Path(str(dest)+suffix).read_bytes(),
                        'recomputed CSV differs: '+str(prefix)+suffix)
        run(['tests/check_statistics.py'])
        # Only existing synthetic functions; do not launch their real-solver checks.
        sys.path.insert(0, str(ROOT/'tests'))
        from check_large import unit_checks
        from check_diagnostics import statistics_checks
        unit_checks(out)
        statistics_checks()
    print('PASS all three completed datasets: five CSV files byte-identical; synthetic checks')


def check_links():
    files = [ROOT/n for n in ('README.md', 'SPEC.md', 'PLAN.md', 'STATUS.md')]
    files += list((ROOT/'docs').glob('*.md')) + list((ROOT/'results').rglob('*.md'))
    for path in files:
        text = path.read_text()
        require(sum(line.startswith('```') for line in text.splitlines()) % 2 == 0,
                'unbalanced fences: '+str(path))
        for name in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', text):
            if ':' in name or name.startswith('#'):
                continue
            target = name.split('#')[0]
            require((path.parent/target).exists(), f'broken link in {path.relative_to(ROOT)}: {name}')
    print('PASS current Markdown file links and code fences')


def check_course(baseline):
    before = json.loads(baseline.read_text())
    after = {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT/'docs/sources').rglob('*')) if p.is_file()}
    require(before == after, 'course materials changed')
    require(not subprocess.check_output(['git', 'ls-files', 'docs/sources'], cwd=ROOT), 'course material tracked')
    print(f'PASS {len(after)} course material paths/hashes unchanged and untracked')


def check_figures():
    directory = ROOT/'results/figures/large-02-r1-viz-01'
    if not directory.exists():
        print('NOT RUN new figure checks: figure directory absent')
        return
    m = json.loads((directory/'generation.json').read_text())
    require((m['configuration_count'], m['measured_samples']) == (44, 440), 'figure counts')
    base = ROOT/'results/performance/large-02-r1/m4-diagnostic-02-r1'
    manifest = json.loads(Path(str(base)+'.json').read_text())
    require(m['sampling_revision'] == manifest['revision'], 'figure sampling version')
    ids = {c['id'] for c in manifest['matrix']}
    require(len(m['charts']) == 9, 'expected nine chart groups')
    for chart in m['charts']:
        expected = ids
        if 'rounds-' in chart['name']:
            kind = 'mpi' if chart['name'].endswith('mpi') else 'openmp'
            expected = {c['id'] for c in manifest['matrix'] if c['kind'] in ('serial', kind)}
            require(chart['raw_sample_points'] == len(expected)*10 == 240, 'round plot coverage')
        require(set(chart['configurations']) == expected and len(chart['configurations']) == len(expected),
                'chart configuration coverage: '+chart['name'])
        svg = ET.parse(directory/(chart['name']+'.svg')).getroot()
        require(not list(svg.iter('{http://www.w3.org/2000/svg}text')), 'SVG must embed glyph paths')
        require((directory/(chart['name']+'.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), 'invalid PNG')
        if chart['name'] == '07-samples':
            points = sum(len(list(g.iter('{http://www.w3.org/2000/svg}use')))
                         for g in svg.iter('{http://www.w3.org/2000/svg}g')
                         if g.get('id', '').startswith('PathCollection_'))
            require(points == chart['raw_sample_points'] == 440, 'SVG must contain all 440 sample markers')
    require((directory/'statistics.csv').read_bytes() == Path(str(base)+'.csv').read_bytes(), 'figure CSV changed')
    for name, expected in {**m['inputs'], **m['script_sha256']}.items():
        require(digest(ROOT/name) == expected, 'figure input/script changed: '+name)
    font = Path(m['font']['path'])
    if font.exists():
        require(digest(font) == m['font']['sha256'], 'font changed')
    else:
        print('NOT RUN local font hash: recorded external font unavailable; SVG has embedded glyph paths')
    ledger_files = set()
    for line in (directory/'SHA256SUMS').read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        require(digest(directory/name) == expected, 'figure checksum: '+name)
        ledger_files.add(name)
    require(ledger_files == {p.name for p in directory.iterdir() if p.name != 'SHA256SUMS'}, 'figure ledger coverage')
    print('PASS nine SVG/PNG groups, exact 44-config coverage, 440 SVG raw markers, statistics/input/script hashes')


def check_refusal():
    for script, args in [
        ('diagnose.py', ['--build', '/nonexistent', '--run-id', '01']),
        ('benchmark_large.py', ['--build', '/nonexistent', '--run-id', '02-r1']),
        ('plot_results.py', ['--output', 'results/figures/large-02-r1-viz-01'])]:
        result = subprocess.run([sys.executable, 'scripts/'+script, *args], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode != 0 and 'directory already exists' in result.stderr,
                'existing result directory was not rejected before work: '+script)
    print('PASS diagnostic/large/plot reused directories refused before build or generation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-baseline', type=Path)
    args = parser.parse_args()
    check_migration()
    check_sources()
    check_statistics()
    check_links()
    check_figures()
    check_refusal()
    if args.course_baseline:
        check_course(args.course_baseline)


if __name__ == '__main__':
    main()
