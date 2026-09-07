# Intake for RSI store pages Sleven saved.  C1, 2026-09-06.
# Scans the connected folders for "<Ship> - <Maker> _ Star Citizen Store_files",
# takes the ship name from the page title EXACTLY, checks it against the front page
# ship list, and copies the pictures in.  A name that does not match is reported and
# skipped - never guessed (rule 17, rule 11).
import os, re, json, shutil, sys
HOME=os.path.expanduser('~')
MNT=HOME+'/mnt'
RAW=HOME+'/mnt/citizen-compass/data-layer/raw/ship-images-from-sleven'
DERV=HOME+'/mnt/citizen-compass/data-layer/derived/main-page-concepts'

d=json.load(open(DERV+'/frontpage_data.json',encoding='utf-8'))
ships=d['ships'] if isinstance(d,dict) and 'ships' in d else d
if isinstance(ships,dict): ships=list(ships.values())
NAMES={(s.get('n') or s.get('name')) for s in ships}

man=json.load(open(RAW+'/manifest.json',encoding='utf-8'))
ALIAS=man.get('alias',{})   # RSI store page title -> our front page ship name
have={e['ship'] for e in man['ships']}

pat=re.compile(r'^(.+?) - (.+?) _ Star Citizen Store_files$')
added=[]; problems=[]
for f in sorted(os.listdir(MNT)):
    m=pat.match(f)
    if not m: continue
    ship, maker = m.group(1).strip(), m.group(2).strip()
    if ship in have: continue
    ship = ALIAS.get(ship, ship)          # explicit, recorded mapping only. never guessed.
    if ship in have: continue
    if ship not in NAMES:
        problems.append((f, ship, 'page title does not match any front page ship name')); continue
    src=os.path.join(MNT,f)
    pics=sorted([x for x in os.listdir(src) if x.lower().endswith(('.webp','.jpg','.jpeg','.png'))
                 and x.lower().startswith('source')])
    if not pics:
        problems.append((f, ship, 'no source*.webp images in the saved folder')); continue
    dst=os.path.join(RAW,ship); os.makedirs(dst,exist_ok=True)
    files=[]
    for i,p in enumerate(pics,1):
        ext=os.path.splitext(p)[1].lower()
        out='rsi_%d%s'%(i,ext)
        shutil.copyfile(os.path.join(src,p), os.path.join(dst,out))
        files.append(out)
    man['ships'].append({'ship':ship,'page':'%s - %s | Star Citizen Store'%(ship,maker),
                         'saved':'2026-09-06','files':files,'pick':files[0]})
    added.append((ship,files))

man['ships'].sort(key=lambda e:e['ship'])
json.dump(man, open(RAW+'/manifest.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
for s,fs in added: print('ADDED', s, fs, '(pick defaults to', fs[0]+')')
for f,s,w in problems: print('PROBLEM', f, '->', repr(s), '-', w)
if not added and not problems: print('nothing new')
