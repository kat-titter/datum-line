"""What data is worth, and why cell data does not convert between labs: public figures, not results.

Nothing here is computed. Every number is quoted from the source in REFS, which continues the numbering
of the references in the README ([1] to [9]), and was checked against that source on 15 October 2026.
Slide 06 (first view), board A23 and the product vision read from this one list.
"""

REFS = {
    10: 'TechCrunch. Mercor quintuples valuation to $10B with $350M Series C. 27 October 2025.',
    11: 'Recursion. Recursion reports third quarter 2025 financial results and provides business update. Press release, 5 November 2025.',
    12: 'Jungco K. Google, Meta join $1.8B push to build AI &#8220;virtual cells&#8221;: here&#8217;s what we know. eWeek, 9 October 2026.',
    13: 'Wolff C, &#8230;, Schmied C. Morphological profiling data resource enables prediction of chemical compound properties. <em>iScience</em> 28(5):112445, 2025.',
}

# what data sells for: (big number, what it is, reference)
PRICES = [
    ('$1.5M a day', 'paid to experts for AI training data, by one vendor', 10),
    ('$30M', 'one cell dataset &#183; paid by Roche', 11),
    ('$1.8B', 'pledged for virtual-cell data; funders get a year first', 12),
]

# the short line under each price on board A23, from the same sources as DEALS
DETAIL = ['~$85 an hour &#183; $10B valuation', 'second milestone &#183; $213M to date', 'Meta, DeepMind, Isomorphic: $300M']

# EU-OPENSCREEN: one Cell Painting protocol at four sites, with cells, serum and dye lots supplied centrally [13]
SITES = {
    'n_sites': 4,
    'line': 'Hep G2',
    'supplied': 'cells, serum and dye lots',
    'within': (84, 94),          # percent replicating, within a site
    'across': (54, 68),          # percent pairing, across sites
    'quote': 'not directly comparable between imaging sites',
    'cause': 'differences in cell culture as well as staining',
    'ref': 13,
}

# the longer form, for the board and the documents
DEALS = [
    ('AI training data', 'One vendor pays its experts more than $1.5M a day, about $85 an hour on average, at a $10B valuation.', 10),
    ('Cell maps', 'Roche and Genentech paid Recursion a second $30M milestone for an accepted whole-genome map of microglial immune cells; $213M from the partnership to date.', 11),
    ('Consortia', 'A $1.8B virtual-cell data initiative, part new money and part existing funding; Meta, Google DeepMind and Isomorphic put in $300M together '
                  'and get a year of exclusive access first.', 12),
]
