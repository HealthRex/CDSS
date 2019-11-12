= Dev Workshop =
SQL Queries and Databases

== Learning Goals ==
- Data Tables in Databases in Database Servers
- Querying from Relational Databases with SQL
  - FROM
      - Table Alias
  - SELECT
  - WHERE
      - =, <, >, <>, IN
      - LIKE
      - Date/Time functions
  - ORDER BY
  - LIMIT OFFSET
  - Aggregate Functions (count, sum, min, max, distinct)
  - GROUP BY, HAVING
  - CASE WHEN

  - Subqueries
  - Inner Join, Outer Join

- Bonus Topics to lookup but not covered here:
  - Indexes
  - Explain Queries
  - Insert/Delete/Update
  - ACID transactional properties (atomicity, consistency, isolation, durability)
  - Constraints (unique/primary keys, foreign keys)
  - 3rd Normal Form vs. Denormalized data

- See also 
  https://github.com/HealthRex/CDSS/wiki/STRIDE-Inpatient-SQL-Tutorial for more examples on the STRIDE derived clinical_item tables.   
  medinfo.db.Model.SQLQuery for a convenient Python object to dynamically construct SQL queries in application code.


== Preconditions ==
- Access to run queries on a SQL database, for example, Google BigQuery hosted copy of STARR datalake
- Review basic SQL syntax: https://www.w3schools.com/sql/default.asp

== Workshop Steps ==
- Data Tables in Databases in Database Servers
  A database server can host one or more databases. 
  Usually will be working with one primary database that contains many different 2D tables of data.
  Each table is of fixed width (number of columns/features/covariates), but arbitrary length (number of rows/instances/observations).
  Database Schema and Data Dictionaries ("metadata") define what tables exist, what columns they have, 
    and what data types each column holds (e.g., integer, floating point, string, datetime) .
  Entity-Relationship diagrams depict the relationship of different tables, usually through ID integer keys that reference rows in other tables.
  http://www.sqlitetutorial.net/sqlite-sample-database/
  https://med.stanford.edu/content/dam/sm/researchit/Content/STARR-Data-Synopsis-Jun-2018.pdf

    * Under BigQuery resources, find the database of interest (e.g., starr_datalake2018)
    * Browse through the data tables in the database (e.g., order_med) to see the types of data columns contained 
    (e.g.,  jc_uid = Deidentified unique patient identifier, 
            order_med_id_coded = Primary key for this table, uniquely identifying each individual medication order
            medication_id = Foreign key ID for what type of medication is being ordered, 
            med_description = Text description of what that medication is)

- Querying from Relational Databases with SQL
    Main interaction method with SQL databases is pulling out data with SELECT queries that effectively generate temporary result data tables.

  - FROM - Specify which table(s) of data you want to query from
      - Table Alias - Create an alternative (usually short abbreviation) name for a table to make it easier to reference later
  - SELECT - Specify which columns of the data you want to retrieve. '*' to retrieve all available columns, useful for browsing
  - LIMIT OFFSET - Restrict the number of result rows returned. Useful when browsing through database and don't want millions of results

    * Querying for a sample of medication order data

          SELECT *
          FROM starr_datalake2018.order_med
          LIMIT 100;

    * Query for just some of the most relevant columns information

        SELECT
          jc_uid,   -- Unique patient identifier (Deidentified. Not the "real" MRN, but can be mapped back to real data for specific IRB approved projects)
          pat_enc_csn_id_coded,   -- Unique encounter identifier (e.g., patient in hospital or patient in clinic or patient in laboratory)
          order_med_id_coded,   -- Primary key for this table, uniquely identifying an individual medication order. "Coded" for deidentification (not the original value in EMR).
          order_time_jittered,  -- When the order was place. Deidentification "jitterred" the date by +/- X days. Time of day still correct, and date shift consistent for each patient, allowing for valid relative time comparisons.
          medication_id,
          med_description,
          med_route,  -- Description of how medication administered (by mouth, by injection, etc.)
          hv_discrete_dose, -- Medication dose per administration
          hv_dose_unit, -- Units of dosing information
          freq_name,  -- How often medication to be given
          pharm_class_name -- Description of the broad class of pharmaceutical the medication belongs to. Beware that meds don't have clean relationships with such categories. Usually a many-to-many relationship. (
        FROM
          starr_datalake2018.order_med
        LIMIT 100

  - WHERE - Specify / filter which rows of data you want to retrieve using different logical operators.
      - =, <, >, <=, >=    -- Usual logical operators    
      - IS, IS NOT         -- For checking whether a value is or is not NULL ("NA" / "None"), as technically invalid to say something = null.
      - <>                -- SQL's version of "not equals"
      - IN                 -- Allow for multiple equals options. Handy when trying to match multiple ID keys
      - LIKE                 -- String operator that can match wildcard '%'. Handy for prefix and suffix searches.
      - Date/Time functions

      * Query for all of the medication orders where the description starts with "INSULIN"

        SELECT
          *
        FROM
          starr_datalake2018.order_med
        WHERE
          UPPER(med_description) like 'INSULIN%'
        LIMIT 100
	
	Note the "UPPER" string function applied to the text field to effectively make this a case-insensitive search.

      * And occurs in the inpatient setting (ordering_mode_c = 2)

        SELECT
          *
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 -- Inpatient 
        LIMIT 100

    * And is injected by subcutaneous or intravenous route (med_route_c = 18 or 11)

        SELECT
          *
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 AND -- Inpatient 
          med_route_c IN (18,11) -- Subcutaneous or Intravenous
        LIMIT 100

      * And occurred in the year 2016
        There are many datetime specific functions (e.g., DATEDIFF), but these are often not standardized across SQL implementations
	E.g., Alternative implementation to below could use EXTRACT(YEAR FROM order_time_jittered) = 2016.
	https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions

        SELECT
          *
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 AND -- Inpatient 
          med_route_c IN (18,11) AND -- Subcutaneous or Intravenous
          order_time_jittered >= '2016-01-01' AND order_time_jittered < '2017-01-01'
        LIMIT 100

  - ORDER BY - Sort query results by column values

      * Query for inpatient insulin orders like above for just the following two patients ('JCde49f8','JCd08052'), 
          showing results in chronological order for each patient.

        SELECT
          *
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 AND -- Inpatient 
          med_route_c IN (18,11) AND -- Subcutaneous or Intravenous
          order_time_jittered >= '2016-01-01' and order_time_jittered < '2017-01-01' AND
          jc_uid IN ('JCde49f8','JCd08052')
        ORDER BY 
          jc_uid, order_time_jittered
        LIMIT 100

  - Aggregate Functions (count, sum, min, max, distinct)

      * For the inpatient insulin orders in 2016, query for the total number of orders, number of unique patients, unique encounters (hospitalizations), and the sum of all maximum dose values (max_discrete_dose).

        SELECT
          count(*) as totalOrders, -- Result column renaming/aliasing for convenience
          count(distinct jc_uid) as totalPatients,
          count(distinct pat_enc_csn_id_coded) as totalEncounters,
          sum(max_discrete_dose) sumMaxDoses
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 AND -- Inpatient 
          med_route_c in (18,11) AND -- Subcutaneous or Intravenous
          order_time_jittered >= '2016-01-01' and order_time_jittered < '2017-01-01'
        LIMIT 100

  - GROUP BY, HAVING -- Convenient way to aggregate rows of data into common categories, then easily report summary (aggregate) stats for each

      * Report similar stats for inpatient insulin orders (total orders, patients, encounters) for each month from 2015-2017,
      	but only include months where have at least 700 patients

        SELECT
          EXTRACT(YEAR FROM order_time_jittered) as orderYear,    -- Any column NOT an aggregate function (e.g., count, sum),  
          EXTRACT(MONTH FROM order_time_jittered) as orderMonth,    --    MUST be in GROUP BY expression to make sense
          count(*) as totalOrders,
          count(distinct jc_uid) as totalPatients,
          count(distinct pat_enc_csn_id_coded) as totalEncounters
        FROM
          starr_datalake2018.order_med
        WHERE
          med_description like 'INSULIN%' AND 
          ordering_mode_c = 2 AND -- Inpatient 
          med_route_c in (18,11) AND -- Subcutaneous or Intravenous
          EXTRACT(YEAR FROM order_time_jittered) >= 2015 AND 
          EXTRACT(YEAR FROM order_time_jittered) < 2018
        GROUP BY
          orderYear,
          orderMonth
        HAVING
          totalPatients >= 700
        ORDER BY
          orderYear,
          orderMonth
        LIMIT 100

  - CASE WHEN -- Embed an if/then statement into a query. Can be a convenient way to extract out a "one hot" encoding of categorical data

  	* Count up the total number Male vs. Female patients as well as the most common categories of canonical_race

		SELECT 
		    SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) AS males,
		    SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS females,
		    SUM(CASE WHEN canonical_race LIKE '%Asian%' THEN 1 ELSE 0 END) AS asians,
		    SUM(CASE WHEN canonical_race LIKE '%Black%' THEN 1 ELSE 0 END) AS blacks,    
		    SUM(CASE WHEN canonical_race LIKE '%Pacific%' THEN 1 ELSE 0 END) AS pacific_islanders,
		    SUM(CASE WHEN canonical_race LIKE '%White%' THEN 1 ELSE 0 END) AS whites,
		    SUM(CASE WHEN canonical_race LIKE '%Other%' THEN 1 ELSE 0 END) AS race_other,
		    SUM(CASE WHEN canonical_race LIKE '%Unknown%' THEN 1 ELSE 0 END) AS race_unknown,
		    SUM(CASE WHEN canonical_ethnicity LIKE 'Hispanic%' THEN 1 ELSE 0 END) AS hispanics
		FROM
		    starr_datalake2018.demographic

  - Subqueries -- Can treat the results of a query like a temporary table itself, by wrapping in parantheses, and then querying off that again

  	* Find all of patients who had an encounter of appt_type = 'Anesthesia' on a contact_date of '2016-01-01'

        SELECT DISTINCT jc_uid
        FROM starr_datalake2018.encounter
        WHERE appt_type = 'Anesthesia'
        AND contact_date_jittered = '2016-01-01'

  	* Report the age, in years of the patients who had the above encounters

        SELECT DISTINCT   -- Note need to use distinct, because some patients had multiple encounters. Don't want to report twice
          rit_uid, 
          DATE_DIFF(DATE('2016-01-01'), DATE(birth_date_jittered), YEAR) as ageYears
        FROM starr_datalake2018.demographic
        WHERE rit_uid IN
        (   SELECT DISTINCT jc_uid
            FROM starr_datalake2018.encounter
            WHERE appt_type = 'Anesthesia'
            AND contact_date_jittered = '2016-01-01'
        )
        

  - Inner Join - Subqueries like above where matching by an ID column are almost always incorrect (or at least inefficient).
  		Generally should be joining tables together by some matching criteria (usually a foreign key ID field)

  	* Repeat above, but directly joining on demographic and encounter table
        SELECT DISTINCT
          dem.rit_uid, 
          DATE_DIFF(DATE('2016-01-01'), DATE(dem.birth_date_jittered), YEAR) as ageYears
        FROM
          starr_datalake2018.demographic AS dem JOIN  -- Create a shorthand table alias for convenience when referencing
          starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
        WHERE
          enc.appt_type = 'Anesthesia' AND 
          enc.contact_date_jittered = '2016-01-01'

  - Outer Join - When joining tables, sometimes there is no matching record in the other table. 
  		Default (inner) join behavior is to skip those records then, but then you might lose track of data on the side
  		of the query that does have data. Sometimes want to keep those and just match to "null" on the other side.

    * Find all of the patient demographic records for patients with these IDs
      ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f')

        SELECT *
        FROM starr_datalake2018.demographic
        WHERE rit_uid IN ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f')

    * Find all of the encounters that occurred on 2016-01-01

        SELECT *
        FROM starr_datalake2018.encounter
        WHERE contact_date_jittered = '2016-01-01'

    * For each of the patients in the list above, report how many encounters each had on 2016-01-01.
      To start, just make a query result with one row per patient encounter that matches the above criteria    

        SELECT
          dem.rit_uid, 
          enc.pat_enc_csn_id_coded 
        FROM 
          starr_datalake2018.demographic AS dem JOIN
          starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
        WHERE
           dem.rit_uid IN ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f') AND
           contact_date_jittered = '2016-01-01'
        ORDER BY
          dem.rit_uid;

    * Then apply GROUP BY and row counts to get the summary stats

        SELECT
          dem.rit_uid,
          COUNT(DISTINCT enc.pat_enc_csn_id_coded)
        FROM 
          starr_datalake2018.demographic AS dem JOIN
          starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
        WHERE
           dem.rit_uid IN ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f') AND
           contact_date_jittered = '2016-01-01'
        GROUP BY
          dem.rit_uid
        ORDER BY
          COUNT(DISTINCT enc.pat_enc_csn_id_coded) DESC;

    * Problem with above is that it only shows results for 7 patients (those that had some encounters on 2016-01-01). 
      No results are shown at all for the patients who had no encounters on that date. (Would like to report "0" encounters.)
      Go back to the query for one row per patient encounter and do an outer join to at least fill in "null" value entries
      for the patients who didn't have any specific encounters.

        SELECT
          dem.rit_uid, 
          enc.pat_enc_csn_id_coded 
        FROM 
          starr_datalake2018.demographic AS dem LEFT OUTER JOIN
          starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
        WHERE
           dem.rit_uid IN ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f') AND
           (contact_date_jittered IS NULL OR contact_date_jittered = '2016-01-01')
        ORDER BY
          dem.rit_uid;

    * Now redo aggregate query with outer join so will appropriately count up at least zero records for each patient

        SELECT
          dem.rit_uid,
          COUNT(DISTINCT enc.pat_enc_csn_id_coded)
        FROM 
          starr_datalake2018.demographic AS dem LEFT JOIN
          starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
        WHERE
           dem.rit_uid IN ('JCd9a485','JCdbb0dd','JCcf7fef','JCe48eb5','JCe01809','JCdc9a27','JCd7e138','JCcf3c57','JCe38e82','JCd31c2f') AND
           (contact_date_jittered IS NULL OR contact_date_jittered = '2016-01-01')
        GROUP BY
          dem.rit_uid
        ORDER BY
          COUNT(DISTINCT enc.pat_enc_csn_id_coded) DESC;

- Challenge Queries
  - Top 10 Diagnoses recorded in 2017? In 2018?
  - Top 5 medication routes of administration in Inpatient setting in 2017?
  - What are other medications/drugs are in the same pharmaceutical class as Metoprolol?
  - For Blood Culture (2 Aerobic) results, what were Top 10 bugs grown? How often were they Susceptible to Ceftriaxone? To Ciprofloxacin?
  - What percent of patients had a Glucose By Meter lab_result value >250 at some point in 2017?
  - For each of the patients above, what was the average number of units of Insulin administered to them on any day they received insulin?
    (Look in mar = Medication Administration Record table. For some reason, the dose given is recorded in the "sig" field.)
  - Find all patients who received a tPA infusion (medication_id = 86145) and report the 
  	time the patient presented to the emergency department (adt.effective_time_jittered
  	    (where admit.event_type_c = 1 -- Admission 
         and admit.pat_class_c = '112' -- Emergency Services)
  	time the medication was ordered (order_med.order_time_jittered),
  	time the medication was administered (mar.taken_time_jittered)

  	Use above to estimate the average time between showing up in the emergency department and receiving tPA for those who received it.
