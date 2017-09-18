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
-- Data for Name: sim_patient; Type: TABLE DATA; Schema: public; Owner: -
--

COPY sim_patient (sim_patient_id, age_years, gender, name) FROM stdin;
9	62	Male	(Template) Chest Pain
6	32	Male	(Template) DLBCL Fever
13	62	Male	(User1) Chest Pain
14	32	Male	(User1) DLBCL Fever
15	57	Male	(User1) Vomiting
16	26	Female	(User1) Diabetic fatigue
2	37	Male	XXX
1	45	Female	XXX
3	75	Male	XXX
4	51	Male	XXX
11	45	Female	XXX
12	62	Male	XXX/HalfUsed
7	57	Male	(Template) Black vomit
17	26	Female	(User2) Diabetic fatigue
18	57	Male	(User2) Black vomit
19	62	Male	(User2) Chest Pain
20	32	Male	(User2) DLBCL Fever
5	59	Male	(Template) Hematemesis, Alcohol
21	59	Male	TestStates
23	59	Male	(User3) Hematemesis, Alcohol
24	62	Male	(User3) Chest Pain
25	32	Male	(User3) DLBCL Fever
26	26	Female	(Test) Diabetc
22	26	Female	(Template) Diabetic fatigue
8	26	Female	(User3) Diabetic fatigue
27	59	Male	TestFFP
28	26	Female	(User4) Diabetic Fatigue
29	62	Male	(User4) Chest Pain
30	32	Male	(User4) DLBCL Fever
31	59	Male	(User4) Hematemesis, Alcohol
32	62	Male	(User5) Chest Pain
33	26	Female	(User5) Diabetic Fatigue
34	32	Male	(User5) DLBCL Fever
35	59	Male	(User5) Hematemesis, Alcohol
36	26	Female	(User6) Diabetic fatigue
37	62	Male	(User6) Chest Pain
38	32	Male	(User6) DLBCL Fever
39	59	Male	(User6) Hematemesis, Alcohol
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('sim_patient_sim_patient_id_seq', 39, true);


--
-- PostgreSQL database dump complete
--

