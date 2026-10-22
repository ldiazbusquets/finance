exec(open('val_all.py').read())
# General Dynamics: 2026 guidance (July 22, 2026) revenue ~$55.7B, operating margin 10.5%, tax ~17.5%.
# Net debt $3.2B (June 28, 2026). ~272M diluted shares (Q2 net earnings $1.16B / EPS $4.24 = 274M; estimate 272M after buybacks).
P=350.755; SH=272e6
W0=wacc(0.80,P*SH,8.1e9,.05)   # beta 0.80 (defense peers); measured 0.70
def gd(g1=.07,g2=.06,m0=.105,mT=.11,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(55.7e9, fade([g1,g2]), ramp(m0,mT,4), .175, lambda t,r,d: d/s2c, W, .03, .15, -3.2e9, SH, show, 'GD')
b=gd(show=True)['ps']; bear=gd(.04,.03,.10,.10,W=W0+.01)['ps']; bull=gd(.09,.08,.11,.12,W=W0-.01)['ps']
print('GD W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(gd(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: gd(g,g)['ps'],0,1))
print(' implied mT', solve(lambda m: gd(mT=m)['ps'],0.05,0.5))
