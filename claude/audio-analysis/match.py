import numpy as np
sr=16000
a=np.fromfile('sess.raw',dtype=np.float32).astype(np.float64)
hop=int(sr*0.05); n=len(a)//hop
f=a[:n*hop].reshape(n,hop)
rms=np.sqrt((f**2).mean(1))+1e-12; db=20*np.log10(rms)
w=int(4/0.05)
bg=np.array([np.percentile(db[max(0,i-w):i+1],20) for i in range(n)])
hot=(db-bg)>9.0
ev=[];i=0
while i<n:
    if hot[i]:
        j=i
        while j+1<n and hot[j+1]: j+=1
        ev.append((i*0.05,(j+1)*0.05)); i=j+1
    else: i+=1
m=[]
for e in ev:
    if m and e[0]-m[-1][1]<0.4: m[-1]=(m[-1][0],e[1])
    else: m.append(e)

# fingerprint: log-magnitude spectrum of first 0.5s of the event, 32 log-spaced bands, energy-normalised
def fp(t0):
    s=int(t0*sr); seg=a[s:s+int(0.5*sr)]
    if len(seg)<int(0.5*sr): return None
    seg=seg*np.hanning(len(seg))
    S=np.abs(np.fft.rfft(seg)); fr=np.fft.rfftfreq(len(seg),1/sr)
    edges=np.logspace(np.log10(80),np.log10(7500),33)
    b=np.array([S[(fr>=edges[k])&(fr<edges[k+1])].sum() for k in range(32)])+1e-12
    b=np.log(b); b=(b-b.mean())/(b.std()+1e-9)
    return b
F=[(t0,t1,fp(t0)) for t0,t1 in m]
F=[x for x in F if x[2] is not None]
def mmss(t): return f"{int(t//60):02d}:{t%60:05.2f}"
print(f"{len(F)} events fingerprinted (first 0.5s, 32 log bands, normalised)\n")
pairs=[]
for i in range(len(F)):
    for j in range(i+1,len(F)):
        c=float(np.dot(F[i][2],F[j][2])/32)
        pairs.append((c,F[i][0],F[j][0]))
pairs.sort(reverse=True)
print("TOP MATCHING PAIRS (1.00 = identical spectrum shape)")
for c,t1,t2 in pairs[:14]:
    print(f"  {c:5.3f}   {mmss(t1)}  <->  {mmss(t2)}    gap {abs(t2-t1):7.1f}s")
print("\nLEAST SIMILAR, for contrast")
for c,t1,t2 in pairs[-4:]:
    print(f"  {c:5.3f}   {mmss(t1)}  <->  {mmss(t2)}")
cs=np.array([p[0] for p in pairs])
print(f"\nall {len(pairs)} pairs: median {np.median(cs):.3f}  mean {cs.mean():.3f}  90th pct {np.percentile(cs,90):.3f}  max {cs.max():.3f}")
