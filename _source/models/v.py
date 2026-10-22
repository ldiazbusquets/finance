exec(open('val_all.py').read())
# Visa: fiscal 2026 (to Sep 30) net revenue about $45.0B (estimate: three quarters plus a fourth at ~12% growth). GAAP operating margin ~62%
# including litigation provisions. Net debt $10.0B (debt $23.9B less cash and investments $13.9B, Jun 30). 1.898B diluted class A equivalents.
P=414.26; SH=1.898e9
W0=wacc(0.83,P*SH,23.9e9,.05)
def vi(g1=.11,g2=.10,m0=.62,mT=.63,W=None,heavy=(),s2c=4,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(45.0e9, fade([g1,g2]), ramp(m0,mT,3), .19, ri, W, .03, .40, -10.0e9, SH, show, 'v'.upper())
b=vi(show=True)['ps']; bear=vi(.07,.06,.60,.58,W=W0+.01)['ps']; bull=vi(.13,.12,.63,.66,W=W0-.01)['ps']
print('v'.upper(),'W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(vi(W=W)['ps'])) for W in [.075,.08,.085,.09,.095]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: vi(g,g)['ps'],-.5,1))
print(' implied mT', solve(lambda m: vi(mT=m)['ps'],0.01,0.95))
