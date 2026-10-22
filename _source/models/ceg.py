exec(open('val_all.py').read())
# Constellation Energy: 2026 revenue about $40B with Calpine for a full year (estimate); adjusted EPS guidance $11.50-12.50 (Aug 6, 2026)
# implies EBIT about $6.6B (16.5%). Base EPS growth guided >10% a year over rolling three years. Net debt $24.0B (Jun 30). 360M diluted shares.
# Capex well above depreciation (uprates, new gas units): net investment $2.5B a year to 2028, then growth / 2.
P=255.21; SH=360e6
W0=wacc(1.24,P*SH,24.7e9,.05)
def cg(g1=.05,g2=.07,m0=.165,mT=.19,W=None,heavy=(2.5,2.5,2,2),s2c=2,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(40e9, fade([g1,g2]), ramp(m0,mT,5), .21, ri, W, .03, .12, -24.0e9, SH, show, 'ceg'.upper())
b=cg(show=True)['ps']; bear=cg(.02,.03,.15,.15,heavy=(3,3,2.5,2.5),W=W0+.01)['ps']; bull=cg(.08,.10,.17,.23,heavy=(2.5,2.5,2,2),W=W0-.01)['ps']
print('ceg'.upper(),'W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(cg(W=W)['ps'])) for W in [.085,.09,.095,.10,.105]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: cg(g,g)['ps'],-.5,1))
print(' implied mT', solve(lambda m: cg(mT=m)['ps'],0.01,0.95))
