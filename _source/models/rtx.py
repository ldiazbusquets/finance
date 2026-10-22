exec(open('val_all.py').read())
# RTX: 2026 adjusted sales guidance midpoint $97.25B (raised Oct 20, 2026). Adjusted operating margin ~12.5% (segments 15.2% less
# corporate, eliminations and the pension adjustment), rising as the Pratt & Whitney GTF powder-metal costs roll off - estimate.
# Net debt $28.2B (debt $37.4B less cash $9.2B, Sep 30, 2026). 1.368B diluted shares.
P=194.745; SH=1.368e9
W0=wacc(0.80,P*SH,37.4e9,.05)   # beta 0.80 (defense peers); measured 0.81
def rt(g1=.08,g2=.07,m0=.125,mT=.14,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(97.25e9, fade([g1,g2]), ramp(m0,mT,5), .18, lambda t,r,d: d/s2c, W, .03, .15, -28.2e9, SH, show, 'RTX')
b=rt(show=True)['ps']; bear=rt(.04,.04,.115,.12,W=W0+.01)['ps']; bull=rt(.10,.09,.13,.155,W=W0-.01)['ps']
print('RTX W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(rt(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: rt(g,g)['ps'],0,1))
print(' implied mT', solve(lambda m: rt(mT=m)['ps'],0.05,0.5))
