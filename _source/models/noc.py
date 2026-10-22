exec(open('val_all.py').read())
# Northrop Grumman: 2026 guidance midpoint $44.0B; 2027 growth 5-7%, higher in 2028; margins up 10-20bp a year
P=552.53; SH=143.0e6
W0=wacc(0.80,P*SH,15.2e9,.05)   # beta 0.80 (defense peers), not the measured 0.50
def nc(g1=.06,g2=.07,m0=.113,mT=.12,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(44.0e9, fade([g1,g2]), ramp(m0,mT,5), .16, lambda t,r,d: d/s2c, W, .03, .15, -11.5e9, SH, show, 'NOC')
b=nc(show=True)['ps']; bear=nc(.03,.03,.105,.105,W=W0+.01)['ps']; bull=nc(.08,.09,.118,.13,W=W0-.01)['ps']
print('NOC W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(nc(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: nc(g,g)['ps'],0,1))
print(' implied mT', solve(lambda m: nc(mT=m)['ps'],0.05,0.5))
