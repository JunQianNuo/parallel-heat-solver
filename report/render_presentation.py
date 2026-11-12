#!/usr/bin/env python3
"""Open the delivered PPTX with LibreOffice and render its PDF for review."""
import argparse, os, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--soffice',default=shutil.which('soffice'))
    ap.add_argument('--library-path',help='Optional isolated LibreOffice runtime library path')
    ap.add_argument('--fontconfig',type=Path,help='Optional existing fontconfig XML')
    args=ap.parse_args()
    if not args.soffice:ap.error('LibreOffice not found; provide --soffice')
    env=os.environ.copy();env['SAL_USE_VCLPLUGIN']='svp'
    if args.library_path:env['LD_LIBRARY_PATH']=args.library_path
    if args.fontconfig:env['FONTCONFIG_FILE']=str(args.fontconfig.resolve())
    profile=ROOT.parent/'build/m5-lo/profile';profile.mkdir(parents=True,exist_ok=True)
    subprocess.run([args.soffice,f'-env:UserInstallation={profile.resolve().as_uri()}','--headless','--convert-to','pdf','--outdir',str(ROOT),str(ROOT/'presentation.pptx')],env=env,check=True,timeout=120)
    require=ROOT/'presentation.pdf'
    if not require.exists():raise RuntimeError('PDF was not produced')
    print(require)
if __name__=='__main__':main()
