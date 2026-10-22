exec(open('val_all.py').read())
# Caterpillar: 2025 revenue $67.6B; 2026 guided up mid-to-high teens (~$78B); MP&E net debt $5.0B (Cat Financial's debt is funded by its loan book)
P=703.84; SH=462.5e6
W0=wacc(1.05,P*SH,11.0e9,.05)
def ct(g1=.08,g2=.06,m0=.20,mT=.21,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(78.0e9, fade([g1,g2]), ramp(m0,mT,4), .22, lambda t,r,d: d/s2c, W, .03, .20, -5.0e9, SH, show, 'CAT')
b=ct(show=True)['ps']; bear=ct(.0,.02,.17,.17,W=W0+.01)['ps']; bull=ct(.12,.10,.215,.23,W=W0-.01)['ps']
print('CAT W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(ct(W=W)['ps'])) for W in [.085,.09,.095,.10,.105]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: ct(g,g)['ps'],0,1))
print(' implied mT', solve(lambda m: ct(mT=m)['ps'],0.05,0.9))
