exec(open('val_all.py').read())
P=216.47; SH=24.3e9
def nv(g1=.40,g2=.15,m0=.63,mT=.55,W=None,s2c=2.5,show=False,lab='base'):
    W=W or ke(1.58)
    return dcf(404e9, fade([g1,g2]), ramp(m0,mT,7), .17, lambda t,r,d: d/s2c, W, .03, .25, 0, SH, show, lab)['ps']
b=nv(show=True); bear=nv(.20,.05,.60,.45,W=ke(1.58)+.01); bull=nv(.55,.25,.65,.60,W=ke(1.58)-.01)
print('NVDA base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(W,round(nv(W=W))) for W in [.09,.10,.11,ke(1.58)]])
def solve(f,lo,hi,tgt=P):
  for _ in range(60):
    m=(lo+hi)/2
    if f(m)>tgt: hi=m
    else: lo=m
  return m
print(' implied g1', solve(lambda g: nv(g),-.3,2)); print(' implied mT', solve(lambda m: nv(mT=m,m0=max(.63,m)),0.3,0.95)); print(' implied W', 1/solve(lambda iw: nv(W=1/iw),3,30))
