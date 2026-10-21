exec(open('val_all.py').read())
P=135.79
def ddm(g=.08,yrs=5,gT=.035,k=None,d0=3.58,show=False):
    k=k or ke(0.70); d=d0; pv=0; gs=[g]*yrs+[g+(gT-g)*i/(10-yrs) for i in range(1,11-yrs)]
    for t,gg in enumerate(gs,1):
        d*=1+gg; pv+=d/(1+k)**t
    tv=d*(1+gT)/(k-gT); v=pv+tv/(1+k)**10
    if show: print(f'  k {k:.2%} pvdiv {pv:.1f} pvtv {tv/(1+k)**10:.1f} value {v:.1f}')
    return v
b=ddm(show=True); bear=ddm(.06,gT=.03,k=ke(.7)+.01); bull=ddm(.09,gT=.04,k=ke(.7)-.005)
print('AWK base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'P',P,'ke',ke(.7))
print(' sens', [(k,round(ddm(k=k))) for k in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied k', 1/solve(lambda ik: ddm(k=1/ik),5,30))
print(' implied gT', solve(lambda g: ddm(gT=g),0,.07))
