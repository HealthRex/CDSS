--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.11
-- Dumped by pg_dump version 9.6.11

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
151	zzzzzzz_kh10_chestpain	62	Male
152	qqq1_feverb_	30	Male
153	1_test_he	59	Male
154	zzzzzzz_kh10_diabeticfatigue	26	Female
155	zzzzzzz_kh10_feverb	30	Male
156	zzzzzzz_kh10_headache	25	Female
157	zzzzzzz_kh10_hematemesis	59	Male
158	zzzzzzz_kh10_palpitations	66	Female
159	zzzzzzz_kh10_shortness	70	Male
160	zzzzzzzz_r11_chestpain	62	Male
161	zzzzzzzz_r11_diabeticfatigue	26	Female
162	zzzzzzzz_r11_feverb	30	Male
163	zzzzzzzz_r11_headache	25	Female
164	zzzzzzzz_r11_hematemesis	59	Male
165	zzzzzzzz_r11_palpitations	66	Female
166	zzzzzzzz_r11_shortness	70	Male
167	Z_r12_chestpain	62	Male
168	zzzzzzzzz_r12_chestpain	62	Male
169	zzzzzzzzz_r12_diabeticfatigue_one	26	Female
170	zzzzzzzzz_r12_feverb	30	Male
171	zzzzzzzzz_r12_headache	25	Female
172	zzzzzzzzz_r12_hematemesis	59	Male
173	zzzzzzzzz_r12_palpitations	66	Female
174	zzzzzzzzz_r12_shortness	70	Male
175	zzzzzzzzzz_r13_chestpain	62	Male
176	zzzzzzzzzz_r14_diabeticFatigue	26	Female
177	zzzzzzzzzz_13_feverB	30	Male
178	zzzzzzzzzz_r13_diabeticFatigue	26	Female
179	zzzzzzzzzz_r13_headache	25	Female
180	zzzzzzzzzz_r13_hematemesis	59	Male
181	zzzzzzzzzz_r13_palpitations	66	Female
182	zzzzzzzzzz_r13_shortnessBreath	70	Male
183	palptest	66	Female
184	zzzzzzzzzz_r14_feverB	30	Male
185	zzzzzzzzzz_r14_headache	25	Female
186	zzzzzzzzzz_r14_hematemesis	59	Male
187	zzzzzzzzzz_r14_palpitations	66	Female
188	zzzzzzzzzz_r14_shortnessBreath	70	Male
189	zzzzzzzzzz_r14_chestPain	62	Male
190	zzzzzzzzzz_15_chestpain	62	Male
191	zzzzzzzzzz_15_diabeticFatigue	26	Female
192	zzzzzzzzzz_r15_feverB	30	Male
193	zzzzzzzzzz_r15_headache	25	Female
194	zzzzzzzzzz_15_hematemesis	59	Male
195	zzzzzzzzzz_r15_palpitations	66	Female
196	zzzzzzzzzz_r15_shortnessofBreath	70	Male
197	zzzzzzzzzz_r15_chestPain	62	Male
198	zzzzzzzzzz_r15_diabeticFatigue	26	Female
199	zzzzzzzzzz_r15_hematemesis	59	Male
200	zzzzzzzzzz_r16_chestPain	62	Male
201	zzzzzzzzzz_r16_chestPain	62	Male
202	zzzzzzzzzz_r16_diabeticFatigue	26	Female
203	zzzzzzzzzz_r16_feverB	30	Male
204	zzzzzzzzzz_r16_headache	25	Female
205	zzzzzzzzzz_r16_hematemesis	59	Male
206	zzzzzzzzzz_r16_palpitations	66	Female
207	zzzzzzzzzz_r16_shortnessBreath	70	Male
208	zzzzzzzzzz_r17_chestPain	62	Male
209	zzzzzzzzzz_r17_diabeticFatigue	26	Female
210	zzzzzzzzzz_r17_feverB	30	Male
211	zzzzzzzzzz_r17_headache	25	Female
212	zzzzzzzzzz_r17_hematemesis	59	Male
213	zzzzzzzzzz_r17_palpitations	66	Female
214	zzzzzzzzzz_r17_shortness	70	Male
215	zzzzzzzzzz_r18_chestPain	62	Male
216	zzzzzzzzzz_r18_diabeticFatigue	26	Female
217	zzzzzzzzzz_r18_feverB	30	Male
218	zzzzzzzzzz_r18_headache	25	Female
219	zzzzzzzzzz_r18_hematemesis	59	Male
220	zzzzzzzzzz_r18_palpitations	66	Female
221	zzzzzzzzzz_r18_shortnessBreath	70	Male
222	zzzzzzzzzz_r19_chestPain	62	Male
223	zzzzzzzzzz_r19_diabeticFatigue	26	Female
224	zzzzzzzzz_r19_feverB	30	Male
225	zzzzzzzzz_r19_headache	25	Female
226	zzzzzzzzz_r19_hematemesis	59	Male
227	zzzzzzzzzz_r19_feverB	30	Male
228	zzzzzzzzz_r19_headache	25	Female
229	zzzzzzzzzz_r19_headache	25	Female
230	zzzzzzzzzz_r19_hematemesis	59	Male
231	zzzzzzzzzz_r19_palpitations	66	Female
232	zzzzzzzzzz_shortness_breath	70	Male
233	zzzzzzzzzz_r19_shortnessBreath	70	Male
234	zzzzzzzzzz_r20_chestPain	62	Male
235	zzzzzzzzzz_r20_diabeticFatigue	26	Female
236	zzzzzzzzzz_r20_feverB	30	Male
237	zzzzzzzzzz_r20_headache	25	Female
238	zzzzzzzzzz_r20_hematemesis	59	Male
239	zzzzzzzzzz_r20_palpitations	66	Female
240	zzzzzzzzzz_r20_shortnessBreath	70	Male
241	palp_test	66	Female
242	palptest2	66	Female
243	palp_test3	66	Female
244	zzzzzzzzzz_r21_chestPain	62	Male
245	zzzzzzzzzz_r21_diabeticFatigue	26	Female
246	zzzzzzzzzz_r21_feverB	30	Male
247	zzzzzzzzzz_r21_headache	25	Female
248	zzzzzzzzzz_r21_hematemesis	59	Male
249	zzzzzzzzzz_r21_palpitations	66	Female
250	zzzzzzzzzz_r21_shortnessBreath 	70	Male
251	zzzzzzzzzz_r22_chestpain	62	Male
252	zzzzzzzzzz_r22_diabetic_fatigue	26	Female
253	zzzzzzzzzz_r21_feverB	30	Male
254	zzzzzzzzzz_r21_headache	25	Female
255	zzzzzzzzzz_r22_hematemesis	59	Male
256	zzzzzzzzz_r22_feverB	30	Male
257	zzzzzzzzzz_r22_feverB	30	Male
258	zzzzzzzzzz_r22_headache	25	Female
259	zzzzzzzzzz_r21_hematemesis	59	Male
260	zzzzzzzzzz_r21_palpitations	66	Female
261	zzzzzzzzzz_r22_shortnessBreath	70	Male
262	zzzzzzzzzz_r21_palpitations	66	Female
263	zzzzzzzzzz_r22_palpitations	66	Female
264	testSTAR	66	Female
265	zzzzzzzzzz_r23_chestpain	62	Male
266	zzzzzzzzzz_r23_diabeticFatigue	26	Female
267	zzzzzzzzzz_r23_feverB	30	Male
268	zzzzzzzzzz_r23_headache	25	Female
269	zzzzzzzzzz_r23_hematemesis	59	Male
270	zzzzzzzzzz_r23_palpitations	66	Female
271	zzzzzzzzzz_r23_shortnessBreath	70	Male
272	testingcase_palpitations	66	Female
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_sim_patient_id_seq', 272, true);


--
-- PostgreSQL database dump complete
--

