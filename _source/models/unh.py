exec(open('val_all.py').read())
# UnitedHealth: 2026 revenue about $450B; adjusted EPS at least $20.50 (Oct 13, 2026) implies an operating margin near 5.5%.
# Margins recover toward 7% (historic 8-9%) as Medicare Advantage and Medicaid repricing works through. Net debt $45.8B (debt $74.3B less cash and
# short-term investments $28.5B, Sep 30). 902M diluted shares. Beta 0.80 floor (measured 0.61).
P=425.06; SH=902e6
W0=wacc(0.80,P*SH,74.3e9,.05)
def uh(g1=.04,g2=.07,m0=.055,mT=.07,W=None,heavy=(),s2c=6,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(450e9, fade([g1,g2]), ramp(m0,mT,5), .23, ri, W, .03, .20, -45.8e9, SH, show, 'unh'.upper())
b=uh(show=True)['ps']; bear=uh(.02,.04,.05,.055,W=W0+.01)['ps']; bull=uh(.06,.09,.06,.08,W=W0-.01)['ps']
print('unh'.upper(),'W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(uh(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: uh(g,g)['ps'],-.5,1))
print(' implied mT', solve(lambda m: uh(mT=m)['ps'],0.01,0.95))
