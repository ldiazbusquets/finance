exec(open('val_all.py').read())
# Lockheed Martin: 2026 guidance midpoint $81B; segment margin ~10.6% plus the FAS/CAS pension adjustment gives ~11.5% operating
P=590.20; SH=231.5e6
W0=wacc(0.80,P*SH,20.5e9,.05)   # beta 0.80 (defense peers), not the measured 0.48
def lm(g1=.07,g2=.06,m0=.115,mT=.12,W=None,s2c=4,show=False):
    W=W or W0
    return dcf(81.0e9, fade([g1,g2]), ramp(m0,mT,4), .16, lambda t,r,d: d/s2c, W, .03, .15, -14.5e9, SH, show, 'LMT')
b=lm(show=True)['ps']; bear=lm(.04,.03,.10,.105,W=W0+.01)['ps']; bull=lm(.09,.08,.12,.13,W=W0-.01)['ps']
print('LMT W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(lm(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: lm(g,g)['ps'],0,1))
print(' implied mT', solve(lambda m: lm(mT=m)['ps'],0.05,0.5))
