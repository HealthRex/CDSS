--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: sim_state; Type: TABLE DATA; Schema: public; Owner: -
--

COPY sim_state (sim_state_id, name, description) FROM stdin;
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
\.


--
-- Name: sim_state_sim_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('sim_state_sim_state_id_seq', 21, true);


--
-- PostgreSQL database dump complete
--

