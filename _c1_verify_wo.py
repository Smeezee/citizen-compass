import json,glob,os,collections,sys
SC=r"/sessions/rcw-013myycj7uev5hz6gm3pxwvb/mnt/citizen-compass/data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z"
UEX=r"/sessions/rcw-013myycj7uev5hz6gm3pxwvb/mnt/citizen-compass/data-layer/external-sources/uexcorp/snapshots/20260801T235530Z"
L=lambda p: json.load(open(p,encoding='utf-8'))
out=[]
def say(s): out.append(s); print(s,flush=True)

for f,claim in (("fps-items.json",5182),("ship-items.json",2598)):
    n=sum(1 for r in L(os.path.join(SC,f))
          if ((r.get("stdItem") or {}).get("DescriptionText") or (r.get("stdItem") or {}).get("Description") or "").strip())
    say(f"{f:18} records with text: {n:6}  claimed {claim:6}  {'OK' if n==claim else 'MISMATCH'}")

src={}; nbp=0
for p in glob.glob(os.path.join(SC,"contracts","*.json")):
    raw=open(p,encoding='utf-8',errors='ignore').read()
    if '"PoolUUID"' not in raw: continue
    c=json.loads(raw); pools=c.get("Blueprints") or []
    if not pools: continue
    nbp+=1
    for pool in pools:
        for e in (pool.get("PoolContents") or []):
            b=e.get("BlueprintUUID")
            if b: src.setdefault(b,[]).append(pool.get("Chance"))
say(f"contracts with Blueprints[] : {nbp:6}  claimed    768  {'OK' if nbp==768 else 'MISMATCH'}")
say(f"blueprints with a contract  : {len(src):6}  claimed    676  {'OK' if len(src)==676 else 'MISMATCH'}")
mx=max(len(v) for v in src.values())
say(f"max sources on one blueprint: {mx:6}  claimed    127  {'OK' if mx==127 else 'MISMATCH'}")

bps=L(os.path.join(SC,"blueprints.json")); keys={b.get("Key") for b in bps}
def flatten(node,acc,g=None):
    k=node.get("Kind")
    if k=="group": g=node.get("Name")
    if k in ("resource","item"):
        acc.append({"kind":k,"name":node.get("Name"),"q":node.get("QuantityScu"),"mq":node.get("MinQuality")})
    for c in (node.get("Children") or []): flatten(c,acc,g)
kinds=collections.Counter(); leaves=[]; inv=collections.defaultdict(set); outs=collections.Counter(); nullout=0
for b in bps:
    tier=(b.get("Tiers") or [{}])[0]; req=tier.get("Requirements") or {}
    av=b.get("Availability") or {}; pk=[p.get("Key") or "" for p in (av.get("RewardPools") or [])]
    ing=[]; flatten(req,ing); leaves+=ing
    u=b["UUID"]
    if av.get("Default"): k="default"
    elif u in src: k="contract"
    elif any("Xenothreat" in x or "RedWind" in x for x in pk): k="event"
    elif any(x.startswith("BP_REWARD_") and "BP_CRAFT_"+x[10:] in keys for x in pk): k="direct_reward"
    elif pk: k="other_pool"
    else: k="none"
    kinds[k]+=1
    for i in ing: inv[i["name"]].add(u)
    o=b.get("Output") or {}
    if o.get("UUID"): outs[o["UUID"]]+=1
    else: nullout+=1
say(f"source_kind : {dict(kinds)}")
say(f"  claimed   : {{'none': 865, 'contract': 676, 'event': 31, 'direct_reward': 16, 'default': 8, 'other_pool': 1}}")
say(f"ingredient leaves           : {len(leaves):6}  claimed   4274  {'OK' if len(leaves)==4274 else 'MISMATCH'}")
say(f"  leaves with no QuantityScu: {sum(1 for i in leaves if i['q'] is None):6}  claimed    298")
say(f"  all of those are 'item'   : {all(i['kind']=='item' for i in leaves if i['q'] is None)}")
say(f"  every leaf has MinQuality : {all(i['mq'] is not None for i in leaves)}")
say(f"distinct ingredients        : {len(inv):6}  claimed     37  {'OK' if len(inv)==37 else 'MISMATCH'}")
top=sorted(inv.items(),key=lambda kv:-len(kv[1]))[0]
say(f"top ingredient              : {top[0]} -> {len(top[1])}  claimed Aslarite -> 856")
say(f"distinct outputs            : {len(outs):6}  claimed   1588")
say(f"  outputs made by >1 bp     : {sum(1 for v in outs.values() if v>1):6}  claimed      3")
say(f"  blueprints with null output: {nullout:5}  claimed      6")
open("/sessions/rcw-013myycj7uev5hz6gm3pxwvb/mnt/citizen-compass/_c1_verify_out.txt","w",encoding="utf-8").write("\n".join(out))
