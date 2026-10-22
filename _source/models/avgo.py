exec(open('val_all.py').read())
# Broadcom: fiscal 2026 (to early November) revenue about $106B (first three quarters ~$71B plus Q4 guidance $34.8B) - estimate.
# Management: FY2027 AI revenue ~$115B, FY2028 ~$230B. Operating margin here is after stock pay and amortization of software
# intangibles is excluded (it is not a cash cost), ~55% easing as custom racks carry more memory content.
# Net debt $35.4B (debt $59.4B less cash $24.0B, Aug 2, 2026). 4.89B diluted shares.
P=323.24; SH=4.89e9
W0=wacc(1.30,P*SH,59.4e9,.05)   # beta 1.30 (large-cap chip peers), not the measured 1.86 inflated by the 2026 swings
def av(g1=.55,g2=.25,m0=.55,mT=.50,W=None,s2c=4,show=False):
    W=W or W0
    return dcf(106e9, fade([g1,g2]), ramp(m0,mT,5), .16, lambda t,r,d: d/s2c, W, .03, .25, -35.4e9, SH, show, 'AVGO')
b=av(show=True)['ps']; bear=av(.30,.0,.48,.45,W=W0+.01)['ps']; bull=av(.60,.45,.57,.53,W=W0-.01)['ps']
print('AVGO W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(av(W=W)['ps'])) for W in [.09,.095,.10,.105,.11]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: av(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: av(mT=m)['ps'],0.05,0.95))
