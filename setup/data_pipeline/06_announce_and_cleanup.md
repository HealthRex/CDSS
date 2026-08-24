# Step 6 — Announce & Clean Up

## 1. Slack announcement

Post to `#general`, then `#devops`. Slack uses single asterisks for bold (`*bold*`, not `**bold**`).

Lead with anything that could break existing queries — changed column values, big size changes, removed tables. Those matter more to researchers than the fact that a refresh happened.

Template, from the Aug 2026 refresh:

```
STAAR data refresh — shc_core_2025 / lpch_core_2025 updated

Loaded the FY26 refresh #2 (Clarity data cut: Aug 9, 2026). Both datasets are validated and live.

What's new:
• ~3-5% more data across clinical tables
• SmartData is now unfiltered — smrtdta went 6.2M → 479.6M rows (SHC) and 0 → 102.5M (LPCH). Heads up if you query it without a concept_id filter, you'll scan a lot more than before.
• data_source for LPCH tables is fixed — was incorrectly "CLARITY SHC", now "CLARITY_LPCH". Update any queries filtering on that string.
• New SHC tables: alt_com_action, order_quest

Still pending: deid notes (data team expects end of month).

Backups in copy_shc_core_2025 / copy_lpch_core_2025 for ~2 weeks. Flag anything that looks off.
```

Worth calling out explicitly when relevant:

- **Column value changes** — anything that breaks a `WHERE` clause
- **Large table size changes** — researchers pay for what they scan
- **New or removed tables**
- **Anything still pending** from the data team

## 2. Update the changelog

Add an entry to [`CHANGELOG.md`](./CHANGELOG.md) while it's fresh: data cut date, what the data team changed, tables added/excluded, growth numbers, and any open questions. This is what makes the next refresh faster.

## 3. Reply to the data team

Confirm the load worked and close any open questions from their delivery email. If they asked something the lab didn't answer (like the SmartData element IDs in Aug 2026), say who's following up and by when — otherwise they'll make the decision for you next time.

## 4. Drop backups

Wait 1–2 weeks after announcing. If nobody has reported problems:

```sql
DROP SCHEMA `som-nero-phi-jonc101.copy_shc_core_2025` CASCADE;
DROP SCHEMA `som-nero-phi-jonc101.copy_lpch_core_2025` CASCADE;
```

With refreshes every 4–6 weeks, don't let this slip — stale backups get confusing, and Step 3 drops them anyway at the start of the next run.

## Periodic: old dataset cleanup

Not part of every refresh. Worth doing every year or two.

Find datasets untouched for 3+ years:

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

Then:

1. **Filter manually.** Exclude `shc_core_*`, `lpch_core_*`, `shc_access_log`, `wui_omop*`, `starr_datalake2018`, `wui_datalake`, and anything in active use. Dataset `last_modified_time` reflects metadata changes, not queries — a dataset can look stale while being actively read.
2. **Get PI sign-off** on the filtered list.
3. **Announce** in `#general` and `#devops` with a 2-week claim window.
4. **Delete** unclaimed datasets after the deadline:

```sql
DROP SCHEMA IF EXISTS `som-nero-phi-jonc101.<dataset>` CASCADE;
```

You may lack owner permission on datasets you didn't create — those need the project admin.

5. **Record what was deleted** (date, list, who claimed what) so there's an answer if someone asks months later.

## Onboarding note for new GCP users

Worth sending when someone gets project access:

> Welcome to the lab's GCP project (som-nero-phi-jonc101)! Quick housekeeping note: please create your own dataset (e.g., yourname_db) for any tables you generate or extract, and avoid modifying or deleting anything outside of it — the shc_core_* and lpch_core_* datasets in particular are shared production data.
>
> Let me know if you have any questions getting set up!

Anything involving clinical notes or identifiers belongs in `som-nero-phi-jonc101-secure`, not the working project.
