exec(open('val_all.py').read())
P=335.26; BV=132.30; G=.045
k=ke(1.046)
v=lambda roe,kk: (roe-G)/(kk-G)*BV
b,bear,bull=v(.16,k),v(.145,k+.005),v(.18,k-.005)
print('JPM base',round(b),'bear',round(bear),'bull',round(bull),'wt',round(.25*bear+.5*b+.25*bull),'price',P)
print(' sens',[(kk,round(v(.16,kk))) for kk in [.09,.095,.10,k]])
print(' implied ROE', G+P/BV*(k-G))
