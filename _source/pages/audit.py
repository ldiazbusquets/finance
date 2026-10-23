"""Reports checked by hand against the company's own filings: slug -> (date, figures checked, result).
The full log, with sources, is on the About page (about.html#audit)."""
DONE = {
    'nvidia': ('October 23, 2026', 10, 'All match'),
    'amazon': ('October 23, 2026', 13, 'All match; two figures clarified'),
    'jpmorgan': ('October 23, 2026', 16, 'All match'),
    'l3harris': ('October 23, 2026', 12, 'One correction (the dividend), which does not enter the valuation'),
    'exxonmobil': ('October 23, 2026', 11, 'All match'),
    'alphabet': ('October 23, 2026', 17, 'One correction (net cash counted the SpaceX stake twice; value $249 to $245, rating unchanged)'),
    'meta': ('October 23, 2026', 16, 'All match; one date clarified'),
    'microsoft': ('October 23, 2026', 12, 'All match'),
    'broadcom': ('October 23, 2026', 12, 'All match'),
    'visa': ('October 23, 2026', 11, 'All match'),
    'unitedhealth': ('October 23, 2026', 13, 'All match'),
    'johnson-johnson': ('October 23, 2026', 9, 'All match'),
    'rtx': ('October 23, 2026', 14, 'All match; one term clarified'),
    'lockheed-martin': ('October 23, 2026', 11, 'All match'),
    'general-dynamics': ('October 23, 2026', 8, 'All match'),
}
