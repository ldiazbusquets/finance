exec(open('val_all.py').read())
# Johnson & Johnson: 2026 sales guidance midpoint $101.2B (Oct 13, 2026). Operating margin 31% (adjusted, less amortization; estimate).
# Net debt $27.4B (Sep 27) plus the proposed $5.5B talc settlement = $32.9B. 2.45B diluted shares. Beta 0.80 floor (measured 0.33).
# Reinvestment includes acquisitions: $1 for every $2 of new sales.
P=267.68; SH=2.45e9
W0=wacc(0.80,P*SH,44.65e9,.05)
def jj(g1=.05,g2=.06,m0=.31,mT=.32,W=None,heavy=(),s2c=2,show=False):
    W=W or W0
    def ri(t,r,d): return heavy[t-1]*1e9 if t<=len(heavy) else d/s2c
    return dcf(101.2e9, fade([g1,g2]), ramp(m0,mT,4), .17, ri, W, .03, .15, -32.9e9, SH, show, 'jnj'.upper())
b=jj(show=True)['ps']; bear=jj(.02,.03,.28,.28,W=W0+.01)['ps']; bull=jj(.07,.08,.32,.34,W=W0-.01)['ps']
print('jnj'.upper(),'W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(jj(W=W)['ps'])) for W in [.07,.075,.08,.085,.09]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: jj(g,g)['ps'],-.5,1))
print(' implied mT', solve(lambda m: jj(mT=m)['ps'],0.01,0.95))
