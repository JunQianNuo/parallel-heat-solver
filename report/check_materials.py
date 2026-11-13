#!/usr/bin/env python3
"""Check authored report provenance and links without running any solver."""
import csv, hashlib, json, re, xml.etree.ElementTree as ET
from zipfile import ZipFile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent

def require(condition,message):
    if not condition: raise ValueError(message)

def main():
    files=[p for p in ROOT.rglob('*.md') if not any(x in p.parts for x in ['backup','live_preview','svg_final'])]
    links=0
    for p in files:
        txt=p.read_text()
        require(txt.count('```')%2==0,f'unclosed fence: {p}')
        for target in re.findall(r'\]\(([^)]+)\)',txt):
            if re.match(r'https?://|#',target):continue
            require((p.parent/target.split('#')[0]).exists(),f'missing link {p}: {target}');links+=1
    report=(ROOT/'FINAL_REPORT.md').read_text()
    rows=list(csv.DictReader((REPO/'results/performance/large-02-r1/m4-diagnostic-02-r1.csv').open(newline='')))
    for N in [384,512,768,1024]:
        selected={(r['kind'],int(r['actual'])):r for r in rows if int(r['N'])==N}
        for kind,p in [('mpi',16),('openmp',8),('openmp',16)]:
            r=selected[kind,p]
            require(f"{float(r['speedup_serial']):.4f}" in report,f'missing rounded speedup {N}/{kind}/{p}')
        require(f"{float(selected['mpi',16]['efficiency'])*100:.2f}%" in report,f'missing efficiency {N}')
    m3=list(csv.DictReader((REPO/'results/validation/m3-errors.csv').open()))
    for r in m3:
        if r['build']=='debug' and r['suite']=='default' and r['solver']=='serial' and r['ratio']:
            require(f"{float(r['ratio']):.6f}" in report,'M3 ratio mismatch')
            require(f"{float(r['order']):.6f}" in report,'M3 order mismatch')
    notes=(ROOT/'SPEAKER_NOTES.md').read_text()
    pages=re.findall(r'## P(\d+) .*?· (\d+)秒[^\n]*\n\n(.*?)(?=\n## |\Z)',notes,re.S)
    require(len(pages)==8,'expected eight main-script pages')
    require(sum(int(t) for _,t,_ in pages)==280,'expected 280 seconds')
    speech=[]
    for n,t,txt in pages:
        count=len(re.findall('[\u4e00-\u9fffA-Za-z0-9]',txt))
        speech.append({'page':n,'budget_seconds':int(t),'CJK_and_alphanumeric_characters':count,'characters_per_budget_minute':round(count/int(t)*60,1)})
    total=sum(p['CJK_and_alphanumeric_characters'] for p in speech)
    # Explicit scenario, not an observed human speech rate or timed rehearsal.
    scenario={'assumed_characters_per_minute':280,'assumed_pause_seconds':20,'estimated_total_seconds':round(total/280*60+20,1),'human_rehearsal':'未运行/待用户验证'}
    pdf=ROOT/'FINAL_REPORT.pdf'
    require(pdf.read_bytes().startswith(b'%PDF'),'invalid PDF signature')
    project=ROOT/'heat-defense_ppt169_20261112'
    ns={'s':'http://www.w3.org/2000/svg'}
    svg=ET.parse(project/'svg_output/07_performance.svg').getroot()
    area=svg.find(".//s:g[@id='n1024-speedup-chartArea']",ns)
    expected=[r for r in rows if r['N']=='1024' and r['kind']!='serial']
    points=list(area.findall('.//s:circle',ns))+list(area.findall('.//s:rect',ns))
    require(len(points)==10,'expected ten chart points')
    for el,r in zip(points,expected):
        x=float(el.get('cx')) if el.tag.endswith('circle') else float(el.get('x'))+5
        y=float(el.get('cy')) if el.tag.endswith('circle') else float(el.get('y'))+5
        require(abs(x-(120+40*(int(r['actual'])-1)))<.001,'chart x mismatch')
        require(abs(y-(540-80*float(r['speedup_serial'])))<.001,'chart y mismatch')
    intervals=[e for e in area.findall('.//s:line',ns) if e.get('x1')==e.get('x2')]
    require(len(intervals)==10,'expected ten asymmetric intervals')
    for el,r in zip(intervals,expected):
        require(abs(float(el.get('y1'))-(540-80*float(r['speedup_high'])))<.001,'CI high mismatch')
        require(abs(float(el.get('y2'))-(540-80*float(r['speedup_low'])))<.001,'CI low mismatch')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    figures=REPO/'results/figures/large-02-r1-viz-01'
    for n in ['02-speedup.png','05-grid-speedup.png']:
        require(sha(project/'images'/n)==sha(figures/n),'figure copy changed')
    require(sha(project/'sources/m4-diagnostic-02-r1.csv')==sha(REPO/'results/performance/large-02-r1/m4-diagnostic-02-r1.csv'),'CSV copy changed')
    pptx=ROOT/'presentation-v3.pptx'
    with ZipFile(pptx) as z:
        slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        notes_files=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        require(len(slides)==len(notes_files)==12,'PPT slide/notes count')
        formula_count=0; shape_count=0
        namespaces={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
        for n in slides:
            tree=ET.fromstring(z.read(n));formula_count+=len(tree.findall('.//m:oMath',namespaces));shape_count+=len(tree.findall('.//p:sp',namespaces))
            require(tree.find('p:timing',namespaces) is None,'unexpected animations')
            require(tree.find('p:transition',namespaces) is None,'unexpected transitions')
        require(formula_count>=1 and shape_count>100,'expected native math and editable text/shapes')
        math_tree=ET.fromstring(z.read('ppt/slides/slide3.xml'))
        math_parts=math_tree.findall('.//m:eqArr/m:e',namespaces)
        require(len(math_parts)==2,'P03 expected two native equation rows')
        require(not any('&' in (e.text or '') for e in math_tree.findall('.//m:t',namespaces)),'P03 leaked alignment token')
        scripts=math_tree.findall('.//m:sSubSup',namespaces)
        pairs=[(''.join(e.find('m:sub',namespaces).itertext()),''.join(e.find('m:sup',namespaces).itertext())) for e in scripts]
        require(pairs==[('ij','n+1'),('ij','n'),('i−1,j','n'),('i+1,j','n'),('i,j−1','n'),('i,j+1','n')],'P03 native formula subscripts/time layers mismatch')
        media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
        require(all(sha(figures/n) in media for n in ['02-speedup.png','05-grid-speedup.png']),'embedded figure mismatch')
        for i,(_,_,txt) in enumerate(pages,1):
            tree=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
            text=''.join(tree.itertext())
            require(txt.strip() in text,f'notes/script mismatch P{i:02}')
    course_before=REPO/'build/m5-v3/course-before.json'
    course_check='未运行：当前机器缺少本轮前置快照'
    if course_before.exists():
        before=json.loads(course_before.read_text())
        after={str(p.relative_to(REPO/'docs/sources')):sha(p) for p in sorted((REPO/'docs/sources').rglob('*')) if p.is_file()}
        require(before==after,'course files changed since M5 snapshot')
        course_check=f'{len(after)} files: paths/content unchanged since this M5 snapshot'
    summary={'local_file_links_checked':links,'performance_table':'checked against archived CSV','M3_ratios_orders':'checked against archived CSV','main_script':speech,'total_count':total,'timing_scenario':scenario,'solver_build_tests_sampling':'未运行：M5只整理既有证据','report_pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}
    summary.update({'P03_native_formula':'two rows; six space/time scripts checked; no visible alignment token','chart_points_and_intervals':'10 points and 10 asymmetric intervals verified from CSV','pptx':{'slides':len(slides),'notes':len(notes_files),'native_math':formula_count,'editable_shapes':shape_count,'animations_transitions':0,'file':pptx.name,'sha256':sha(pptx)},'course_protection':course_check,'presentation_pdf_sha256':sha(ROOT/'presentation-v3.pdf')})
    out=ROOT/'material_checks.json';out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
