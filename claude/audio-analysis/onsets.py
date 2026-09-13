import numpy as np
sr=16000
a=np.fromfile('sess.raw',dtype=np.float32)
hop=int(sr*0.05)                      # 50 ms frames
n=len(a)//hop
f=a[:n*hop].reshape(n,hop)
rms=np.sqrt((f.astype(np.float64)**2).mean(1))+1e-12
db=20*np.log10(rms)

# rolling background = 20th percentile over +-4s window
w=int(4/0.05)
bg=np.array([np.percentile(db[max(0,i-w):i+1],20) for i in range(n)])
excess=db-bg

thr=9.0                                # dB above local background
hot=excess>thr
# group into events
ev=[];i=0
while i<n:
    if hot[i]:
        j=i
        while j+1<n and hot[j+1]: j+=1
        seg=slice(i,j+1)
        ev.append((i*0.05,(j+1)*0.05,db[seg].max(),excess[seg].max()))
        i=j+1
    else: i+=1
# merge events closer than 0.4s
m=[]
for e in ev:
    if m and e[0]-m[-1][1]<0.4:
        p=m[-1]; m[-1]=(p[0],e[1],max(p[2],e[2]),max(p[3],e[3]))
    else: m.append(list(e) if False else e)
    m[-1]=tuple(m[-1])
print(f"duration {n*0.05:.1f}s   overall floor(20pct) {np.percentile(db,20):.1f} dB   median {np.median(db):.1f} dB")
print(f"candidate events at >{thr} dB above local background: {len(m)}")
print()
def mmss(t): return f"{int(t//60):02d}:{t%60:05.2f}"
for s,e,pk,ex in m:
    print(f"  {mmss(s)} - {mmss(e)}   len {e-s:5.2f}s   peak {pk:6.1f} dB   +{ex:4.1f} over background")
