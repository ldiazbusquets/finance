exec(open('val_all.py').read())
# Microsoft: fiscal 2026 (to June) revenue $331.8B; FY27 capex guided $255-260B including finance leases.
# Net cash $36.5B (cash $76.8B less debt $40.3B, Jun 30) plus ~27% of OpenAI, valued at this site's OpenAI base case ($790B) = $213B (estimate).
P=521.08; SH=7.43e9
OAI=.27*790e9
W0=wacc(1.09,P*SH,40.3e9,.05)
def ms(g1=.17,g2=.15,m0=.45,mT=.45,W=None,heavy=(180,140,100,70),s2c=2.0,oai=OAI,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(331.8e9, fade([g1,g2]), ramp(m0,mT,4), .18, ri, W, .03, .25, 36.5e9+oai, SH, show, 'MSFT')
b=ms(show=True)['ps']; bear=ms(.12,.10,.42,.40,W=W0+.01,heavy=(200,170,130,90))['ps']; bull=ms(.21,.18,.47,.48,W=W0-.01,heavy=(160,110,70,40))['ps']
print('MSFT W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(ms(W=W)['ps'])) for W in [.085,.09,.095,.10,.105]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: ms(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: ms(mT=m)['ps'],0.05,0.95))
