#!/usr/bin/env python3
"""Check the written report against archived evidence without opening a PPTX."""
import argparse, csv, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--course-baseline',type=Path)
    ap.add_argument('--output',type=Path,default=ROOT/'records/report_checks.json')
    args=ap.parse_args()
    report=ROOT/'FINAL_REPORT.md';source=report.read_text()
    require(source.count('```')%2==0,'unclosed code fence')
    require(source.count('$$')%2==0,'unclosed display formula')
    require(all(re.search(rf'^## {i}\. ',source,re.M) for i in range(1,9)),'missing numbered report section')
    links=0
    for target in re.findall(r'\]\(([^)]+)\)',source):
        if re.match(r'https?://|#',target):continue
        require((ROOT/target.split('#')[0]).exists(),f'missing report link: {target}');links+=1
    rows=list(csv.DictReader((REPO/'results/performance/large-02-r1/m4-diagnostic-02-r1.csv').open(newline='')))
    checked=[]
    for N in [384,512,768,1024]:
        selected={(r['kind'],int(r['actual'])):r for r in rows if int(r['N'])==N}
        for kind,k in [('mpi',16),('openmp',8),('openmp',16)]:
            r=selected[kind,k];require(f"{float(r['speedup_serial']):.4f}" in source,f'speedup mismatch {N}/{kind}/{k}')
        require(f"{float(selected['mpi',16]['efficiency'])*100:.2f}%" in source,f'efficiency mismatch {N}')
        checked.append(N)
    m3=list(csv.DictReader((REPO/'results/validation/m3-errors.csv').open()))
    for r in m3:
        if r['build']=='debug' and r['suite']=='default' and r['solver']=='serial' and r['ratio']:
            require(f"{float(r['ratio']):.6f}" in source,'M3 error ratio mismatch')
            require(f"{float(r['order']):.6f}" in source,'M3 observed order mismatch')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    pdf=ROOT/'FINAL_REPORT.pdf';require(pdf.read_bytes().startswith(b'%PDF'),'invalid PDF header')
    pdf_check={'page_analysis':'未运行：缺少PyMuPDF'}
    try:import pymupdf
    except ImportError:pass
    else:
        doc=pymupdf.open(pdf);outside=[]
        for i,page in enumerate(doc,1):
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:outside.append({'page':i,'text':span['text']})
        require(not outside,'PDF text crosses page boundary')
        pdf_check={'pages':len(doc),'text_outside_page':outside,'page_analysis':'读取现有PDF；未重新生成或渲染'}
    course='未运行：未提供本轮前置快照'
    if args.course_baseline:
        before=json.loads(args.course_baseline.read_text());base=REPO/'docs/sources'
        after={str(p.relative_to(base)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()}
        require(before==after,'read-only course material changed');course=f'{len(after)} files: paths/content unchanged'
    result={'scope':'书面报告；未调用PPT工具、求解器、构建、数值回归或性能采样','report_links_checked':links,'numbered_sections':8,'performance_table_N':checked,'M3_error_ratios_orders':'对照归档CSV通过','report_markdown_sha256':sha(report),'report_pdf_sha256':sha(pdf),'pdf':pdf_check,'course_protection':course,'human_review':'未验收；姓名学号待填写，内容/排版待用户审阅'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
