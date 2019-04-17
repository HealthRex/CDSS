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
-- Data for Name: sim_patient; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_patient (sim_patient_id, name, age_years, gender) FROM stdin;
9	(Template) Chest Pain	62	Male
6	(Template) DLBCL Fever	32	Male
13	(User1) Chest Pain	62	Male
14	(User1) DLBCL Fever	32	Male
15	(User1) Vomiting	57	Male
16	(User1) Diabetic fatigue	26	Female
7	(Template) Black vomit	57	Male
17	(User2) Diabetic fatigue	26	Female
18	(User2) Black vomit	57	Male
19	(User2) Chest Pain	62	Male
20	(User2) DLBCL Fever	32	Male
5	(Template) Hematemesis, Alcohol	59	Male
23	(User3) Hematemesis, Alcohol	59	Male
24	(User3) Chest Pain	62	Male
25	(User3) DLBCL Fever	32	Male
22	(Template) Diabetic fatigue	26	Female
8	(User3) Diabetic fatigue	26	Female
28	(User4) Diabetic Fatigue	26	Female
29	(User4) Chest Pain	62	Male
30	(User4) DLBCL Fever	32	Male
31	(User4) Hematemesis, Alcohol	59	Male
32	(User5) Chest Pain	62	Male
33	(User5) Diabetic Fatigue	26	Female
34	(User5) DLBCL Fever	32	Male
35	(User5) Hematemesis, Alcohol	59	Male
36	(User6) Diabetic fatigue	26	Female
37	(User6) Chest Pain	62	Male
38	(User6) DLBCL Fever	32	Male
39	(User6) Hematemesis, Alcohol	59	Male
50	(Template) Chemo Fever v2	30	Male
48	(Template) Neck Stiffness	25	Female
49	(Template) Palpitations	66	Female
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_sim_patient_id_seq', 60, true);


--
-- PostgreSQL database dump complete
--

