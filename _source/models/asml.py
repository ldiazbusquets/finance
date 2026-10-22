exec(open('val_all.py').read())
# ASML: 2026 guidance midpoint EUR 44.5B, converted at $1.123 per euro = $50.0B; net cash about EUR 9B = $10B; one ADR = one share
FX=1.123; P=1558.26; SH=383.1e6
W0=ke(1.30)
def asm(g1=.22,g2=.15,m0=.415,mT=.44,W=None,s2c=3,show=False):
    W=W or W0
    return dcf(44.5e9*FX, fade([g1,g2]), ramp(m0,mT,3), .16, lambda t,r,d: d/s2c, W, .03, .30, 9.0e9*FX, SH, show, 'ASML')
b=asm(show=True)['ps']; bear=asm(.08,.05,.36,.36,W=W0+.01)['ps']; bull=asm(.30,.20,.43,.47,W=W0-.01)['ps']
print('ASML W',round(W0,4),'base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(asm(W=W)['ps'])) for W in [.095,.10,.105,.11,.115]])
def solve(f,lo,hi,tgt=None):
  tgt=tgt or P
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g', solve(lambda g: asm(g,g)['ps'],0,2))
print(' implied mT', solve(lambda m: asm(mT=m)['ps'],0.1,0.9))
