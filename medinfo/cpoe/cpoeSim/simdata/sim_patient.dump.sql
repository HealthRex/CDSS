--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.9
-- Dumped by pg_dump version 9.6.9

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

COPY public.sim_patient (sim_patient_id, name, age_years, gender, study_list) FROM stdin;
23	(User3) Hematemesis, Alcohol	59	Male	\N
31	(User4) Hematemesis, Alcohol	59	Male	\N
35	(User5) Hematemesis, Alcohol	59	Male	\N
39	(User6) Hematemesis, Alcohol	59	Male	\N
7	(xTemplate) Black vomit	57	Male	\N
9	(Template) Chest Pain	62	Male	\N
22	(Template) Diabetic Fatigue	26	Female	\N
6	(xTemplate) DLBCL Fever	32	Male	\N
48	(Template) Headache	25	Female	\N
49	(Template) Palpitations	66	Female	\N
13	(User1) Chest Pain	62	Male	\N
16	(User1) Diabetic fatigue	26	Female	\N
14	(User1) DLBCL Fever	32	Male	\N
15	(User1) Vomiting	57	Male	\N
18	(User2) Black vomit	57	Male	\N
19	(User2) Chest Pain	62	Male	\N
17	(User2) Diabetic fatigue	26	Female	\N
20	(User2) DLBCL Fever	32	Male	\N
24	(User3) Chest Pain	62	Male	\N
8	(User3) Diabetic fatigue	26	Female	\N
25	(User3) DLBCL Fever	32	Male	\N
29	(User4) Chest Pain	62	Male	\N
28	(User4) Diabetic Fatigue	26	Female	\N
30	(User4) DLBCL Fever	32	Male	\N
32	(User5) Chest Pain	62	Male	\N
33	(User5) Diabetic Fatigue	26	Female	\N
34	(User5) DLBCL Fever	32	Male	\N
37	(User6) Chest Pain	62	Male	\N
36	(User6) Diabetic fatigue	26	Female	\N
38	(User6) DLBCL Fever	32	Male	\N
61	(Template) Shortness of Breath	70	Male	\N
65	xx_chestpain	62	Male	\N
66	xx_feverb	30	Male	\N
67	xx_headache	25	Female	\N
68	xx_hematemesis	59	Male	\N
69	xx_palpitations	66	Female	\N
70	xx_shortness	70	Male	\N
71	xx_JT_chestpain	62	Male	\N
72	xx_JT_diabeticfatigue	26	Female	\N
83	zz_KS_Diabeticfatigue	26	Female	\N
84	zz_KS_ChestPain	62	Male	\N
85	nn_sk_chestpain	62	Male	\N
86	nn_sk_diabeticfatigue	26	Female	\N
87	nn_sk_feverb	30	Male	\N
89	nn_sk_hematemesis	59	Male	\N
92	qq_jc_chest_pain	62	Male	\N
93	qq_jc_diabetic_fatigue	26	Female	\N
98	minh_shortness	70	Male	\N
99	yyy_shortness	70	Male	\N
101	user_script_testing	30	Male	\N
102	user_script_testing_feverb	30	Male	\N
103	user_script_testing_headache	25	Female	\N
104	user_test_scripting_hematemesis	59	Male	\N
105	user_script_testing_hematemesis	66	Female	\N
106	user_script_testing_palpitations	66	Female	\N
107	user_script_testing_shortness_of_breath	70	Male	\N
108	user_script_hematemesis2	59	Male	\N
109	son_5_shortness	70	Male	\N
110	mmm_s5_chestpain	62	Male	\N
116	rrr_sw6_chest_pain	62	Male	\N
117	rrr_sw6_diabetic_fatigue	26	Female	\N
123	tester3	59	Male	\N
124	sw_testing_why	59	Male	\N
125	rrr_JC_REVIEW	59	Male	\N
126	hema_tem	59	Male	\N
127	eee_al_7_chestpain	62	Male	\N
128	eee_al_7_diabetic_fatigue	26	Female	\N
134	zzz_testing	59	Male	\N
135	zzz_hema2	59	Male	\N
136	zzz_hema3	59	Male	\N
137	zzzz_gl8_chestpain	62	Male	\N
138	zzzz_gl8_diabeticFatigue	26	Female	\N
144	zzzzzz_ph9_chestpain	62	Male	\N
145	zzzzzz_ph9_diabeticfatigue	26	Female	\N
151	zzzzzzz_kh10_chestpain	62	Male	\N
152	qqq1_feverb_	30	Male	\N
153	1_test_he	59	Male	\N
154	zzzzzzz_kh10_diabeticfatigue	26	Female	\N
160	zzzzzzzz_r11_chestpain	62	Male	\N
161	zzzzzzzz_r11_diabeticfatigue	26	Female	\N
167	Z_r12_chestpain	62	Male	\N
168	zzzzzzzzz_r12_chestpain	62	Male	\N
169	zzzzzzzzz_r12_diabeticfatigue_one	26	Female	\N
175	zzzzzzzzzz_r13_chestpain	62	Male	\N
176	zzzzzzzzzz_r14_diabeticFatigue	26	Female	\N
178	zzzzzzzzzz_r13_diabeticFatigue	26	Female	\N
183	palptest	66	Female	\N
189	zzzzzzzzzz_r14_chestPain	62	Male	\N
190	zzzzzzzzzz_15_chestpain	62	Male	\N
191	zzzzzzzzzz_15_diabeticFatigue	26	Female	\N
194	zzzzzzzzzz_15_hematemesis	59	Male	\N
197	zzzzzzzzzz_r15_chestPain	62	Male	\N
198	zzzzzzzzzz_r15_diabeticFatigue	26	Female	\N
200	zzzzzzzzzz_r16_chestPain	62	Male	\N
201	zzzzzzzzzz_r16_chestPain	62	Male	\N
202	zzzzzzzzzz_r16_diabeticFatigue	26	Female	\N
208	zzzzzzzzzz_r17_chestPain	62	Male	\N
209	zzzzzzzzzz_r17_diabeticFatigue	26	Female	\N
215	zzzzzzzzzz_r18_chestPain	62	Male	\N
216	zzzzzzzzzz_r18_diabeticFatigue	26	Female	\N
217	zzzzzzzzzz_r18_feverB	30	Male	\N
218	zzzzzzzzzz_r18_headache	25	Female	\N
219	zzzzzzzzzz_r18_hematemesis	59	Male	\N
220	zzzzzzzzzz_r18_palpitations	66	Female	\N
221	zzzzzzzzzz_r18_shortnessBreath	70	Male	\N
222	zzzzzzzzzz_r19_chestPain	62	Male	\N
223	zzzzzzzzzz_r19_diabeticFatigue	26	Female	\N
224	zzzzzzzzz_r19_feverB	30	Male	\N
225	zzzzzzzzz_r19_headache	25	Female	\N
226	zzzzzzzzz_r19_hematemesis	59	Male	\N
228	zzzzzzzzz_r19_headache	25	Female	\N
232	zzzzzzzzzz_shortness_breath	70	Male	\N
234	zzzzzzzzzz_r20_chestPain	62	Male	\N
235	zzzzzzzzzz_r20_diabeticFatigue	26	Female	\N
241	palp_test	66	Female	\N
242	palptest2	66	Female	\N
243	palp_test3	66	Female	\N
244	zzzzzzzzzz_r21_chestPain	62	Male	\N
245	zzzzzzzzzz_r21_diabeticFatigue	26	Female	\N
251	zzzzzzzzzz_r22_chestpain	62	Male	\N
252	zzzzzzzzzz_r22_diabetic_fatigue	26	Female	\N
253	zzzzzzzzzz_r21_feverB	30	Male	\N
254	zzzzzzzzzz_r21_headache	25	Female	\N
256	zzzzzzzzz_r22_feverB	30	Male	\N
259	zzzzzzzzzz_r21_hematemesis	59	Male	\N
260	zzzzzzzzzz_r21_palpitations	66	Female	\N
262	zzzzzzzzzz_r21_palpitations	66	Female	\N
264	testSTAR	66	Female	\N
265	zzzzzzzzzz_r23_chestpain	62	Male	\N
266	zzzzzzzzzz_r23_diabeticFatigue	26	Female	\N
272	testingcase_palpitations	66	Female	\N
273	zzzzzzzzzz_r24_chestpain	62	Male	\N
274	zzzzzzzzzz_r24_diabetic_fatigue	26	Female	\N
280	zzzzzzzzzz_r25_chestpain	62	Male	\N
281	zzzzzzzzzz_r25_diabeticFatigue	26	Female	\N
284	zzzzzzzzzz_R25_hematemesis	59	Male	\N
288	zzzzzzzzzz_r26_chestPain	62	Male	\N
289	zzzzzzzzzz_r26_diabeticFatigue	26	Female	\N
290	zzzzzzzzz_r26_feverB	30	Male	\N
295	zzzzzzzzzz_shortnessBreath	70	Male	\N
297	zzzzzzzzzz_r27_chestPain	62	Male	\N
298	zzzzzzzzzz_r27_diabeticFatigue	26	Female	\N
304	zzzzzzzzzz_ls_test	59	Male	\N
305	zzzzzzzzzz_r28_hematemesis	59	Male	\N
306	hematemesis_lisa_shieh	59	Male	\N
307	LISASHIEH_HEADACHE	25	Female	\N
308	zzzzzzzzzz_jh_meningitis	25	Female	\N
309	zzzzzzzzzz_r29_gibleed	59	Male	\N
310	zzzzzzzzzz_r30_palpitations	66	Female	\N
311	zzzzzzzzzz_r31	30	Male	\N
312	zzzzzzzzzz_r31_shortness	70	Male	\N
313	zzzzzzzzzz_r31_feverb	30	Male	\N
314	zzzzzzzzzzz_r32_	26	Female	\N
315	zzzzzzzzzzz_r32_chestpain	62	Male	\N
318	zzzzzzzzzz_r31_hematemesis	59	Male	\N
322	zzzzzzzzzzz_r33_diabeticFatigue	26	Female	\N
323	zzzzzzzzzzz_r33_chestPain	62	Male	\N
329	zzzzzzzzzzz_33_chestPain	62	Male	\N
330	zzzzzzzzzzz_33_diabeticFatigue	26	Female	\N
331	zzzzzzzzzzz_33_feverB	30	Male	\N
332	zzzzzzzzzzz_33_headache	25	Female	\N
333	zzzzzzzzzzz_33_hematemesis	59	Male	\N
334	zzzzzzzzzzz_33_palpitations	66	Female	\N
335	zzzzzzzzzzz_33_shortnessBreath	70	Male	\N
336	zzzzzzzzzzz_34_hematemesis	59	Male	\N
337	zzzzzzzzzzz_34_hematemesis	59	Male	\N
338	zzzzzzzzzz_34_hematemesis	59	Male	\N
344	zzzzzzzzzzz_r35_	62	Male	\N
345	zzzzzzzzzzzz_r35_chestPain	62	Male	\N
346	zzzzzzzzzzzz_r35_diabeticFatigue	26	Female	\N
352	zzzzzzzzzzzz_r36_chestPain	62	Male	\N
353	zzzzzzzzzzzz_r36_diabeticFatigue	26	Female	\N
354		30	Male	\N
360	zzzzzzzzzzzz_r37_chestPain	62	Male	\N
361	zzzzzzzzzzzz_r37_diabeticFatigue	26	Female	\N
367	zzzzzzzzzzzz_r38_chestPain	62	Male	\N
368	zzzzzzzzzzzz_r38_diabeticFatigue	26	Female	\N
374	mel_test	26	Female	\N
375	zzzzzzzzzzzz_r39_chestpain	62	Male	\N
376	zzzzzzzzzzzz_r39_diabeticFatigue	26	Female	\N
382	zzzzzzzzzzzz_r40	26	Female	\N
383	zzzzzzzzzzzz_r40	26	Female	\N
384	zzzzzzzzzzzz_r40_chestpain	62	Male	\N
390	zzzzzzzzzzzz_r41_chestPain	62	Male	\N
391	zzzzzzzzzzzz_r41_diabeticFatigue	26	Female	\N
397	zzzzzzzzzzzz_r42_chestpain	62	Male	\N
398	zzzzzzzzzzzz_r42_diabeticFatigue	26	Female	\N
409	zzzzzzzzzzzz_r43_diabeticFatigue	26	Female	\N
410	zzzzzzzzzzzz_r43_chestPain	62	Male	\N
411	zzzzzzzzzzzzzz_feverB	30	Male	\N
412	zzzzzzzzzzzz_r44_chestPain	62	Male	\N
413	zzzzzzzzzzzz_r44_diabeticFatigue	26	Female	\N
419	zzzzzzzzzzzz_r45_chestPain	62	Male	\N
420	zzzzzzzzzzzz_r45_diabeticFatigue	26	Female	\N
425	zzzzzzzzzzzz_r44_shortnessBreath	70	Male	\N
428	zzzzzzzzzzzz_r46_chestPain	62	Male	\N
429	zzzzzzzzzzzz_r46_diabeticFatigue	26	Female	\N
434	zzzzzzzzzzzz_r47_diabeticFatigue	26	Female	\N
435	zzzzzzzzzzzz_r47_chestPain	62	Male	\N
436	zzzzzzzzzzzz_r47_feverB	30	Male	\N
437	zzzzzzzzzzzz_r47_headache	25	Female	\N
438	zzzzzzzzzzzz_r47_hematemesis	59	Male	\N
439	zzzzzzzzzzzz_r47_palpitations	66	Female	\N
440	zzzzzzzzzzzz_r47_shortnessBreath	70	Male	\N
441	zzzzzzzzzzzz_r48_chestPain	62	Male	\N
442	zzzzzzzzzzzz_r48_diabeticFatigue	26	Female	\N
443	zzzzzzzzzzzz_r48_feverB	30	Male	\N
444	zzzzzzzzzzzz_r48_headache	25	Female	\N
445	zzzzzzzzzzzz_r48_hematemesis	59	Male	\N
446	zzzzzzzzzzzz_r48_palpitations	66	Female	\N
447	zzzzzzzzzzzz_r48_shortnessBreath	70	Male	\N
448	zzzzzzzzzzzz_r49_chestPain	62	Male	\N
449	zzzzzzzzzzzz_r49_diabeticFatigue	26	Female	\N
455	zzzzzzzzzzzz_r50_chestPain	62	Male	\N
456	zzzzzzzzzzzz_r50_diabeticFatigue	26	Female	\N
5	(Template) Hematemesis	59	Male	OrderRex.Usability.Scoring
50	(Template) Fever B	30	Male	OrderRex.Usability.Scoring
73	xx_JT_feverB	30	Male	OrderRex.Usability.Scoring
74	xx_JT_headache	25	Female	OrderRex.Usability.Scoring
75	xx_JT_hematemesis	59	Male	OrderRex.Usability.Scoring
76	xx_JT_palpitations	66	Female	OrderRex.Usability.Scoring
77	zz_KS_feverb	30	Male	OrderRex.Usability.Scoring
78	zz_KS_Headache	25	Female	OrderRex.Usability.Scoring
79	zz_KS_hematemesis	59	Male	OrderRex.Usability.Scoring
80	zz_KS_palpitations	66	Female	OrderRex.Usability.Scoring
81	zz_ks_shortness	70	Male	OrderRex.Usability.Scoring
82	xx_JT_shortness	70	Male	OrderRex.Usability.Scoring
88	nn_sk_headache	25	Female	OrderRex.Usability.Scoring
90	nn_sk_palpitations	66	Female	OrderRex.Usability.Scoring
91	 nn_sk_shortness	70	Male	OrderRex.Usability.Scoring
94	qq_jc_feverb	30	Male	OrderRex.Usability.Scoring
95	qq_jc_hematemesis	59	Male	OrderRex.Usability.Scoring
96	qq_jc_palpitations	66	Female	OrderRex.Usability.Scoring
97	qq_jc_shortness_breath	70	Male	OrderRex.Usability.Scoring
100	qq_jc_headache	25	Female	OrderRex.Usability.Scoring
111	mmm_s5_feverb	30	Male	OrderRex.Usability.Scoring
112	mmm_s5_headache	25	Female	OrderRex.Usability.Scoring
113	mmm_s5_hematemiss	59	Male	OrderRex.Usability.Scoring
114	mmm_s5_palpitations	66	Female	OrderRex.Usability.Scoring
115	mmm_s5_sob	70	Male	OrderRex.Usability.Scoring
118	rrr_sw6_feverb	30	Male	OrderRex.Usability.Scoring
119	rrr_sw6_headache	25	Female	OrderRex.Usability.Scoring
120	rrr_sw6_hematemesis	59	Male	OrderRex.Usability.Scoring
121	rrr_sw6_palpitations	66	Female	OrderRex.Usability.Scoring
122	rrr_sw6_shortness_breath	70	Male	OrderRex.Usability.Scoring
129	eee_al_7_feverb	30	Male	OrderRex.Usability.Scoring
130	eee_al_7_headache	25	Female	OrderRex.Usability.Scoring
131	eee_al_7_hematemesis	59	Male	OrderRex.Usability.Scoring
132	eee_al_7_palpitations	66	Female	OrderRex.Usability.Scoring
133	eee_al_7_shortness	70	Male	OrderRex.Usability.Scoring
139	zzzz_gl8_feverB	30	Male	OrderRex.Usability.Scoring
140	zzzz_gl8_headache	25	Female	OrderRex.Usability.Scoring
141	zzzz_gl8_hematemesis	59	Male	OrderRex.Usability.Scoring
142	zzzz_gl8_palpitations	66	Female	OrderRex.Usability.Scoring
143	zzzz_gl8_shortness	70	Male	OrderRex.Usability.Scoring
146	zzzzzz_ph9_feverB	30	Male	OrderRex.Usability.Scoring
147	zzzzzz_ph9_headache	25	Female	OrderRex.Usability.Scoring
148	zzzzzz_ph9_hematemesis	59	Male	OrderRex.Usability.Scoring
149	zzzzzz_ph9_palpitations	66	Female	OrderRex.Usability.Scoring
150	zzzzzz_ph9_shortness	70	Male	OrderRex.Usability.Scoring
155	zzzzzzz_kh10_feverb	30	Male	OrderRex.Usability.Scoring
156	zzzzzzz_kh10_headache	25	Female	OrderRex.Usability.Scoring
157	zzzzzzz_kh10_hematemesis	59	Male	OrderRex.Usability.Scoring
158	zzzzzzz_kh10_palpitations	66	Female	OrderRex.Usability.Scoring
159	zzzzzzz_kh10_shortness	70	Male	OrderRex.Usability.Scoring
162	zzzzzzzz_r11_feverb	30	Male	OrderRex.Usability.Scoring
163	zzzzzzzz_r11_headache	25	Female	OrderRex.Usability.Scoring
164	zzzzzzzz_r11_hematemesis	59	Male	OrderRex.Usability.Scoring
165	zzzzzzzz_r11_palpitations	66	Female	OrderRex.Usability.Scoring
166	zzzzzzzz_r11_shortness	70	Male	OrderRex.Usability.Scoring
170	zzzzzzzzz_r12_feverb	30	Male	OrderRex.Usability.Scoring
171	zzzzzzzzz_r12_headache	25	Female	OrderRex.Usability.Scoring
172	zzzzzzzzz_r12_hematemesis	59	Male	OrderRex.Usability.Scoring
173	zzzzzzzzz_r12_palpitations	66	Female	OrderRex.Usability.Scoring
174	zzzzzzzzz_r12_shortness	70	Male	OrderRex.Usability.Scoring
177	zzzzzzzzzz_13_feverB	30	Male	OrderRex.Usability.Scoring
179	zzzzzzzzzz_r13_headache	25	Female	OrderRex.Usability.Scoring
180	zzzzzzzzzz_r13_hematemesis	59	Male	OrderRex.Usability.Scoring
181	zzzzzzzzzz_r13_palpitations	66	Female	OrderRex.Usability.Scoring
182	zzzzzzzzzz_r13_shortnessBreath	70	Male	OrderRex.Usability.Scoring
184	zzzzzzzzzz_r14_feverB	30	Male	OrderRex.Usability.Scoring
185	zzzzzzzzzz_r14_headache	25	Female	OrderRex.Usability.Scoring
186	zzzzzzzzzz_r14_hematemesis	59	Male	OrderRex.Usability.Scoring
187	zzzzzzzzzz_r14_palpitations	66	Female	OrderRex.Usability.Scoring
188	zzzzzzzzzz_r14_shortnessBreath	70	Male	OrderRex.Usability.Scoring
192	zzzzzzzzzz_r15_feverB	30	Male	OrderRex.Usability.Scoring
193	zzzzzzzzzz_r15_headache	25	Female	OrderRex.Usability.Scoring
195	zzzzzzzzzz_r15_palpitations	66	Female	OrderRex.Usability.Scoring
196	zzzzzzzzzz_r15_shortnessofBreath	70	Male	OrderRex.Usability.Scoring
199	zzzzzzzzzz_r15_hematemesis	59	Male	OrderRex.Usability.Scoring
203	zzzzzzzzzz_r16_feverB	30	Male	OrderRex.Usability.Scoring
204	zzzzzzzzzz_r16_headache	25	Female	OrderRex.Usability.Scoring
205	zzzzzzzzzz_r16_hematemesis	59	Male	OrderRex.Usability.Scoring
206	zzzzzzzzzz_r16_palpitations	66	Female	OrderRex.Usability.Scoring
207	zzzzzzzzzz_r16_shortnessBreath	70	Male	OrderRex.Usability.Scoring
210	zzzzzzzzzz_r17_feverB	30	Male	OrderRex.Usability.Scoring
211	zzzzzzzzzz_r17_headache	25	Female	OrderRex.Usability.Scoring
212	zzzzzzzzzz_r17_hematemesis	59	Male	OrderRex.Usability.Scoring
213	zzzzzzzzzz_r17_palpitations	66	Female	OrderRex.Usability.Scoring
214	zzzzzzzzzz_r17_shortness	70	Male	OrderRex.Usability.Scoring
227	zzzzzzzzzz_r19_feverB	30	Male	OrderRex.Usability.Scoring
229	zzzzzzzzzz_r19_headache	25	Female	OrderRex.Usability.Scoring
230	zzzzzzzzzz_r19_hematemesis	59	Male	OrderRex.Usability.Scoring
231	zzzzzzzzzz_r19_palpitations	66	Female	OrderRex.Usability.Scoring
233	zzzzzzzzzz_r19_shortnessBreath	70	Male	OrderRex.Usability.Scoring
236	zzzzzzzzzz_r20_feverB	30	Male	OrderRex.Usability.Scoring
237	zzzzzzzzzz_r20_headache	25	Female	OrderRex.Usability.Scoring
238	zzzzzzzzzz_r20_hematemesis	59	Male	OrderRex.Usability.Scoring
239	zzzzzzzzzz_r20_palpitations	66	Female	OrderRex.Usability.Scoring
240	zzzzzzzzzz_r20_shortnessBreath	70	Male	OrderRex.Usability.Scoring
246	zzzzzzzzzz_r21_feverB	30	Male	OrderRex.Usability.Scoring
247	zzzzzzzzzz_r21_headache	25	Female	OrderRex.Usability.Scoring
248	zzzzzzzzzz_r21_hematemesis	59	Male	OrderRex.Usability.Scoring
249	zzzzzzzzzz_r21_palpitations	66	Female	OrderRex.Usability.Scoring
250	zzzzzzzzzz_r21_shortnessBreath 	70	Male	OrderRex.Usability.Scoring
255	zzzzzzzzzz_r22_hematemesis	59	Male	OrderRex.Usability.Scoring
257	zzzzzzzzzz_r22_feverB	30	Male	OrderRex.Usability.Scoring
258	zzzzzzzzzz_r22_headache	25	Female	OrderRex.Usability.Scoring
261	zzzzzzzzzz_r22_shortnessBreath	70	Male	OrderRex.Usability.Scoring
263	zzzzzzzzzz_r22_palpitations	66	Female	OrderRex.Usability.Scoring
267	zzzzzzzzzz_r23_feverB	30	Male	OrderRex.Usability.Scoring
268	zzzzzzzzzz_r23_headache	25	Female	OrderRex.Usability.Scoring
269	zzzzzzzzzz_r23_hematemesis	59	Male	OrderRex.Usability.Scoring
270	zzzzzzzzzz_r23_palpitations	66	Female	OrderRex.Usability.Scoring
271	zzzzzzzzzz_r23_shortnessBreath	70	Male	OrderRex.Usability.Scoring
275	zzzzzzzzzz_r24_feverB	30	Male	OrderRex.Usability.Scoring
276	zzzzzzzzzz_r24_headache	25	Female	OrderRex.Usability.Scoring
277	zzzzzzzzzz_r24_hematemesis	59	Male	OrderRex.Usability.Scoring
278	zzzzzzzzzz_r24_palpitations	66	Female	OrderRex.Usability.Scoring
279	zzzzzzzzzz_r24_shortnessBreath	70	Male	OrderRex.Usability.Scoring
282	zzzzzzzzzz_r25_feverB	30	Male	OrderRex.Usability.Scoring
283	zzzzzzzzzz_r25_headache	25	Female	OrderRex.Usability.Scoring
285	zzzzzzzzzz_r25_palpitations	66	Female	OrderRex.Usability.Scoring
286	zzzzzzzzzz_r25_shortnessBreath	70	Male	OrderRex.Usability.Scoring
287	zzzzzzzzzz_r25_hematemesis	59	Male	OrderRex.Usability.Scoring
291	zzzzzzzzzz_r26_feverB	30	Male	OrderRex.Usability.Scoring
292	zzzzzzzzzz_r26_headache	25	Female	OrderRex.Usability.Scoring
293	zzzzzzzzzz_r26_hematemesis	59	Male	OrderRex.Usability.Scoring
294	zzzzzzzzzz_r26_palpitations	66	Female	OrderRex.Usability.Scoring
296	zzzzzzzzzz_r26_shortnessBreath	70	Male	OrderRex.Usability.Scoring
299	zzzzzzzzzz_r27_feverB	30	Male	OrderRex.Usability.Scoring
300	zzzzzzzzzz_r27_headache	25	Female	OrderRex.Usability.Scoring
301	zzzzzzzzzz_r27_hematemesis	59	Male	OrderRex.Usability.Scoring
302	zzzzzzzzzz_r27_palpitations	66	Female	OrderRex.Usability.Scoring
303	zzzzzzzzzz_r27_shortnessBreath	70	Male	OrderRex.Usability.Scoring
316	zzzzzzzzzzz_r32_feverB	30	Male	OrderRex.Usability.Scoring
317	zzzzzzzzzzz_r32_headache	25	Female	OrderRex.Usability.Scoring
319	zzzzzzzzzzz_r32_palpitations	66	Female	OrderRex.Usability.Scoring
320	zzzzzzzzzzz_r32_shortnessBreath	70	Male	OrderRex.Usability.Scoring
321	zzzzzzzzzzz_r32_hematemesis	59	Male	OrderRex.Usability.Scoring
324	zzzzzzzzzzz_r33_feverB	30	Male	OrderRex.Usability.Scoring
325	zzzzzzzzzzz_r33_headache	25	Female	OrderRex.Usability.Scoring
326	zzzzzzzzzzz_r33_hematemesis	59	Male	OrderRex.Usability.Scoring
327	zzzzzzzzzzz_r33_palpitations	66	Female	OrderRex.Usability.Scoring
328	zzzzzzzzzzz_r33_shortnessBreath	70	Male	OrderRex.Usability.Scoring
339	zzzzzzzzzzzz_r34_hematemesis	59	Male	OrderRex.Usability.Scoring
340	zzzzzzzzzzz_r34_palpitaitonis	66	Female	OrderRex.Usability.Scoring
341	zzzzzzzzzzz_r34_headache	25	Female	OrderRex.Usability.Scoring
342	zzzzzzzzzzz_r34_feverB	30	Male	OrderRex.Usability.Scoring
343	zzzzzzzzzzz_r34_shortness	70	Male	OrderRex.Usability.Scoring
347	zzzzzzzzzzzz_r35_feverB	30	Male	OrderRex.Usability.Scoring
348	zzzzzzzzzzzz_r35_headache	25	Female	OrderRex.Usability.Scoring
349	zzzzzzzzzzzz_r35_hematemesis	59	Male	OrderRex.Usability.Scoring
350	zzzzzzzzzzzz_r35_palpitations	66	Female	OrderRex.Usability.Scoring
351	zzzzzzzzzzzz_r35_shortnessBreath	70	Male	OrderRex.Usability.Scoring
355	zzzzzzzzzzzz_r36_feverB	30	Male	OrderRex.Usability.Scoring
356	zzzzzzzzzzzz_r36_headache	25	Female	OrderRex.Usability.Scoring
357	zzzzzzzzzzzz_r36_hematemesis	59	Male	OrderRex.Usability.Scoring
358	zzzzzzzzzzzz_r36_palpitations	66	Female	OrderRex.Usability.Scoring
359	zzzzzzzzzzzz_r36_shortnessBreath	70	Male	OrderRex.Usability.Scoring
362	zzzzzzzzzzzz_r37_feverB	30	Male	OrderRex.Usability.Scoring
363	zzzzzzzzzzzz_r37_headache	25	Female	OrderRex.Usability.Scoring
364	zzzzzzzzzzzz_r37_hematemesis	59	Male	OrderRex.Usability.Scoring
365	zzzzzzzzzzzz_r37_palpitations	66	Female	OrderRex.Usability.Scoring
366	zzzzzzzzzzzz_r37_shortnessBreath	70	Male	OrderRex.Usability.Scoring
369	zzzzzzzzzzzz_r38_feverB	30	Male	OrderRex.Usability.Scoring
370	zzzzzzzzzzzz_r38_headache	25	Female	OrderRex.Usability.Scoring
371	zzzzzzzzzzzz_r38_hematemesis	59	Male	OrderRex.Usability.Scoring
372	zzzzzzzzzzzz_r38_palpitations	66	Female	OrderRex.Usability.Scoring
373	zzzzzzzzzzzz_r38_shortnessBreath	70	Male	OrderRex.Usability.Scoring
377	zzzzzzzzzzzz_r39_feverB	30	Male	OrderRex.Usability.Scoring
378	zzzzzzzzzzzz_r39_headache	25	Female	OrderRex.Usability.Scoring
379	zzzzzzzzzzzz_r39_hematemesis	59	Male	OrderRex.Usability.Scoring
380	zzzzzzzzzzzz_r39_palpitations	66	Female	OrderRex.Usability.Scoring
381	zzzzzzzzzzzz_r39_shortness	70	Male	OrderRex.Usability.Scoring
385	zzzzzzzzzzzz_r40_headache	25	Female	OrderRex.Usability.Scoring
386	zzzzzzzzzzzz_r40_palpitations	66	Female	OrderRex.Usability.Scoring
387	zzzzzzzzzzzz_r40_hematem	59	Male	OrderRex.Usability.Scoring
388	zzzzzzzzzzzz_r40_fever	30	Male	OrderRex.Usability.Scoring
389	zzzzzzzzzzzz_r40_shortness	70	Male	OrderRex.Usability.Scoring
392	zzzzzzzzzzzz_r41_feverB	30	Male	OrderRex.Usability.Scoring
393	zzzzzzzzzzzz_r41_headache	25	Female	OrderRex.Usability.Scoring
394	zzzzzzzzzzzz_r41_hematemesis	59	Male	OrderRex.Usability.Scoring
395	zzzzzzzzzzzz_r41_palpitations	66	Female	OrderRex.Usability.Scoring
396	zzzzzzzzzzzz_r41_shortnessBreath	70	Male	OrderRex.Usability.Scoring
399	zzzzzzzzzzzz_r42_feverB	30	Male	OrderRex.Usability.Scoring
400	zzzzzzzzzzzz_r42_headache	25	Female	OrderRex.Usability.Scoring
401	zzzzzzzzzzzz_r42_hematemesis	59	Male	OrderRex.Usability.Scoring
402	zzzzzzzzzzzz_r42_palpitations	66	Female	OrderRex.Usability.Scoring
403	zzzzzzzzzzzz_r42_shortness	70	Male	OrderRex.Usability.Scoring
404	zzzzzzzzzzzz_r43_feverB	30	Male	OrderRex.Usability.Scoring
405	zzzzzzzzzzzz_r43_headache	25	Female	OrderRex.Usability.Scoring
406	zzzzzzzzzzzz_r43_palpitations	66	Female	OrderRex.Usability.Scoring
407	zzzzzzzzzzzz_r43_hematemesis	59	Male	OrderRex.Usability.Scoring
408	zzzzzzzzzzzz_r43_shortnessBreath	70	Male	OrderRex.Usability.Scoring
414	zzzzzzzzzzzz_r44_feverB	30	Male	OrderRex.Usability.Scoring
415	zzzzzzzzzzzz_r44_headache	25	Female	OrderRex.Usability.Scoring
416	zzzzzzzzzzzz_r44_hematemesis	59	Male	OrderRex.Usability.Scoring
417	zzzzzzzzzzzz_r44_palipitations	66	Female	OrderRex.Usability.Scoring
418	zzzzzzzzzzzz_r44_shortnessBreath	70	Male	OrderRex.Usability.Scoring
421	zzzzzzzzzzzz_r45_feverB	30	Male	OrderRex.Usability.Scoring
422	zzzzzzzzzzzz_r45_headache	25	Female	OrderRex.Usability.Scoring
423	zzzzzzzzzzzz_r45_hematemesis	59	Male	OrderRex.Usability.Scoring
424	zzzzzzzzzzzz_r45_palpitations	66	Female	OrderRex.Usability.Scoring
426	zzzzzzzzzzzz_r45_shortness	70	Male	OrderRex.Usability.Scoring
427	zzzzzzzzzzzz_r46_feverB	30	Male	OrderRex.Usability.Scoring
430	zzzzzzzzzzzz_r46_headache	25	Female	OrderRex.Usability.Scoring
431	zzzzzzzzzzzz_r46_hematemesis	59	Male	OrderRex.Usability.Scoring
432	zzzzzzzzzzzz_r46_palpitations	66	Female	OrderRex.Usability.Scoring
433	zzzzzzzzzzzz_r46_shortnessBreath	70	Male	OrderRex.Usability.Scoring
450	zzzzzzzzzzzz_r49_feverB	30	Male	OrderRex.Usability.Scoring
451	zzzzzzzzzzzz_r49_headache	25	Female	OrderRex.Usability.Scoring
452	zzzzzzzzzzzz_r49_hematemesis	59	Male	OrderRex.Usability.Scoring
453	zzzzzzzzzzzz_r49_palpitations	66	Female	OrderRex.Usability.Scoring
454	zzzzzzzzzzzz_r49_shortnessBreath	70	Male	OrderRex.Usability.Scoring
457	zzzzzzzzzzzz_r50_feverB	30	Male	OrderRex.Usability.Scoring
458	zzzzzzzzzzzz_r50_headache	25	Female	OrderRex.Usability.Scoring
459	zzzzzzzzzzzz_r50_hematemesis	59	Male	OrderRex.Usability.Scoring
460	zzzzzzzzzzzz_r50_palpitations	66	Female	OrderRex.Usability.Scoring
461	zzzzzzzzzzzz_r50_shortness	70	Male	OrderRex.Usability.Scoring
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_sim_patient_id_seq', 461, true);


--
-- PostgreSQL database dump complete
--

