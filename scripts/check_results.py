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
    for e in entries:
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-baseline', type=Path)
    args = parser.parse_args()
    check_migration()
    check_sources()
    check_statistics()
    check_links()
    if args.course_baseline:
        check_course(args.course_baseline)


if __name__ == '__main__':
    main()
