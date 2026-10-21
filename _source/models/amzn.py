exec(open('val_all.py').read())
P=262.63; SH=10.9e9
W0=wacc(1.33,P*SH,133e9,.05)
def am(g1=.12,g2=.11,m0=.13,mT=.18,W=None,heavy=(130,100,70,50),s2c=2.0,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(810e9, fade([g1,g2]), ramp(m0,mT,5), .19, ri, W, .03, .20, -10e9, SH, show, 'AMZN')
b=am(show=True)['ps']; bear=am(.08,.07,.12,.14,W=W0+.01,heavy=(150,120,90,60))['ps']; bull=am(.15,.14,.14,.22,W=W0-.01,heavy=(110,80,50,30))['ps']
print('AMZN W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(am(W=W)['ps'])) for W in [.085,.09,.095,.10]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied mT', solve(lambda m: am(mT=m)['ps'],0.05,0.6))
print(' implied g', solve(lambda g: am(g,g)['ps'],0,1))
print(' implied W', 1/solve(lambda iw: am(W=1/iw)['ps'],3,30))
