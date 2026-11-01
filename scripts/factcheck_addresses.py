#!/usr/bin/env python3
"""Spot-check: every hex address (5+ digits) on a line of hardware/*.md that cites a source key must appear
verbatim in a local clone of that source. Clones are expected at the paths in M (edit to your layout); keys
without a local clone are skipped. Reads only; prints what it could not find.
Usage: python3 scripts/factcheck_addresses.py"""
import re,glob,os,subprocess,collections,sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
M=[('digikit','/tmp/src/digikit'),('dn2-cfw','/tmp/src/dn2-cfw'),('dn2-ele3','/tmp/src/dn2_firmware_explore'),('dn2-memory-map','/tmp/src/dn2_firmware_explore'),('dn2-bootstrap','/tmp/src/dn2_firmware_explore'),('dn2-hw','/tmp/src/dn2_firmware_explore'),('dn2-principles','/tmp/src/dn2_firmware_explore'),
('dn2-caves','/tmp/src/dn2_firmware_explore'),('dn2-osupdate','/tmp/src/dn2_firmware_explore'),('dn2-dspstop','/tmp/src/dn2_firmware_explore'),('dn2-stall','/tmp/src/dn2_firmware_explore'),
('dn2-ddr','/tmp/src/dn2_firmware_explore'),('dn2-sharcload','/tmp/src/dn2_firmware_explore'),('dn2-service','/tmp/src/dn2_firmware_explore'),('dn2-mods','/tmp/src/dn2_firmware_explore'),
('dn2-dt2port','/tmp/src/dn2_firmware_explore'),('dn2-cfdsp','/tmp/src/dn2_firmware_explore'),('dn2-midirpc','/tmp/src/dn2_firmware_explore'),
('synthack','/tmp/src/synthack-up'),('dt2-plaits','/tmp/src/dt2research'),('dt2-research','/tmp/src/dt2research'),
('own-dt2-notes','/home/claude/digitaktiimods'),('own-heatfx-notes','/home/claude/analogheatfxmods'),('armio','/tmp/src/armio'),('syntakt-workbench','/tmp/src/workbench')]
def clone_for(k):
    for p,d in M:
        if k.startswith(p): return d
cache={}
def text_of(d):
    if d not in cache:
        out=subprocess.run(['git','-C',d,'grep','-h','-i','-I','-o','-E','0x[0-9a-f]+','--','*.md','*.s','*.S','*.inc','*.py','*.c','*.h','*.json','*.toml','*.txt'],capture_output=True,text=True).stdout
        cache[d]=set(x.lower() for x in out.split())
    return cache[d]
tot=0;miss=collections.defaultdict(list);elsewhere=collections.defaultdict(list)
for f in glob.glob('hardware/**/*.md',recursive=True):
    if f.endswith(('SOURCES.md','CONFLICTS.md','READING-LEDGER.md','MINING.md')): continue
    for line in open(f):
        keys=re.findall(r'\{([a-z0-9-]+)\}',line)
        dirs={clone_for(k) for k in keys}-{None}
        if not dirs: continue
        for h in set(re.findall(r'0x[0-9a-fA-F]{5,}',line)):
            tot+=1; hl=h.lower()
            def found(ds): return any(hl in text_of(d) or ('0x'+hl[2:].lstrip('0')) in text_of(d) for d in ds)
            if not found(dirs):
                (elsewhere if found({d for _,d in M}) else miss)[f].append(h)
n=sum(len(v) for v in miss.values()); e=sum(len(v) for v in elsewhere.values())
print(f"checked {tot} addresses; in another local source than the one cited: {e}; not found anywhere: {n}")
for f,v in elsewhere.items(): print("  elsewhere:", f, sorted(set(v))[:25])
for f,v in miss.items(): print("  MISSING:", f, sorted(set(v))[:25])
sys.exit(1 if n else 0)
