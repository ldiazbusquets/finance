import json
LAST = {}
SH=264.7e6; NETCASH=16.76e9-2.85e9   # Sep 30 2026 balance sheet (cash, debt)
def run(g27=.11,g28=.10,gT=.03,mT=.20,da=.022,s2c=4,W=.107,tax=.21,ronic=.20,m26=.14, show=False):
    rev=47.0e9; rows=[]; pv=0
    gs=[g27,g28]+[g28+(gT-g28)*k/8 for k in range(1,9)]   # 2027..2036
    for t,g in enumerate(gs,1):
        r0=rev; rev*=1+g
        eb=m26+(mT-m26)*min(1,t/2)            # EBITDA margin reaches target in 2028
        ebit=rev*(eb-da); nopat=ebit*(1-tax); reinv=(rev-r0)/s2c; f=nopat-reinv
        d=(1+W)**(t-0.5)                       # mid-year, valued at end of 2026 roughly
        pv+=f/d; rows.append((2026+t,g,rev,eb,ebit,nopat,reinv,f))
    nop11=rows[-1][4]*(1+gT)*(1-tax); tv=nop11*(1-gT/ronic)/(W-gT); pvtv=tv/(1+W)**9.5
    ev=pv+pvtv; eq=ev+NETCASH
    LAST.clear(); LAST.update(W=W, gT=gT, rows=rows, pv=pv, tv=tv, pvtv=pvtv, ev=ev, net=NETCASH, eq=eq, sh=SH, da=da, s2c=s2c, tax=tax, ronic=ronic)
    if show:
        for r in rows: print(r[0], f"g {r[1]:.1%} rev {r[2]/1e9:.1f} ebitda {r[3]:.1%} ebit {r[4]/1e9:.1f} fcf {r[7]/1e9:.1f}")
        print(f"pv10 {pv/1e9:.1f} pvtv {pvtv/1e9:.1f} ev {ev/1e9:.1f} eq {eq/1e9:.1f} tvshare {pvtv/ev:.0%}")
    return eq/SH
base=run(show=True); print('base',round(base))
for W in [.085,.09,.095,.10,.107]: print('W',W, round(run(W=W)))
bear=run(g27=.07,g28=.05,mT=.16,W=.115); bull=run(g27=.16,g28=.14,mT=.23,W=.097); print('bear',round(bear),'bull',round(bull))
print('wt', round(.25*bear+.5*base+.25*bull))
