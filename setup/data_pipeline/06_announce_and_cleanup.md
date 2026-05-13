# Step 6 — Announce & Clean Up

Final step. Get the new data in front of researchers and tidy up.

## 1. Slack announcement

Post to `#general` first, then `#devops`. Slack uses single asterisks for bold (not double — `*bold*` not `**bold**`), and triple backticks for code blocks.

### #general (researcher-friendly)

```
📢 STAAR Data Update — YYYY data is live

1. The YYYY data is now available in `som-nero-phi-jonc101`:
   • shc_core_YYYY (adult)
   • lpch_core_YYYY (pediatric)

Datetime conversions and _utc columns have been applied per the standard process.
shc_core_YYYY-1 and lpch_core_YYYY-1 are unchanged and still available for reproducibility.

Note: a few new tables this year in LPCH: lpch_alt_com_action, lpch_mapped_meds,
lpch_order_quest, mom_baby.

Open to recommendations on the cleanup process, naming conventions, or how we should
handle this going forward — drop thoughts here.
```

### #devops (more technical)

```
STAAR data refresh — som-nero-phi-jonc101

shc_core_YYYY and lpch_core_YYYY are live. _utc columns added per the standard pipeline.
Backups in copy_shc_core_YYYY / copy_lpch_core_YYYY (will drop in ~2 weeks once validated).

New tables in lpch_core_YYYY not present in YYYY-1: lpch_alt_com_action, lpch_mapped_meds,
lpch_order_quest, mom_baby. Excluded from transfer: lpch_myc_mesg (stays in secure project).

Production datasets untouched: shc_core_*, lpch_core_*, shc_access_log, wui_omop*,
starr_datalake2018.
```

## 2. Optional: cleanup announcement for old datasets

If you're also retiring old personal/project datasets (recommended every couple of years), post a separate message after the data update has settled (~1 week later). Include the list of datasets scheduled for deletion and a deadline (typically 2 weeks).

Run this to find candidate datasets — anything not modified in 3+ years:

```sql
SELECT
  schema_name AS dataset_name,
  creation_time,
  last_modified_time,
  ROUND(DATE_DIFF(CURRENT_DATE(), DATE(last_modified_time), DAY) / 365.0, 1) AS years_since_modified
FROM `som-nero-phi-jonc101.INFORMATION_SCHEMA.SCHEMATA`
WHERE DATE(last_modified_time) < DATE_SUB(CURRENT_DATE(), INTERVAL 3 YEAR)
ORDER BY last_modified_time;
```

Manually filter the result before announcing:

- **Exclude from cleanup:** `shc_core_*`, `lpch_core_*`, `shc_access_log`, `wui_omop*`, `starr_datalake2018`, `wui_datalake`, and anything else in active research use
- **Get PI sign-off** on the filtered list before posting
- **Allow 2 weeks** for people to claim datasets they still want
- **Document deletions** somewhere (Notion page or markdown file) so you have a record

## 3. Drop backups after validation

Wait at least 1–2 weeks after announcing the new data. If no researchers have flagged issues:

```sql
DROP SCHEMA `som-nero-phi-jonc101.copy_shc_core_YYYY` CASCADE;
DROP SCHEMA `som-nero-phi-jonc101.copy_lpch_core_YYYY` CASCADE;
```

BigQuery's 7-day time-travel provides an additional fallback even after dropping backups.

## 4. Document this year's update

Before closing out, note any changes for next year's run:

- New tables added or removed compared to last year
- Any schema drift you had to work around
- Any tables in the source that aren't in this year's dataset (and why)
- Any tables in this year's dataset carried forward from the prior year (like `zip`)

Add these notes to the README or as a CHANGELOG entry in this folder. Next year's runner will thank you.

## You're done

The annual update is complete. Researchers can use the new `shc_core_YYYY` and `lpch_core_YYYY` datasets immediately.
