exec(open('val_all.py').read())
P=694.25; SH=2.566e9
W0=wacc(1.42,P*SH,83.66e9,.05)
def mt(g1=.18,g2=.14,m0=.34,mT=.38,W=None,heavy=(110,90,60,40),s2c=2.0,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(248e9, fade([g1,g2]), ramp(m0,mT,5), .16, ri, W, .03, .25, 6.6e9, SH, show, 'META')
b=mt(show=True)['ps']; bear=mt(.10,.08,.30,.30,W=W0+.01,heavy=(130,110,80,60))['ps']; bull=mt(.24,.18,.36,.44,W=W0-.01,heavy=(90,70,40,25))['ps']
print('META W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(mt(W=W)['ps'])) for W in [.085,.09,.095,.10]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied mT', solve(lambda m: mt(mT=m)['ps'],0.05,0.9))
print(' implied g', solve(lambda g: mt(g,g)['ps'],0,1))
print(' implied W', 1/solve(lambda iw: mt(W=1/iw)['ps'],3,30))
