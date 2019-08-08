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
273	zzzzzzzzzz_r24_chestpain	62	Male
274	zzzzzzzzzz_r24_diabetic_fatigue	26	Female
275	zzzzzzzzzz_r24_feverB	30	Male
276	zzzzzzzzzz_r24_headache	25	Female
277	zzzzzzzzzz_r24_hematemesis	59	Male
278	zzzzzzzzzz_r24_palpitations	66	Female
279	zzzzzzzzzz_r24_shortnessBreath	70	Male
280	zzzzzzzzzz_r25_chestpain	62	Male
281	zzzzzzzzzz_r25_diabeticFatigue	26	Female
282	zzzzzzzzzz_r25_feverB	30	Male
283	zzzzzzzzzz_r25_headache	25	Female
284	zzzzzzzzzz_R25_hematemesis	59	Male
285	zzzzzzzzzz_r25_palpitations	66	Female
286	zzzzzzzzzz_r25_shortnessBreath	70	Male
287	zzzzzzzzzz_r25_hematemesis	59	Male
288	zzzzzzzzzz_r26_chestPain	62	Male
289	zzzzzzzzzz_r26_diabeticFatigue	26	Female
290	zzzzzzzzz_r26_feverB	30	Male
291	zzzzzzzzzz_r26_feverB	30	Male
292	zzzzzzzzzz_r26_headache	25	Female
293	zzzzzzzzzz_r26_hematemesis	59	Male
294	zzzzzzzzzz_r26_palpitations	66	Female
295	zzzzzzzzzz_shortnessBreath	70	Male
296	zzzzzzzzzz_r26_shortnessBreath	70	Male
297	zzzzzzzzzz_r27_chestPain	62	Male
298	zzzzzzzzzz_r27_diabeticFatigue	26	Female
299	zzzzzzzzzz_r27_feverB	30	Male
300	zzzzzzzzzz_r27_headache	25	Female
301	zzzzzzzzzz_r27_hematemesis	59	Male
302	zzzzzzzzzz_r27_palpitations	66	Female
303	zzzzzzzzzz_r27_shortnessBreath	70	Male
304	zzzzzzzzzz_ls_test	59	Male
305	zzzzzzzzzz_r28_hematemesis	59	Male
306	hematemesis_lisa_shieh	59	Male
307	LISASHIEH_HEADACHE	25	Female
308	zzzzzzzzzz_jh_meningitis	25	Female
309	zzzzzzzzzz_r29_gibleed	59	Male
310	zzzzzzzzzz_r30_palpitations	66	Female
311	zzzzzzzzzz_r31	30	Male
312	zzzzzzzzzz_r31_shortness	70	Male
313	zzzzzzzzzz_r31_feverb	30	Male
314	zzzzzzzzzzz_r32_	26	Female
315	zzzzzzzzzzz_r32_chestpain	62	Male
316	zzzzzzzzzzz_r32_feverB	30	Male
317	zzzzzzzzzzz_r32_headache	25	Female
318	zzzzzzzzzz_r31_hematemesis	59	Male
319	zzzzzzzzzzz_r32_palpitations	66	Female
320	zzzzzzzzzzz_r32_shortnessBreath	70	Male
321	zzzzzzzzzzz_r32_hematemesis	59	Male
322	zzzzzzzzzzz_r33_diabeticFatigue	26	Female
323	zzzzzzzzzzz_r33_chestPain	62	Male
324	zzzzzzzzzzz_r33_feverB	30	Male
325	zzzzzzzzzzz_r33_headache	25	Female
326	zzzzzzzzzzz_r33_hematemesis	59	Male
327	zzzzzzzzzzz_r33_palpitations	66	Female
328	zzzzzzzzzzz_r33_shortnessBreath	70	Male
329	zzzzzzzzzzz_33_chestPain	62	Male
330	zzzzzzzzzzz_33_diabeticFatigue	26	Female
331	zzzzzzzzzzz_33_feverB	30	Male
332	zzzzzzzzzzz_33_headache	25	Female
333	zzzzzzzzzzz_33_hematemesis	59	Male
334	zzzzzzzzzzz_33_palpitations	66	Female
335	zzzzzzzzzzz_33_shortnessBreath	70	Male
336	zzzzzzzzzzz_34_hematemesis	59	Male
337	zzzzzzzzzzz_34_hematemesis	59	Male
338	zzzzzzzzzz_34_hematemesis	59	Male
339	zzzzzzzzzzzz_r34_hematemesis	59	Male
340	zzzzzzzzzzz_r34_palpitaitonis	66	Female
341	zzzzzzzzzzz_r34_headache	25	Female
342	zzzzzzzzzzz_r34_feverB	30	Male
343	zzzzzzzzzzz_r34_shortness	70	Male
344	zzzzzzzzzzz_r35_	62	Male
345	zzzzzzzzzzzz_r35_chestPain	62	Male
346	zzzzzzzzzzzz_r35_diabeticFatigue	26	Female
347	zzzzzzzzzzzz_r35_feverB	30	Male
348	zzzzzzzzzzzz_r35_headache	25	Female
349	zzzzzzzzzzzz_r35_hematemesis	59	Male
350	zzzzzzzzzzzz_r35_palpitations	66	Female
351	zzzzzzzzzzzz_r35_shortnessBreath	70	Male
352	zzzzzzzzzzzz_r36_chestPain	62	Male
353	zzzzzzzzzzzz_r36_diabeticFatigue	26	Female
354		30	Male
355	zzzzzzzzzzzz_r36_feverB	30	Male
356	zzzzzzzzzzzz_r36_headache	25	Female
357	zzzzzzzzzzzz_r36_hematemesis	59	Male
358	zzzzzzzzzzzz_r36_palpitations	66	Female
359	zzzzzzzzzzzz_r36_shortnessBreath	70	Male
360	zzzzzzzzzzzz_r37_chestPain	62	Male
361	zzzzzzzzzzzz_r37_diabeticFatigue	26	Female
362	zzzzzzzzzzzz_r37_feverB	30	Male
363	zzzzzzzzzzzz_r37_headache	25	Female
364	zzzzzzzzzzzz_r37_hematemesis	59	Male
365	zzzzzzzzzzzz_r37_palpitations	66	Female
366	zzzzzzzzzzzz_r37_shortnessBreath	70	Male
367	zzzzzzzzzzzz_r38_chestPain	62	Male
368	zzzzzzzzzzzz_r38_diabeticFatigue	26	Female
369	zzzzzzzzzzzz_r38_feverB	30	Male
370	zzzzzzzzzzzz_r38_headache	25	Female
371	zzzzzzzzzzzz_r38_hematemesis	59	Male
372	zzzzzzzzzzzz_r38_palpitations	66	Female
373	zzzzzzzzzzzz_r38_shortnessBreath	70	Male
374	mel_test	26	Female
375	zzzzzzzzzzzz_r39_chestpain	62	Male
376	zzzzzzzzzzzz_r39_diabeticFatigue	26	Female
377	zzzzzzzzzzzz_r39_feverB	30	Male
378	zzzzzzzzzzzz_r39_headache	25	Female
379	zzzzzzzzzzzz_r39_hematemesis	59	Male
380	zzzzzzzzzzzz_r39_palpitations	66	Female
381	zzzzzzzzzzzz_r39_shortness	70	Male
382	zzzzzzzzzzzz_r40	26	Female
383	zzzzzzzzzzzz_r40	26	Female
384	zzzzzzzzzzzz_r40_chestpain	62	Male
385	zzzzzzzzzzzz_r40_headache	25	Female
386	zzzzzzzzzzzz_r40_palpitations	66	Female
387	zzzzzzzzzzzz_r40_hematem	59	Male
388	zzzzzzzzzzzz_r40_fever	30	Male
389	zzzzzzzzzzzz_r40_shortness	70	Male
390	zzzzzzzzzzzz_r41_chestPain	62	Male
391	zzzzzzzzzzzz_r41_diabeticFatigue	26	Female
392	zzzzzzzzzzzz_r41_feverB	30	Male
393	zzzzzzzzzzzz_r41_headache	25	Female
394	zzzzzzzzzzzz_r41_hematemesis	59	Male
395	zzzzzzzzzzzz_r41_palpitations	66	Female
396	zzzzzzzzzzzz_r41_shortnessBreath	70	Male
397	zzzzzzzzzzzz_r42_chestpain	62	Male
398	zzzzzzzzzzzz_r42_diabeticFatigue	26	Female
399	zzzzzzzzzzzz_r42_feverB	30	Male
400	zzzzzzzzzzzz_r42_headache	25	Female
401	zzzzzzzzzzzz_r42_hematemesis	59	Male
402	zzzzzzzzzzzz_r42_palpitations	66	Female
403	zzzzzzzzzzzz_r42_shortness	70	Male
404	zzzzzzzzzzzz_r43_feverB	30	Male
405	zzzzzzzzzzzz_r43_headache	25	Female
406	zzzzzzzzzzzz_r43_palpitations	66	Female
407	zzzzzzzzzzzz_r43_hematemesis	59	Male
408	zzzzzzzzzzzz_r43_shortnessBreath	70	Male
409	zzzzzzzzzzzz_r43_diabeticFatigue	26	Female
410	zzzzzzzzzzzz_r43_chestPain	62	Male
411	zzzzzzzzzzzzzz_feverB	30	Male
412	zzzzzzzzzzzz_r44_chestPain	62	Male
413	zzzzzzzzzzzz_r44_diabeticFatigue	26	Female
414	zzzzzzzzzzzz_r44_feverB	30	Male
415	zzzzzzzzzzzz_r44_headache	25	Female
416	zzzzzzzzzzzz_r44_hematemesis	59	Male
417	zzzzzzzzzzzz_r44_palipitations	66	Female
418	zzzzzzzzzzzz_r44_shortnessBreath	70	Male
419	zzzzzzzzzzzz_r45_chestPain	62	Male
420	zzzzzzzzzzzz_r45_diabeticFatigue	26	Female
421	zzzzzzzzzzzz_r45_feverB	30	Male
422	zzzzzzzzzzzz_r45_headache	25	Female
423	zzzzzzzzzzzz_r45_hematemesis	59	Male
424	zzzzzzzzzzzz_r45_palpitations	66	Female
425	zzzzzzzzzzzz_r44_shortnessBreath	70	Male
426	zzzzzzzzzzzz_r45_shortness	70	Male
427	zzzzzzzzzzzz_r46_feverB	30	Male
428	zzzzzzzzzzzz_r46_chestPain	62	Male
429	zzzzzzzzzzzz_r46_diabeticFatigue	26	Female
430	zzzzzzzzzzzz_r46_headache	25	Female
431	zzzzzzzzzzzz_r46_hematemesis	59	Male
432	zzzzzzzzzzzz_r46_palpitations	66	Female
433	zzzzzzzzzzzz_r46_shortnessBreath	70	Male
434	zzzzzzzzzzzz_r47_diabeticFatigue	26	Female
435	zzzzzzzzzzzz_r47_chestPain	62	Male
436	zzzzzzzzzzzz_r47_feverB	30	Male
437	zzzzzzzzzzzz_r47_headache	25	Female
438	zzzzzzzzzzzz_r47_hematemesis	59	Male
439	zzzzzzzzzzzz_r47_palpitations	66	Female
440	zzzzzzzzzzzz_r47_shortnessBreath	70	Male
441	zzzzzzzzzzzz_r48_chestPain	62	Male
442	zzzzzzzzzzzz_r48_diabeticFatigue	26	Female
443	zzzzzzzzzzzz_r48_feverB	30	Male
444	zzzzzzzzzzzz_r48_headache	25	Female
445	zzzzzzzzzzzz_r48_hematemesis	59	Male
446	zzzzzzzzzzzz_r48_palpitations	66	Female
447	zzzzzzzzzzzz_r48_shortnessBreath	70	Male
448	zzzzzzzzzzzz_r49_chestPain	62	Male
449	zzzzzzzzzzzz_r49_diabeticFatigue	26	Female
450	zzzzzzzzzzzz_r49_feverB	30	Male
451	zzzzzzzzzzzz_r49_headache	25	Female
452	zzzzzzzzzzzz_r49_hematemesis	59	Male
453	zzzzzzzzzzzz_r49_palpitations	66	Female
454	zzzzzzzzzzzz_r49_shortnessBreath	70	Male
455	zzzzzzzzzzzz_r50_chestPain	62	Male
456	zzzzzzzzzzzz_r50_diabeticFatigue	26	Female
457	zzzzzzzzzzzz_r50_feverB	30	Male
458	zzzzzzzzzzzz_r50_headache	25	Female
459	zzzzzzzzzzzz_r50_hematemesis	59	Male
460	zzzzzzzzzzzz_r50_palpitations	66	Female
461	zzzzzzzzzzzz_r50_shortness	70	Male
\.


--
-- Name: sim_patient_sim_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_sim_patient_id_seq', 461, true);


--
-- PostgreSQL database dump complete
--

