exec(open('val_all.py').read())
# TSMC (ADR TSM, 1 ADR = 5 shares): 2026 revenue about $176B (+44%, company); Q3 operating margin 58.7%; capex $60-64B.
# Net cash about $60B (estimate); 25.93B shares = 5.186B ADR-equivalents.
P=412.35; SH=5.186e9
W0=ke(1.24)
def ts(g1=.25,g2=.20,m0=.57,mT=.54,W=None,s2c=1.3,show=False):
    W=W or W0
    return dcf(176e9, fade([g1,g2]), ramp(m0,mT,5), .16, lambda t,r,d: d/s2c, W, .03, .25, 60e9, SH, show, 'TSM')
b=ts(show=True)['ps']; bear=ts(.12,.08,.52,.48,W=W0+.01)['ps']; bull=ts(.32,.25,.59,.57,W=W0-.01)['ps']
print('TSM W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(ts(W=W)['ps'])) for W in [.095,.10,.105,.11,.115]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: ts(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: ts(mT=m)['ps'],0.05,0.95))
