#!/usr/bin/env python3
"""Render the authored Markdown report to A4 PDF; never reads experiment journals."""
import argparse, hashlib, html, json, re, subprocess, sys
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--font', default='/mnt/c/Windows/Fonts/msyh.ttc')
    ap.add_argument('--math-python', default='python3')
    args=ap.parse_args()
    pdfmetrics.registerFont(TTFont('Chinese',args.font,subfontIndex=0))
    source=(ROOT/'FINAL_REPORT.md').read_text()
    cache=ROOT.parent/'build/m5-report-math';cache.mkdir(parents=True,exist_ok=True)
    formulas=list(dict.fromkeys(re.findall(r'\$\$(.*?)\$\$|(?<!\$)\$([^$\n]+)\$(?!\$)',source,re.S)))
    expressions=[a.strip() or b.strip() for a,b in formulas]
    jobs=[]
    for expr in expressions:
        path=cache/(hashlib.sha256(expr.encode()).hexdigest()[:20]+'.png')
        jobs.append({'expr':expr.replace('\n',' '),'path':str(path)})
    jobfile=cache/'jobs.json';jobfile.write_text(json.dumps(jobs))
    code=r"""import json,sys,matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import math_to_image
for j in json.load(open(sys.argv[1])):
 expr=j['expr'].replace(r'\le',r'\leq').replace(r'\bmod',r'\mathrm{mod}')
 math_to_image('$'+expr+'$',j['path'],dpi=200,format='png',color='#172e38')
"""
    subprocess.run([args.math_python,'-c',code,str(jobfile)],check=True)
    paths={e:Path(j['path']) for e,j in zip(expressions,jobs)}
    body=ParagraphStyle('body',fontName='Chinese',fontSize=9.4,leading=16,wordWrap=None,spaceAfter=7)
    cell=ParagraphStyle('cell',parent=body,fontSize=8,leading=12,spaceAfter=0)
    styles={n:ParagraphStyle(n,parent=body,fontSize=size,leading=lead,spaceBefore=12,spaceAfter=8,textColor=colors.HexColor('#164e63')) for n,size,lead in [('h1',21,31),('h2',14,22),('h3',11,18)]}
    def inline(txt):
        pieces=re.split(r'(\$[^$]+\$)',txt)
        out=[]
        for part in pieces:
            if part.startswith('$') and part.endswith('$'):
                p=paths[part[1:-1].strip()]; w,h=ImageReader(str(p)).getSize(); ht=11
                out.append(f'<img src="{p}" width="{w/h*ht:.2f}" height="{ht}" valign="-2"/>')
            else:
                part=html.escape(part)
                part=re.sub(r'`([^`]+)`',r'<font color="#155e75">\1</font>',part)
                part=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<link href="\2" color="#155e75">\1</link>',part)
                out.append(part)
        return ''.join(out)
    lines=source.splitlines(); story=[]; i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line=='$$':
            i+=1;buf=[]
            while i<len(lines) and lines[i].strip()!='$$':buf.append(lines[i]);i+=1
            expr='\n'.join(buf).strip();p=paths[expr];w,h=ImageReader(str(p)).getSize();height=20; width=w/h*height
            if width>475:height*=475/width;width=475
            story.extend([Image(str(p),width=width,height=height),Spacer(1,10)]);i+=1;continue
        if line.startswith('!['):
            path=ROOT/re.search(r'\]\(([^)]+)\)',line).group(1);w,h=ImageReader(str(path)).getSize(); width=475
            story.extend([Image(str(path),width=width,height=width*h/w),Spacer(1,7)]);i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',v) for v in row):rows.append(row)
                i+=1
            count=len(rows[0]); widths=([60,200,215] if count==3 else [475/count]*count)
            table=Table([[Paragraph(inline(v),cell) for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf1f5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#94a3b8')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#dce3e9')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,10)]);continue
        if line.startswith('```'):
            i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                story.append(Paragraph(html.escape(lines[i]),ParagraphStyle('code',parent=cell,fontSize=7.5,leading=12)));i+=1
            story.append(Spacer(1,8));i+=1;continue
        match=re.match(r'^(#{1,3}) (.+)',line)
        if match:story.append(Paragraph(inline(match[2]),styles['h'+str(len(match[1]))]));i+=1;continue
        buf=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||\$\$|!\[|```|- )',lines[i].strip()):buf.append(lines[i].strip());i+=1
        story.append(Paragraph(inline(' '.join(buf)),body))
    def footer(c,doc):
        c.setFont('Chinese',8);c.setFillColor(colors.HexColor('#64748b'));c.drawString(48,27,'二维热传导 · 最终报告 · 2026-11-12');c.drawRightString(547,27,str(doc.page))
    doc=SimpleDocTemplate(str(ROOT/'FINAL_REPORT.pdf'),pagesize=(595.28,841.89),rightMargin=60,leftMargin=60,topMargin=42,bottomMargin=48,title='二维热传导方程的串行、MPI与OpenMP求解',author='姓名待填写；Codex辅助整理')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Rendered',ROOT/'FINAL_REPORT.pdf')
if __name__=='__main__':main()
