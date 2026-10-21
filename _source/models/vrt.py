exec(open('val_all.py').read())
P=203.56; SH=393e6
W0=wacc(1.83,P*SH,2.94e9,.055)
def vr(g1=.25,g2=.16,m0=.225,mT=.245,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(14.0e9, fade([g1,g2]), ramp(m0,mT,3), .21, lambda t,r,d: d/s2c, W, .03, .25, -0.13e9, SH, show, 'VRT')
b=vr(show=True)['ps']; bear=vr(.12,.08,.21,.21,W=W0+.01)['ps']; bull=vr(.35,.22,.235,.27,W=W0-.01)['ps']
print('VRT W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(vr(W=W)['ps'])) for W in [.09,.10,.11,.12]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: vr(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: vr(mT=m)['ps'],0.05,0.9))
print(' implied W', 1/solve(lambda iw: vr(W=1/iw)['ps'],3,30))
