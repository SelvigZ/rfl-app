# RFL Tracker App Change Request

**Project context:**  
This app tracks daily RFL/cut progress using weight and waist measurements. It currently has a main dashboard, a daily tracker, and an insights section with a graph showing weight and waist over time.

**Purpose of this document:**  
Use this as the implementation brief for Codex. The goal is to improve trend visibility, reduce graph scaling issues, and add a few useful dashboard/insight metrics using the current data set.

---

## 1. Add a Graph to the Insights Section

### Current behavior
The app already has a graph/trend visualization in the daily tracker area.

### Requested change
Add a similar graph to the **Insights** section.

### Requirements
- The Insights graph should use the same underlying daily data as the daily tracker graph.
- It should show:
  - Weight over time
  - Waist over time
- Date should be on the x-axis.
- Weight and waist should be visually distinguishable.
- Keep the styling consistent with the existing app theme.

### Acceptance criteria
- The Insights page includes a graph that renders without breaking the current daily tracker graph.
- The graph updates when new daily entries are added.
- The graph handles missing waist or weight values gracefully.

---

## 2. Add Trendlines for Weight and Waist

### Requested change
Add trendlines to both graphs:
1. Daily tracker graph
2. Insights graph

### Requirements
Each graph should include:
- Raw weight line
- Raw waist line
- Weight trendline
- Waist trendline

### Preferred trendline behavior
Use a rolling average if simple and stable.

Suggested options:
- 3-day rolling average for short-term smoothing
- 7-day rolling average for better trend clarity

Recommendation:
- Use a **7-day rolling average** if there are enough data points.
- If fewer than 7 entries exist, use the available entries or hide the trendline until enough data exists.

### Acceptance criteria
- Weight trendline displays correctly.
- Waist trendline displays correctly.
- Trendlines do not interfere visually with the raw data lines.
- Trendlines should be labeled or visually differentiated.

---

## 3. Improve Graph Scaling So Weight and Waist Lines Do Not Stack on Top of Each Other

### Current issue
Weight and waist are plotted together, but the scaling sometimes causes the two lines to visually overlap or stack on top of each other. This happened after both values dropped in a similar relative pattern. Even though weight and waist use different units, the chart visually placed them too close together.

### Requested change
Improve graph scaling so weight and waist remain readable and do not sit directly on top of each other.

### Possible implementation approaches
Codex should choose the most stable/simple approach based on the current chart library.

#### Option A — Separate y-axes
Use two y-axes:
- Left y-axis: Weight in pounds
- Right y-axis: Waist in inches

This may already exist, but the domains/ranges may need better padding.

#### Option B — Normalize values for plotting
Plot both values as percent change from start:
- Weight percent change from starting weight
- Waist percent change from starting waist

This would make the visual trend comparison cleaner, but the graph should still show actual values in tooltips/labels.

#### Option C — Add vertical offset or independent domains
Keep actual values but force the chart domains to separate enough visually that the lines do not overlap.

### Preferred solution
Use **separate y-axes with better domain padding** first if that is clean with the current chart library.

Suggested behavior:
- Weight y-axis domain should be based on min/max weight with padding.
- Waist y-axis domain should be based on min/max waist with padding.
- Padding should prevent the two lines from visually stacking when possible.
- Tooltips should still show actual weight and waist values.

### Acceptance criteria
- Weight and waist lines are readable throughout the data range.
- Lines do not repeatedly stack directly on top of each other.
- Axis labels clearly show units:
  - Weight (lbs)
  - Waist (in)
- Tooltips or selected-date cards still display actual values.

---

## 4. Add Start Weight and Start Waist to the Main Dashboard

### Current behavior
The Insights page shows:
- Start date
- Weight today
- Waist today
- Weight change
- Waist change

### Requested change
Add **Start Weight** and **Start Waist** to the main dashboard in a similar style.

### Requirements
Main dashboard should show:
- Start date
- Start weight
- Start waist
- Current weight
- Current waist
- Weight change
- Waist change

### Display preference
Use the same card/tile style already used in the Insights section so the app feels consistent.

### Acceptance criteria
- Start weight displays on the main dashboard.
- Start waist displays on the main dashboard.
- Values are pulled from the first entry in the current tracking period/start date logic.
- Dashboard layout remains clean on iPhone screen sizes.

---

## 5. Time Zone Handling

### Current concern
The app date/time behavior may not reflect the phone’s local time.

### Requested change
Preferred behavior:
- Use the phone/device local time zone automatically.

### Important note
If automatic device-local time zone handling is complex, fragile, or likely to introduce bugs, then use a simpler fixed time zone approach for now.

### Fallback behavior
- Use Pacific Time / PST/PDT for now.
- Later, when moving to Japan, update the app to Japan time if needed.

### Implementation guidance
Preferred:
- Use browser/device local time zone via JavaScript date/time APIs.
- Avoid server-side UTC date rollover bugs that could cause entries to appear on the wrong day.

Fallback:
- Hardcode America/Los_Angeles for now if needed.

### Acceptance criteria
- Daily entries align with the user’s local calendar day.
- App does not accidentally create/log entries under the wrong date because of UTC conversion.
- If device-local time is used, document where/how it is handled in the code.

---

## 6. Suggested Additional Insights/Metrics Using Current Data

These are optional but would be useful if they are easy to add.

### A. 7-day average weight
Shows smoother weight trend and reduces noise from sodium, glycogen, refeed days, and gut content.

**Display idea:**  
“7-day average weight: ___ lbs”

### B. 7-day average waist
Useful because waist can also be noisy day-to-day.

**Display idea:**  
“7-day average waist: ___ in”

### C. Total weight lost
Already effectively shown as weight change, but could be highlighted as a key metric.

**Display idea:**  
“Total weight lost: ___ lbs”

### D. Total waist lost
Already effectively shown as waist change, but could be highlighted.

**Display idea:**  
“Total waist lost: ___ in”

### E. Average daily weight change
Useful but should be clearly labeled as trend-based, not a prediction.

**Display idea:**  
“Average daily weight change: ___ lbs/day”

### F. Average weekly weight change
More intuitive than daily rate.

**Display idea:**  
“Average weekly weight change: ___ lbs/week”

### G. Average weekly waist change
Useful for fat-loss tracking.

**Display idea:**  
“Average weekly waist change: ___ in/week”

### H. Lowest recorded weight
Helpful but should not be overemphasized.

**Display idea:**  
“Lowest weight: ___ lbs on ___”

### I. Lowest recorded waist
Helpful for tracking best/current leanness.

**Display idea:**  
“Lowest waist: ___ in on ___”

### J. Refeed rebound flag or note
If weight jumps after a refeed day, the app could show a simple note:
“Recent increase may reflect water/glycogen/gut content. Check 3–5 day trend.”

This is optional and does not need to be fancy.

---

## 7. Priority List

### High priority
1. Add trendlines to weight and waist graphs.
2. Fix graph scaling/overlap issue.
3. Add start weight and start waist to main dashboard.
4. Improve date/time zone handling.

### Medium priority
1. Add Insights graph if it is not already present.
2. Add 7-day average weight and waist.

### Low priority / optional
1. Weekly rate of change metrics.
2. Lowest recorded weight/waist.
3. Refeed rebound note.

---

## 8. Implementation Caution

Avoid large rewrites if possible.

The goal is to improve the current working app, not rebuild it. Prefer small, stable changes that are easy to test and revert.

Before making changes:
- Identify the chart component/library being used.
- Identify where the daily weight/waist data is stored and transformed.
- Identify how the app determines “today.”
- Identify how the start date/start values are currently derived.

After making changes:
- Test on mobile screen sizes.
- Test with at least 10–14 entries.
- Test with missing waist or weight data.
- Test a same-day entry around late evening to make sure time zone/date handling works correctly.

---

## 9. Short Version for Codex

Please update the RFL tracker app with the following:

1. Add an Insights graph similar to the daily tracker graph.
2. Add weight and waist trendlines to both graphs.
3. Fix graph scaling so weight and waist lines do not visually stack or overlap too closely.
4. Add start weight and start waist to the main dashboard.
5. Make the app use phone/device local time if stable; otherwise use America/Los_Angeles as a fallback.
6. Optional: add 7-day average weight/waist, weekly rate of change, lowest recorded weight/waist, and refeed rebound notes.

Prioritize stable, minimal changes over a full rewrite.
