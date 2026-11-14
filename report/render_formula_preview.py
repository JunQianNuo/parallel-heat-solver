#!/usr/bin/env python3
"""Build ordinary SVG vector glyphs for a native-formula fallback, never a slide."""
import argparse, copy, io, json, re, xml.etree.ElementTree as ET
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    ns={'s':'http://www.w3.org/2000/svg'}
    source=ET.parse(args.source).getroot()
    marker=source.find("s:g[@id='update-equation']",ns)
    formula=json.loads(marker.find('s:metadata',ns).text)
    matplotlib.rcParams['mathtext.fontset']='stix'
    buf=io.BytesIO()
    math_to_image('$'+formula['latex']+'$',buf,prop=FontProperties(size=formula['font_size']),format='svg')
    root=ET.fromstring(buf.getvalue());defs={e.get('id'):e for e in root.iter() if e.get('id')}
    def plain(e):
        tag=e.tag.split('}')[-1]
        if tag in ['metadata','defs','style']:return None
        if tag=='use':
            original=defs[e.get('{http://www.w3.org/1999/xlink}href')[1:]]
            out=ET.Element('g',{'transform':f"translate({e.get('x','0')} {e.get('y','0')}) "+e.get('transform','')})
            out.append(plain(copy.deepcopy(original)));return out
        out=ET.Element(tag,{k:v for k,v in e.attrib.items() if k not in ['id','style']})
        for item in e.get('style','').split(';'):
            if ':' in item:
                k,v=item.split(':',1);out.set(k.strip(),v.strip())
        out.text=e.text
        for child in e:
            c=plain(child)
            if c is not None:out.append(c)
        return out
    result=ET.Element('svg',{'viewBox':root.get('viewBox'),'xmlns':ns['s'],'data-preview-font':'STIX; native Office Math uses Cambria Math'})
    for child in root:
        c=plain(child)
        if c is not None:result.append(c)
    for e in result.iter():
        if 'transform' in e.attrib:
            e.set('transform',re.sub(r'-?\d+(?:\.\d+)?',lambda m:format(round(float(m[0]),2),'g'),e.get('transform')))
        for k,v in list(e.attrib.items()):
            if re.fullmatch(r'#[0-9a-fA-F]{6}',v):e.set(k,v.upper())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    ET.indent(result);args.output.write_text(ET.tostring(result,encoding='unicode')+'\n')
    print(root.get('viewBox'))
if __name__=='__main__':main()
