exec(open('val_all.py').read())
# Alphabet: 2026 revenue estimate $490B (first half $229.7B, plus a second half growing as in Q2); 2026 capex guided $195-205B.
# Net cash at June 30 (10-Q): $242.5B cash and marketable securities, less the SpaceX stake ($94.1B, a listed share since the June IPO,
# so it sits in marketable securities: non-marketable securities total only $131.5B), less $98.2B long-term debt = $50.2B.
# Stakes added separately: SpaceX $94.1B and Anthropic about $124.3B = $218B. (Audit, Oct 23 2026: was ~$100B, which counted SpaceX twice.)
P=324.22; SH=12.25e9
STAKES=218.4e9
W0=wacc(1.13,P*SH,70e9,.05)
def gg(g1=.15,g2=.13,m0=.34,mT=.35,W=None,heavy=(150,120,90,60),s2c=2.0,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(490e9, fade([g1,g2]), ramp(m0,mT,4), .17, ri, W, .03, .25, 50.2e9+STAKES, SH, show, 'GOOGL')
b=gg(show=True)['ps']; bear=gg(.09,.07,.31,.30,W=W0+.01,heavy=(180,150,110,80))['ps']; bull=gg(.19,.17,.36,.38,W=W0-.01,heavy=(130,100,70,40))['ps']
print('GOOGL W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(gg(W=W)['ps'])) for W in [.085,.09,.095,.10,.105]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: gg(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: gg(mT=m)['ps'],0.05,0.95))
