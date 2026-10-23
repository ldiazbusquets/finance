"""Proof that the consistency checks catch what they claim to: each test breaks a real, already-built report
in one specific way and expects the checker to object. Run: python3 _source/tests/test_consistency.py (or pytest)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path[:0] = [SRC, os.path.join(SRC, 'pages')]
import consistency as C  # noqa: E402
import holdings  # noqa: E402

ROOT = os.path.dirname(SRC)
AMZN = holdings.R['AMZN']
PAGE = open(os.path.join(ROOT, 'reports', 'amazon.html'), encoding='utf-8').read()


def errs(R=AMZN, page=PAGE):
    return C.check_report(R, page)[0]


def test_clean_report_passes():
    assert errs() == []


def test_all_expected_checks_run():
    ran = C.check_report(AMZN, PAGE)[1]
    assert {'weights', 'field', 'scenario table', 'bridge', 'cash-flow table'} <= ran


def test_wrong_weighted_value():
    assert any('25/50/25' in e for e in errs(dict(AMZN, wt=AMZN['wt'] + 10)))


def test_broken_bridge():
    bad = PAGE.replace('<b class="num">$1.67T</b>', '<b class="num">$1.47T</b>')
    assert bad != PAGE and any('bridge' in e for e in errs(page=bad))


def test_unexplained_second_fcf_figure():
    bad = PAGE.replace('Free cash flow, last 12 months, as Amazon defines it', 'Free cash flow, last 12 months')
    assert bad != PAGE and any('no definition given' in e for e in errs(page=bad))


def test_scenario_table_mismatch():
    assert any('scenario table' in e for e in errs(dict(AMZN, base=AMZN['base'] + 5, wt=round(.25 * AMZN['bear'] + .5 * (AMZN['base'] + 5) + .25 * AMZN['bull']))))


def test_layout_change_cannot_skip_a_check():
    bad = PAGE.replace('<span class="mono">Enterprise value</span>', '<span class="mono">Firm value</span>')
    assert bad != PAGE
    assert any('could not run' in e for e in errs(page=bad))


def test_money_parser():
    assert C.money('$1.02T') == 1.02e12 and C.money('&minus;$35B') == -35e9 and C.money('360M') == 3.6e8 and C.money('$358') == 358


if __name__ == '__main__':
    n = 0
    for k, f in list(globals().items()):
        if k.startswith('test_'):
            f(); n += 1
    print(f'{n} consistency tests passed')
