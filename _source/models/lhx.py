exec(open('val_all.py').read())
P=248.77; SH=187.3e6
W0=wacc(0.80,P*SH,11.0e9,.055)   # beta 0.80 (defense peers), not the measured 0.61
def lh(g1=.075,g2=.075,conv=.146,W=None,gT=.03,show=False):
    W=W or W0
    gs=fade([g1,g2],gT); rev=23.45e9; pv=0; rows=[]
    fc=[3.65e9/25.2e9,3.95e9/27.1e9]  # FCFF/revenue path from guidance, then conv
    for t,g in enumerate(gs,1):
        rev*=1+g; c=conv if t>2 else min(fc[t-1],conv) if conv<fc[t-1] else fc[t-1]
        f=rev*c; pv+=f/(1+W)**(t-.5); rows.append((t,g,rev,f))
    tv=rows[-1][3]*(1+gT)/(W-gT); pvtv=tv/(1+W)**9.5
    ev=pv+pvtv; eq=ev-9.5e9-1.0e9
    if show:
        for r in rows[:3]+rows[-1:]: print(f'  y{r[0]} g {r[1]:.1%} rev {r[2]/1e9:.1f} fcff {r[3]/1e9:.2f}')
        print(f'  pv {pv/1e9:.1f} pvtv {pvtv/1e9:.1f} ev {ev/1e9:.1f} eq {eq/1e9:.1f} tv% {pvtv/ev:.0%}')
    return eq/SH
b=lh(show=True); bear=lh(.04,.03,.125,W=W0+.01); bull=lh(.10,.09,.155,W=W0-.01)
print('LHX W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(lh(W=W))) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied W', 1/solve(lambda iw: lh(W=1/iw),3,30))
print(' implied conv', solve(lambda c: lh(conv=c),0.01,.3))
