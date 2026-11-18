---
name: data-sanity
description: Check data quality before analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Data Sanity

Works WITH power-core; its output is evidence for task-card criteria. `SKILL` = this folder.

1. Profile first: `python SKILL/scripts/profile_csv.py <file.csv> [--delimiter ,]` prints rows, columns, inferred types,
   missing counts, duplicate rows, numeric min / max / mean / median, and IQR outliers. For .xlsx, export the sheet to CSV first.
2. Read the profile before computing anything. Decide how to treat missing values, duplicates and outliers, and write the
   decision down. Do not silently drop rows.
3. Check units, currencies, date formats and percent vs percentage points. Check that categories are spelled consistently.
4. Order-of-magnitude check each result. Re-derive one headline number a second way (different formula or tool). If they
   disagree, resolve it before reporting.
5. Charts: label axes and units, start bars at zero, state the date range and the filter used.
6. Report: the number, how it was computed, the data caveats, and confidence. Keep the cleaned data and the script so the
   result can be reproduced.

