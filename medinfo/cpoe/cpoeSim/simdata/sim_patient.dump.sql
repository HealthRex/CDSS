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
23	(User3) Hematemesis, Alcohol	59	Male
31	(User4) Hematemesis, Alcohol	59	Male
35	(User5) Hematemesis, Alcohol	59	Male
39	(User6) Hematemesis, Alcohol	59	Male
7	(xTemplate) Black vomit	57	Male
50	(Template) Fever B	30	Male
9	(Template) Chest Pain	62	Male
22	(Template) Diabetic Fatigue	26	Female
6	(xTemplate) DLBCL Fever	32	Male
5	(Template) Hematemesis	59	Male
48	(Template) Headache	25	Female
49	(Template) Palpitations	66	Female
13	(User1) Chest Pain	62	Male
16	(User1) Diabetic fatigue	26	Female
14	(User1) DLBCL Fever	32	Male
15	(User1) Vomiting	57	Male
18	(User2) Black vomit	57	Male
19	(User2) Chest Pain	62	Male
17	(User2) Diabetic fatigue	26	Female
20	(User2) DLBCL Fever	32	Male
24	(User3) Chest Pain	62	Male
8	(User3) Diabetic fatigue	26	Female
25	(User3) DLBCL Fever	32	Male
29	(User4) Chest Pain	62	Male
28	(User4) Diabetic Fatigue	26	Female
30	(User4) DLBCL Fever	32	Male
32	(User5) Chest Pain	62	Male
33	(User5) Diabetic Fatigue	26	Female
34	(User5) DLBCL Fever	32	Male
37	(User6) Chest Pain	62	Male
36	(User6) Diabetic fatigue	26	Female
38	(User6) DLBCL Fever	32	Male
61	(Template) Shortness of Breath	70	Male
65	xx_chestpain	62	Male
66	xx_feverb	30	Male
67	xx_headache	25	Female
68	xx_hematemesis	59	Male
69	xx_palpitations	66	Female
70	xx_shortness	70	Male
71	xx_JT_chestpain	62	Male
72	xx_JT_diabeticfatigue	26	Female
73	xx_JT_feverB	30	Male
74	xx_JT_headache	25	Female
75	xx_JT_hematemesis	59	Male
76	xx_JT_palpitations	66	Female
77	zz_KS_feverb	30	Male
78	zz_KS_Headache	25	Female
79	zz_KS_hematemesis	59	Male
80	zz_KS_palpitations	66	Female
81	zz_ks_shortness	70	Male
82	xx_JT_shortness	70	Male
83	zz_KS_Diabeticfatigue	26	Female
84	zz_KS_ChestPain	62	Male
85	nn_sk_chestpain	62	Male
86	nn_sk_diabeticfatigue	26	Female
87	nn_sk_feverb	30	Male
88	nn_sk_headache	25	Female
89	nn_sk_hematemesis	59	Male
90	nn_sk_palpitations	66	Female
91	 nn_sk_shortness	70	Male
92	qq_jc_chest_pain	62	Male
93	qq_jc_diabetic_fatigue	26	Female
94	qq_jc_feverb	30	Male
95	qq_jc_hematemesis	59	Male
96	qq_jc_palpitations	66	Female
97	qq_jc_shortness_breath	70	Male
98	minh_shortness	70	Male
99	yyy_shortness	70	Male
100	qq_jc_headache	25	Female
101	user_script_testing	30	Male
102	user_script_testing_feverb	30	Male
103	user_script_testing_headache	25	Female
104	user_test_scripting_hematemesis	59	Male
105	user_script_testing_hematemesis	66	Female
106	user_script_testing_palpitations	66	Female
107	user_script_testing_shortness_of_breath	70	Male
108	user_script_hematemesis2	59	Male
109	son_5_shortness	70	Male
110	mmm_s5_chestpain	62	Male
111	mmm_s5_feverb	30	Male
112	mmm_s5_headache	25	Female
113	mmm_s5_hematemiss	59	Male
114	mmm_s5_palpitations	66	Female
115	mmm_s5_sob	70	Male
116	rrr_sw6_chest_pain	62	Male
117	rrr_sw6_diabetic_fatigue	26	Female
118	rrr_sw6_feverb	30	Male
119	rrr_sw6_headache	25	Female
120	rrr_sw6_hematemesis	59	Male
121	rrr_sw6_palpitations	66	Female
122	rrr_sw6_shortness_breath	70	Male
123	tester3	59	Male
124	sw_testing_why	59	Male
125	rrr_JC_REVIEW	59	Male
126	hema_tem	59	Male
127	eee_al_7_chestpain	62	Male
128	eee_al_7_diabetic_fatigue	26	Female
129	eee_al_7_feverb	30	Male
130	eee_al_7_headache	25	Female
131	eee_al_7_hematemesis	59	Male
132	eee_al_7_palpitations	66	Female
133	eee_al_7_shortness	70	Male
134	zzz_testing	59	Male
135	zzz_hema2	59	Male
136	zzz_hema3	59	Male
137	zzzz_gl8_chestpain	62	Male
138	zzzz_gl8_diabeticFatigue	26	Female
139	zzzz_gl8_feverB	30	Male
140	zzzz_gl8_headache	25	Female
141	zzzz_gl8_hematemesis	59	Male
142	zzzz_gl8_palpitations	66	Female
143	zzzz_gl8_shortness	70	Male
144	zzzzzz_ph9_chestpain	62	Male
145	zzzzzz_ph9_diabeticfatigue	26	Female
146	zzzzzz_ph9_feverB	30	Male
147	zzzzzz_ph9_headache	25	Female
148	zzzzzz_ph9_hematemesis	59	Male
149	zzzzzz_ph9_palpitations	66	Female
150	zzzzzz_ph9_shortness	70	Male
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_sim_patient_id_seq', 150, true);


--
-- PostgreSQL database dump complete
--

