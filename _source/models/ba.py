exec(open('val_all.py').read())
P=190.47; SH=790.6e6
W0=wacc(1.35,P*SH,45.6e9,.06)
def ba(path=(2,6,9,10.5,11.5),gT=.03,W=None,show=False):
    W=W or W0; f=[(x+2.0)*1e9 for x in path]
    g5=.06; gs=[g5+(gT-g5)*i/5 for i in range(1,6)]
    for g in gs: f.append(f[-1]*(1+g))
    pv=sum(x/(1+W)**(t-.5) for t,x in enumerate(f,1)); tv=f[-1]*(1+gT)/(W-gT); pvtv=tv/(1+W)**9.5
    ev=pv+pvtv; eq=ev-25.6e9
    if show: print(f'  W {W:.2%} pv {pv/1e9:.0f} pvtv {pvtv/1e9:.0f} ev {ev/1e9:.0f} eq {eq/1e9:.0f} tv% {pvtv/ev:.0%} y10 fcff {f[-1]/1e9:.1f}')
    return eq/SH
b=ba(show=True); bear=ba((0.5,3,5,6.5,7.5),W=W0+.01); bull=ba((3,8,11,13,14),W=W0-.01)
print('BA base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'P',P)
print(' sens',[(W,round(ba(W=W))) for W in [.08,.085,.09,.095,W0]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
s=solve(lambda k: ba(tuple(x*k for x in (2,6,9,10.5,11.5))),0.1,5); print(' implied scale',s, 'steady fcf', 11.5*s)
