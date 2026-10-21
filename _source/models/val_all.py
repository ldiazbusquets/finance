RF, ERP = .0515, .045
LAST = {}   # the last run's year-by-year detail, for export.py
def ke(b): return RF + b*ERP
def wacc(b, E, D, kd, tax=.21): return E/(E+D)*ke(b) + D/(E+D)*kd*(1-tax)
def fade(gs, gT=.03, n=10):
    """explicit growth list, then straight-line fade to gT by year n"""
    g=list(gs); last=g[-1]; k=n-len(g)
    return g+[last+(gT-last)*i/k for i in range(1,k+1)]
def dcf(rev0, gs, margins, tax, reinv, W, gT, ronic, netcash, shares, show=False, label=''):
    """margins: list (per year) operating margin; reinv: function(t, rev, drev) -> reinvestment"""
    rev=rev0; pv=0; rows=[]
    for t,g in enumerate(gs,1):
        r0=rev; rev*=1+g; m=margins[t-1] if t-1<len(margins) else margins[-1]
        ebit=rev*m; nopat=ebit*(1-tax); ri=reinv(t,rev,rev-r0); f=nopat-ri
        pv+=f/(1+W)**(t-.5); rows.append((t,g,rev,m,ebit,nopat,ri,f))
    n11=rows[-1][4]*(1+gT)*(1-tax); tv=n11*(1-gT/ronic)/(W-gT); pvtv=tv/(1+W)**(len(gs)-.5)
    ev=pv+pvtv; eq=ev+netcash; ps=eq/shares
    if show:
        print(f'--- {label}  W={W:.2%}')
        for r in rows[:4]+rows[-1:]: print(f"  y{r[0]} g {r[1]:.1%} rev {r[2]/1e9:,.0f} m {r[3]:.1%} ebit {r[4]/1e9:,.1f} reinv {r[6]/1e9:,.1f} fcf {r[7]/1e9:,.1f}")
        print(f"  pv {pv/1e9:,.0f} pvtv {pvtv/1e9:,.0f} ev {ev/1e9:,.0f} eq {eq/1e9:,.0f} ps {ps:,.0f} tv% {pvtv/ev:.0%}")
    return dict(ps=ps,pv=pv,pvtv=pvtv,ev=ev,eq=eq,rows=rows)
def ramp(a,b,yrs,n=10): return [a+(b-a)*min(1,t/yrs) for t in range(1,n+1)]
