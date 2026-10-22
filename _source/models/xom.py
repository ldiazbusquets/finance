exec(open('val_all.py').read())
# ExxonMobil: revenue about $370B over the last year with Brent near $110 in October 2026 after Middle East attacks. Base case assumes prices ease:
# revenue -5% in 2027, flat in 2028, operating margin 13% easing to 12% (2025, at about $69 Brent: 12.6%). Capex about $29B vs depreciation about $24B: net investment $5-6B a year.
# Net debt $31.8B (Jun 30). 4.14B diluted shares. Beta 0.80 floor (measured 0.30).
P=178.19; SH=4.14e9
W0=wacc(0.80,P*SH,42.4e9,.05)
def xm(g1=-.05,g2=0,m0=.13,mT=.12,W=None,heavy=(6,6,5,5),s2c=2,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(370e9, fade([g1,g2]), ramp(m0,mT,3), .30, ri, W, .03, .12, -31.8e9, SH, show, 'xom'.upper())
b=xm(show=True)['ps']; bear=xm(-.15,.0,.11,.10,W=W0+.01)['ps']; bull=xm(.03,.02,.14,.14,W=W0-.01)['ps']
print('xom'.upper(),'W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(xm(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: xm(g,g)['ps'],-.5,1))
print(' implied mT', solve(lambda m: xm(mT=m)['ps'],0.01,0.95))
