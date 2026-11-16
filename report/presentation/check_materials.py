#!/usr/bin/env python3
"""Check the current defense deck against saved inputs; never run a solver."""
import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PROJECT = ROOT / 'heat-defense_ppt169_20261112'
NS = {'s': 'http://www.w3.org/2000/svg'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=ROOT / 'records/presentation_checks.json')
    args = ap.parse_args()
    spec = (PROJECT / 'design_spec.md').read_text()
    outline = spec.split('## IX. Content Outline', 1)[1].split('## X.', 1)[0]
    names = re.findall(r'\*\*File\*\*: (\S+\.svg)', outline)
    files = sorted((PROJECT / 'svg_output').glob('*.svg'))
    require(len(names) == 14 and [p.name for p in files] == names, 'page roster mismatch')
    budgets = [int(v) for v in re.findall(r'\*\*Timing\*\*: (\d+)秒', outline)]
    require(len(budgets) == 10 and sum(budgets) == 280, 'main timing budget mismatch')
    trees = {p.name: ET.parse(p).getroot() for p in files}
    visible = '\n'.join(''.join(t.itertext()) for root in trees.values()
                        for t in root.findall('.//s:text', NS))
    notes = (PROJECT / 'notes/total.md').read_text()
    bad = ['02-r1', 'diagnostic-01', 'large-02', 'results/', 'src/',
           '参见实验报告', '详见实验报告', 'F-LARGE']
    require(not any(x in visible or x in notes for x in bad), 'internal reference in audience material')
    sections = re.split(r'^# ', notes, flags=re.M)[1:]
    require([s.splitlines()[0] + '.svg' for s in sections] == names, 'notes order mismatch')
    require(all((PROJECT / 'notes' / (p.stem + '.md')).exists() for p in files), 'missing slide notes')
    counts = [len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]', s.split('\n', 1)[1].replace('---', '')))
              for s in sections[:10]]

    large = list(csv.DictReader((REPO / 'results/performance/large-02-r1/m4-diagnostic-02-r1.csv').open()))
    plot = trees['08_performance.svg']
    coordinate_errors = []
    point_count = 0
    for kind in ['mpi', 'openmp']:
        group = plot.find(".//s:g[@id='" + kind + "-series']", NS)
        rows = [r for r in large if r['N'] == '1024' and r['kind'] == kind]
        marks = group.findall('s:circle' if kind == 'mpi' else 's:rect', NS)
        intervals = group.findall('s:line', NS)
        require(len(rows) == len(marks) == len(intervals) == 5, 'chart point/interval coverage mismatch')
        for k, (r, mark, interval) in enumerate(zip(rows, marks, intervals)):
            x = float(mark.get('cx') if kind == 'mpi' else mark.get('x')) + (0 if kind == 'mpi' else 5)
            y = float(mark.get('cy') if kind == 'mpi' else mark.get('y')) + (0 if kind == 'mpi' else 5)
            coordinate_errors += [abs(x - (110 + 650 * k / 4)),
                                  abs(y - (535 - 75 * float(r['speedup_serial']))),
                                  abs(float(interval.get('y1')) - (535 - 75 * float(r['speedup_low']))),
                                  abs(float(interval.get('y2')) - (535 - 75 * float(r['speedup_high'])))]
            point_count += 1
    require(max(coordinate_errors) < .003, 'chart geometry differs from archived statistics')
    for kind, p in [('mpi', 16), ('openmp', 8), ('openmp', 16)]:
        r = next(r for r in large if r['N'] == '1024' and r['kind'] == kind and int(r['actual']) == p)
        require(f"{float(r['median_seconds']):.4f}" in visible, 'key time mismatch')
        require(f"{float(r['speedup_serial']):.4f}" in visible, 'key speedup mismatch')
        require(f"{float(r['efficiency']) * 100:.2f}%" in visible, 'key efficiency mismatch')
    base = list(csv.DictReader((REPO / 'results/performance/baseline/derived/summary.csv').open()))
    for kind in ['mpi', 'openmp']:
        r = next(r for r in base if r['suite'] == 'scaled' and r['kind'] == kind and r['p'] == '4')
        require(f"{float(r['throughput_ratio_own_p1']):.4f}" in visible, 'throughput mismatch')
    m3 = list(csv.DictReader((REPO / 'results/validation/m3-errors.csv').open()))
    table = trees['07_validation.svg'].find("s:g[@id='refinement-errors']/s:metadata", NS)
    error_rows = json.loads(table.text)['rows']
    for n, row in zip([20, 40, 80], error_rows):
        r = next(r for r in m3 if r['build'] == 'debug' and r['suite'] == 'default'
                 and r['solver'] == 'serial' and int(r['N']) == n)
        cells = [c['text'] if isinstance(c, dict) else c for c in row]
        require(cells[:2] == [r['N'], r['M']], 'refinement grid mismatch')
        mantissa, exponent = cells[2].split(' × 10')
        power = {'⁻⁴': -4, '⁻⁵': -5, '⁻⁶': -6}[exponent]
        require(abs(float(mantissa) * 10 ** power / float(r['E_inf']) - 1) < 5e-5,
                'refinement error rounding mismatch')

    pptx = ROOT / 'presentation/current/presentation-v5.pptx'
    pdf = pptx.with_suffix('.pdf')
    math_in_svg = sum(len(root.findall(".//s:g[@data-pptx-replace-with='formula']", NS)) +
                      len(root.findall('.//s:tspan[@data-pptx-inline-formula]', NS)) for root in trees.values())
    with ZipFile(pptx) as z:
        slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
        slide_notes = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
        roots = [ET.fromstring(z.read(n)) for n in slides]
        maths = sum(sum(e.tag == '{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath'
                        for e in root.iter()) for root in roots)
        animation = any(e.tag.rsplit('}', 1)[-1] in ['timing', 'transition'] for root in roots for e in root.iter())
        media = {hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
        for name in ['02-speedup.png', '05-grid-speedup.png']:
            source = REPO / 'results/figures/large-02-r1-viz-01' / name
            require(digest(source) == digest(PROJECT / 'images' / name), 'image copy mismatch')
            require(digest(source) in media, 'original figure missing in PPTX')
        editable = sum(sum(e.tag == '{http://schemas.openxmlformats.org/drawingml/2006/main}t'
                           for e in root.iter()) for root in roots)
    require(len(slides) == len(slide_notes) == 14, 'package page/notes mismatch')
    require(maths == math_in_svg and not animation, 'native math or disabled-motion contract mismatch')
    import pymupdf
    document = pymupdf.open(pdf)
    require(len(document) == 14, 'rendered PDF page count mismatch')
    for i, page in enumerate(document, 1):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    require(x0 >= -.5 and y0 >= -.5 and x1 <= page.rect.width + .5
                            and y1 <= page.rect.height + .5, f'PDF text outside page {i}: {span["text"]}')
        require(not any(x in page.get_text() for x in bad), 'internal reference in rendered PDF')
    receipt = {'scope': 'current v5 presentation only; no numerical solver runs', 'passed': True,
               'slide_count': 14, 'main_pages': 10, 'backup_pages': 4, 'notes': len(slide_notes),
               'native_math_objects': maths, 'editable_text_runs': editable,
               'source_image_bytes_preserved': True, 'chart_points': point_count, 'chart_intervals': point_count,
               'max_coordinate_error_px': max(coordinate_errors), 'budget_seconds': budgets,
               'main_script_characters': sum(counts), 'speech_estimate_seconds': round(sum(counts) / 280 * 60 + 20, 1),
               'speech_assumption': '280 characters/min + 20s pauses; not a timed human rehearsal',
               'pptx_sha256': digest(pptx), 'pdf_sha256': digest(pdf),
               'report_md_sha256': digest(ROOT / 'FINAL_REPORT.md'),
               'manual_PowerPoint_and_rehearsal': '未运行/待本人验证'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(f'PASS: {len(slides)} slides/notes, {maths} native formulas, {point_count} points/intervals; source figures, statistics and PDF bounds agree.')
    print(args.output)


if __name__ == '__main__':
    main()
