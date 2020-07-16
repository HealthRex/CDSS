### How the upload of LPCH/SHC was made:
**Notes**:
* Here we talk about copying tables already uploaded to BQ to our local project/dataset (e.g., som-nero* and shc_core/lpch_core).
* Attention was given mostly to times conversion. Other fields may still need to be converted (e.g., integer columns might be represented as string).
* All the time columns are assumed to be in local (Pacific) time.

**PHI elimination**

Drop following columns from the following tables:

* Flowsheet
    * meas_value
* Lab_result
    * ord_value
    * extended_value_comment
    * extended_comp_comment

**Step 1**

First, all of the columns in the table containing dates/times were analyzed to check what times they contain. I.e., if they contain only '00:00:00' times, this column is assumed to be a DATE column, if they contained different times, the it is assumed to be a DATETIME column. And according to our convention, we need to introduce additional _UTC columns for these DATETIME ones. 

Below is an example of a query to check times of a single field in a given table:
```
select extract(time from filing_date_jittered) times, count(*) as cnt
from lpch.clinical_note_meta
group by times
order by cnt desc;
```

If the times were in STRING typed column, the query changed a bit:
```
select extract(time from case when noted_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', noted_date) else null end) times, count(*) as cnt
from starr_datalake2020.shc_diagnosis
group by times
order by cnt desc;
```

**Step 2**

Once the types were determined a `SELECT` query was executed with `EXCEPT()` and time conversion functions to convert the table.
BigQuery allows storing the query results in a table. This functionality was used to store the `SELECT` results in a table. 
This is done by clicking *More* button under the query window (on the same line as *Run* button) and clicking *Query Settings*.
Here, choose *Set a destination table for query results* in *Destination* section and fill in project/dataset/table name to store the results. Also, select *Allow large results (no size limit)* in *Results section*.

Here's an example `SELECT` query:
```
        select * except(end_date, start_date, noted_date, hx_date_of_entry, resolved_date),
        parse_datetime('%Y-%m-%d %H:%M:%S', case when end_date <> '' then end_date else null end) as end_date,
        parse_datetime('%Y-%m-%d %H:%M:%S', case when start_date <> '' then start_date else null end) as start_date,
        extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when noted_date <> '' then noted_date else null end)) as noted_date,
        extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when hx_date_of_entry <> '' then hx_date_of_entry else null end)) as hx_date_of_entry,
        extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when resolved_date <> '' then resolved_date else null end)) as resolved_date,
        timestamp(case when end_date <> '' then end_date else null end, "America/Los_Angeles") as end_date_utc,
        timestamp(case when start_date <> '' then start_date else null end, "America/Los_Angeles") as start_date_utc,
        from starr_datalake2020.shc_diagnosis;
```

**Step 3**

After the conversion, we need to check whether it went as expected. This is done by joining both tables (original and a copy) and comparing converted columns.
Here's an example join:
```
        select o.anon_id, o.line, o.pat_enc_csn_id_jittered, o.dx_id, o.start_date, o.source, o.dept_id,
        o.end_date as o1, o.noted_date as o2, o.hx_date_of_entry as o3, o.resolved_date as o4,
        c.end_date, c.noted_date, c.hx_date_of_entry, c.resolved_date
        from starr_datalake2020.shc_diagnosis o
        join shc_core.diagnosis_code c
        on o.anon_id = c.anon_id and o.line = c.line and o.pat_enc_csn_id_jittered = c.pat_enc_csn_id_jittered and o.dx_id = c.dx_id
        and o.start_date = format_datetime('%Y-%m-%d %H:%M:%S', c.start_date)
        and o.source = c.source
        and o.dept_id = c.dept_id
        where o.end_date <> format_datetime('%Y-%m-%d %H:%M:%S', c.end_date)
        or o.noted_date <> format_date('%Y-%m-%d', c.noted_date)
        or o.hx_date_of_entry <> format_date('%Y-%m-%d', c.hx_date_of_entry)
        or o.resolved_date <> format_date('%Y-%m-%d', c.resolved_date);
```

In the above case, a converted field itself was a part of a unique key, so it is omitted from the check as it is used in the `JOIN` section. That field is checked separately by sorting it in both original and copy tables and ranking the sorted rows to be able to join the tables:
```
        select *
        from (select row_number() over() as o_row, o1.o_start_date, o_cnt
            from (select start_date as o_start_date, count(*) as o_cnt
                from starr_datalake2020.shc_diagnosis
                group by start_date
                order by start_date
            ) o1
        ) o2
        join (select row_number() over() as c_row, c1.start_date, cnt
            from (select start_date, count(*) as cnt
                from shc_core.diagnosis_code
                group by start_date
                order by start_date
            ) c1
        ) c2 on o2.o_row = c2.c_row
        where o2.o_start_date <> format_datetime('%Y-%m-%d %H:%M:%S', c2.start_date);
```

Sometimes, though, the check is simpler:
```
        select o.anon_id,
        o.birth_date_jittered as o1, o.death_date_jittered as o2, o.JITTER_DATE_RECENT_CONF_ENC_JITTER_MINDATE_MAXDATE_ as o3,
        c.birth_date_jittered, c.death_date_jittered, c.recent_conf_enc_jittered
        from starr_datalake2020.shc_demographic o
        join shc_core.demographic c
        using (anon_id)
        where o.birth_date_jittered <> timestamp(c.birth_date_jittered)
        or o.death_date_jittered <> timestamp(c.death_date_jittered)
        or o.JITTER_DATE_RECENT_CONF_ENC_JITTER_MINDATE_MAXDATE_ <> timestamp(c.recent_conf_enc_jittered);
```

If the queries return no rows, the conversion was successful.
