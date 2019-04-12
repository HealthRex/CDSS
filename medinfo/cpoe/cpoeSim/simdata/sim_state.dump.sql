--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.5
-- Dumped by pg_dump version 10.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: sim_state; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_state (sim_state_id, name, description) FROM stdin;
1	Example	Example State
0	Default	Default State Info
5	ACS Relief	ACS Pain Relief
6	NFever	Neutropenic Fever (no source) Initial State
7	GIBleed	GI Bleed Initial State
3	ACS	ACS Initial State
8	AMS UTI 	Altered, UTI
10	AMS HyperNa	Altered, Hypernatremia
11	COPD-PNA	COPD Exacerbation, CAPneumonia
12	VTE-Low Risk PE	Low Risk Pulmonary Embolism
14	EtOH-GIBleed Active	Alcoholic Hepatitis - GI Bleed Active
15	EtOH-GIBleed Bleeding Out	Alcoholic Hepatitis - GI Bleed Bleeding Out
4	CodeBlue	Code Blue / ACLS / Dead / Dying
16	EtOH-GIBleed Coag Stabilized	Alcoholic Hepatitis - GI Bleed Coagulopathy Stabilized
2	EtOH-GIBleed Post-EGD	Alcoholic Hepatitis - GI Bleed EGD Done
17	EtOH-GIBleed GI Consult Block	Alcoholic Hepatitis - GI Bleed GI Consult Block Pending Med Management
13	EtOH-GIBleed Onset	Alcoholic Hepatitis - GI Bleed Onset (pre-admission)
9	DKA Onset	Diabetic Ketoacidosis - Onset
20	DKA Hypoglycemic	Diabetic Ketoacidosis - Low Glucose, Low K, Anion Gap
21	DKA Hyperglycemic	Diabetic Ketoacidosis - High Glucose, Normal-High K, Anion Gap
18	DKA Euglycemic	Diabetic Ketoacidosis - Normal Glucose, Normal K, Anion Gap
19	DKA Gap Closed	Diabetic Ketoacidosis - Gap Closed
5000	Neutropenic Fever v2	Neutropenic Fever (v2 example) Initial State
5001	Neutropenic Fever Treated with Abx	Appropriate antibiotic improve patient condition
5002	Neutropenic Fever Treated with IVF	Appropriate IVF improve patient condition
5003	Neutropenic Fever Treated with IVF + ABX	Appropriate Treatments for patient condition
30	Mening Active	Meningitis Active
31	Meningitis Adequately Treated	Appropriate antibiotic improve patient condition
32	Meningits Inadequately Treated	Inadequate treatment worsens patient condition
33	Meningits Worsens	Patient condition worsens after 1 hr
40	Afib-RVR Active	Afib-RVR Active
41	Afib-RVR Stabilized	Cardioversion improves hemodynamics
42	Afib-RVR Stabilized No Anti-coag	No anticoagulation after cardioversion results in stroke
43	Afib-RVR Critical Post Diuretics	Diuretics worsen hypotension
44	Afib-RVR Critical Post Nodal	Nodal Agents worsen hypotension
45	Afib-RVR Metastable	Amio drip (without bolus) slows heart rate
46	Afib-RVR Stablized Consult	Cardiology consult is ordered
\.


--
-- Name: sim_state_sim_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_state_sim_state_id_seq', 21, true);


--
-- PostgreSQL database dump complete
--

