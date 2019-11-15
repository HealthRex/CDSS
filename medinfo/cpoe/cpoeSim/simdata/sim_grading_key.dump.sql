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
-- Data for Name: sim_grading_key; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_grading_key (sim_grading_key_id, sim_grader_id, sim_state_id, sim_case_name, clinical_item_id, score, confidence, group_name, comment) FROM stdin;
9597	Panel Average	40	atrial_fibrillation	45977	3	\N	\N	\N
10406	Andre Kumar	40	atrial_fibrillation	45977	0	4	Weight	\N
10407	Jonathan Chen	40	atrial_fibrillation	45977	0	2	\N	\N
10408	Lisa Shieh	40	atrial_fibrillation	45977	0	3	\N	\N
10409	Panel Consensus	40	atrial_fibrillation	45977	0	\N	\N	\N
8888	Andre Kumar	41	atrial_fibrillation	45977	5	3	Nursing	Only if combind with enoxaparin
8889	Jason Hom	41	atrial_fibrillation	45977	5	4	\N	\N
9442	Panel Average	41	atrial_fibrillation	45977	4	\N	\N	\N
9472	Panel Consensus	41	atrial_fibrillation	45977	4	\N	\N	\N
9620	Lisa Shieh	41	atrial_fibrillation	45977	3	3	\N	\N
10410	Jonathan Chen	41	atrial_fibrillation	45977	0	2	\N	\N
11392	Jonathan Chen	43	atrial_fibrillation	46605	0	3	\N	Irregular rhythm, so adenosine not so relevant
8333	Andre Kumar	41	atrial_fibrillation	45814	8	5	Admit Order	\N
8334	Panel Average	41	atrial_fibrillation	45814	8	\N	\N	\N
10411	Panel Consensus	41	atrial_fibrillation	45814	0	\N	\N	\N
11271	Jonathan Chen	41	atrial_fibrillation	65641	0	3	\N	\N
10412	Jonathan Chen	40	atrial_fibrillation	35968	0	1	\N	Still some negative inotropy?
11106	Andre Kumar	40	atrial_fibrillation	35968	-5	3	Rhythm Control	\N
11107	Jason Hom	40	atrial_fibrillation	35968	-5	5	\N	\N
11108	Lisa Shieh	40	atrial_fibrillation	35968	-5	3	\N	\N
11109	Panel Average	40	atrial_fibrillation	35968	-5	\N	\N	\N
11110	Panel Consensus	40	atrial_fibrillation	35968	-5	\N	\N	\N
10413	Jonathan Chen	43	atrial_fibrillation	35968	0	1	\N	Still some negative inotropy?
11111	Lisa Shieh	43	atrial_fibrillation	35968	-5	3	\N	\N
11179	Panel Average	43	atrial_fibrillation	35968	-8	\N	\N	\N
11182	Andre Kumar	43	atrial_fibrillation	35968	-8	4	Rhythm Control	\N
11183	Panel Consensus	43	atrial_fibrillation	35968	-8	\N	\N	\N
11211	Jason Hom	43	atrial_fibrillation	35968	-10	5	\N	\N
10414	Jonathan Chen	43	atrial_fibrillation	44352	0	2	\N	\N
11112	Lisa Shieh	43	atrial_fibrillation	44352	-5	3	\N	\N
11184	Panel Consensus	43	atrial_fibrillation	44352	-8	\N	\N	\N
11200	Panel Average	43	atrial_fibrillation	44352	-8	\N	\N	\N
11404	Jonathan Chen	41	atrial_fibrillation	47146	1	2	Aspirin	\N
8890	Lisa Shieh	40	atrial_fibrillation	44206	5	5	\N	\N
9947	Jason Hom	40	atrial_fibrillation	44206	2	4	\N	\N
9948	Panel Consensus	40	atrial_fibrillation	44206	2	\N	\N	\N
10206	Panel Average	40	atrial_fibrillation	44206	2	\N	\N	\N
10238	Jonathan Chen	40	atrial_fibrillation	44206	1	2	\N	Troponin mildly elevated so they're treating like NSTEMI, but really is Type 2 demand from the Afib
10994	Andre Kumar	40	atrial_fibrillation	44206	-2	4	Anticoagulants	\N
8468	Lisa Shieh	41	atrial_fibrillation	44206	7	3	\N	\N
9926	Panel Average	41	atrial_fibrillation	44206	2	\N	\N	\N
9949	Panel Consensus	41	atrial_fibrillation	44206	2	\N	\N	\N
10239	Jonathan Chen	41	atrial_fibrillation	44206	1	2	Aspirin	Troponin mildly elevated so they're treating like NSTEMI, but really is Type 2 demand from the Afib
10415	Andre Kumar	41	atrial_fibrillation	44206	0	1	Anticoagulants	-3points if combined wiht other anticoagulants
10416	Jason Hom	41	atrial_fibrillation	44206	0	4	\N	\N
11285	Jonathan Chen	43	atrial_fibrillation	44206	1	2	Aspirin	\N
11241	Jonathan Chen	43	atrial_fibrillation	44315	1	2	Aspirin	\N
8891	Lisa Shieh	41	atrial_fibrillation	44240	5	3	\N	\N
9950	Panel Consensus	41	atrial_fibrillation	44240	2	\N	\N	\N
10207	Panel Average	41	atrial_fibrillation	44240	2	\N	\N	\N
10240	Jonathan Chen	41	atrial_fibrillation	44240	1	2	\N	\N
10417	Andre Kumar	41	atrial_fibrillation	44240	0	5	Statin	\N
10418	Jason Hom	41	atrial_fibrillation	44240	0	4	\N	\N
9621	Lisa Shieh	43	atrial_fibrillation	45901	3	3	\N	\N
9951	Jonathan Chen	43	atrial_fibrillation	45901	2	2	\N	\N
10241	Andre Kumar	43	atrial_fibrillation	45901	1	2	Blood Culture Not Infection	\N
10242	Panel Consensus	43	atrial_fibrillation	45901	1	\N	\N	\N
10380	Panel Average	43	atrial_fibrillation	45901	1	\N	\N	\N
10995	Jason Hom	43	atrial_fibrillation	45901	-2	5	\N	\N
8892	Jason Hom	40	atrial_fibrillation	45919	5	4	\N	\N
9952	Panel Consensus	40	atrial_fibrillation	45919	2	\N	\N	\N
10208	Panel Average	40	atrial_fibrillation	45919	2	\N	\N	\N
10243	Jonathan Chen	40	atrial_fibrillation	45919	1	2	Blood Gas	\N
10419	Andre Kumar	40	atrial_fibrillation	45919	0	3	Blood Gas	\N
10420	Lisa Shieh	40	atrial_fibrillation	45919	0	3	\N	\N
8469	Panel Consensus	40	atrial_fibrillation	45887	7	\N	\N	\N
8657	Panel Average	40	atrial_fibrillation	45887	7	\N	\N	\N
8893	Andre Kumar	40	atrial_fibrillation	45887	5	2	Metabolic Panel	\N
8894	Lisa Shieh	40	atrial_fibrillation	45887	5	3	\N	\N
10421	Jonathan Chen	40	atrial_fibrillation	45887	0	2	\N	\N
8895	Jason Hom	43	atrial_fibrillation	45887	5	5	\N	\N
8896	Lisa Shieh	43	atrial_fibrillation	45887	5	3	\N	\N
9443	Panel Average	43	atrial_fibrillation	45887	4	\N	\N	\N
9473	Panel Consensus	43	atrial_fibrillation	45887	4	\N	\N	\N
9622	Andre Kumar	43	atrial_fibrillation	45887	3	2	Metabolic Panel	\N
10422	Jonathan Chen	43	atrial_fibrillation	45887	0	2	\N	\N
11315	Jonathan Chen	40	atrial_fibrillation	41870	0	5	\N	\N
10423	Andre Kumar	40	atrial_fibrillation	31164	0	5	UNK	? Is this an order set?
10424	Panel Average	40	atrial_fibrillation	31164	0	\N	\N	\N
8300	Panel Average	40	atrial_fibrillation	45827	8	\N	\N	\N
8335	Panel Consensus	40	atrial_fibrillation	45827	8	\N	\N	\N
8897	Andre Kumar	40	atrial_fibrillation	45827	5	5	ECG + Monitoring	\N
8898	Jonathan Chen	40	atrial_fibrillation	45827	5	3	\N	\N
11461	Jonathan Chen	41	atrial_fibrillation	45827	5	3	\N	\N
8698	Panel Consensus	40	atrial_fibrillation	45793	6	\N	\N	\N
8841	Panel Average	40	atrial_fibrillation	45793	6	\N	\N	\N
8899	Lisa Shieh	40	atrial_fibrillation	45793	5	3	\N	\N
9953	Andre Kumar	40	atrial_fibrillation	45793	2	3	CBC	\N
9954	Jonathan Chen	40	atrial_fibrillation	45793	2	3	CBC	\N
8470	Lisa Shieh	41	atrial_fibrillation	45793	7	3	\N	\N
8900	Jason Hom	41	atrial_fibrillation	45793	5	4	\N	\N
9444	Panel Average	41	atrial_fibrillation	45793	4	\N	\N	\N
9474	Panel Consensus	41	atrial_fibrillation	45793	4	\N	\N	\N
9955	Jonathan Chen	41	atrial_fibrillation	45793	2	3	CBC	\N
10244	Andre Kumar	41	atrial_fibrillation	45793	1	4	CBC	\N
8699	Panel Consensus	43	atrial_fibrillation	45793	6	\N	\N	\N
8901	Jason Hom	43	atrial_fibrillation	45793	5	5	\N	\N
8902	Lisa Shieh	43	atrial_fibrillation	45793	5	3	\N	\N
9475	Panel Average	43	atrial_fibrillation	45793	4	\N	\N	\N
9956	Andre Kumar	43	atrial_fibrillation	45793	2	3	CBC	\N
9957	Jonathan Chen	43	atrial_fibrillation	45793	2	3	CBC	\N
8700	Panel Consensus	40	atrial_fibrillation	45788	6	\N	\N	\N
8842	Panel Average	40	atrial_fibrillation	45788	6	\N	\N	\N
8903	Lisa Shieh	40	atrial_fibrillation	45788	5	3	\N	\N
9958	Andre Kumar	40	atrial_fibrillation	45788	2	3	CBC	\N
9959	Jonathan Chen	40	atrial_fibrillation	45788	2	3	CBC	\N
8471	Lisa Shieh	41	atrial_fibrillation	45788	7	3	\N	\N
8701	Panel Consensus	41	atrial_fibrillation	45788	6	\N	\N	\N
8904	Jason Hom	41	atrial_fibrillation	45788	5	4	\N	\N
9445	Panel Average	41	atrial_fibrillation	45788	4	\N	\N	\N
9960	Jonathan Chen	41	atrial_fibrillation	45788	2	3	CBC	\N
10245	Andre Kumar	41	atrial_fibrillation	45788	1	4	CBC	\N
9623	Lisa Shieh	40	atrial_fibrillation	50400	3	3	\N	\N
10425	Jason Hom	40	atrial_fibrillation	50400	0	4	\N	\N
10426	Jonathan Chen	40	atrial_fibrillation	50400	0	2	\N	\N
10965	Panel Average	40	atrial_fibrillation	50400	-1	\N	\N	\N
10970	Panel Consensus	40	atrial_fibrillation	50400	-1	\N	\N	\N
11113	Andre Kumar	40	atrial_fibrillation	50400	-5	2	Consult	"Delays care no expertise aside from sedation (which can be given by ER providers)"
8905	Lisa Shieh	43	atrial_fibrillation	50400	5	3	\N	\N
9476	Panel Average	43	atrial_fibrillation	50400	4	\N	\N	\N
9477	Panel Consensus	43	atrial_fibrillation	50400	4	\N	\N	\N
10427	Jonathan Chen	43	atrial_fibrillation	50400	0	2	\N	\N
11075	Andre Kumar	43	atrial_fibrillation	50400	-3	3	Consult	no clear benefit of consulting anes
8472	Lisa Shieh	40	atrial_fibrillation	49251	7	3	\N	\N
8473	Panel Consensus	40	atrial_fibrillation	49251	7	\N	\N	\N
8658	Panel Average	40	atrial_fibrillation	49251	7	\N	\N	\N
9624	Andre Kumar	40	atrial_fibrillation	49251	3	4	Consult	\N
10428	Jonathan Chen	40	atrial_fibrillation	49251	0	2	\N	\N
8474	Lisa Shieh	41	atrial_fibrillation	49251	7	3	\N	\N
8906	Jason Hom	41	atrial_fibrillation	49251	5	4	\N	\N
8907	Panel Average	41	atrial_fibrillation	49251	5	\N	\N	\N
8908	Panel Consensus	41	atrial_fibrillation	49251	5	\N	\N	\N
9625	Andre Kumar	41	atrial_fibrillation	49251	3	4	Consult	\N
10429	Jonathan Chen	41	atrial_fibrillation	49251	0	2	\N	\N
8702	Panel Average	43	atrial_fibrillation	49251	6	\N	\N	\N
8909	Lisa Shieh	43	atrial_fibrillation	49251	5	3	\N	\N
9961	Andre Kumar	43	atrial_fibrillation	49251	2	3	Consult	delays care, but cardiologist would likely give correct reccomendations
10430	Jonathan Chen	43	atrial_fibrillation	49251	0	2	\N	\N
11452	Jonathan Chen	41	atrial_fibrillation	65695	0	2	\N	\N
11076	Andre Kumar	43	atrial_fibrillation	65695	-3	3	Consult	delays care
11077	Panel Average	43	atrial_fibrillation	65695	-3	\N	\N	\N
8475	Lisa Shieh	43	atrial_fibrillation	61323	7	3	\N	\N
8680	Panel Average	43	atrial_fibrillation	61323	6	\N	\N	\N
8703	Panel Consensus	43	atrial_fibrillation	61323	6	\N	\N	\N
9962	Andre Kumar	43	atrial_fibrillation	61323	2	3	Consult	delays care, but ICU would likely give correct reccomendations
10431	Jonathan Chen	43	atrial_fibrillation	61323	0	2	\N	\N
10432	Jonathan Chen	40	atrial_fibrillation	50098	0	2	CT Head	\N
10433	Lisa Shieh	40	atrial_fibrillation	50098	0	5	\N	\N
11114	Jason Hom	40	atrial_fibrillation	50098	-5	5	\N	\N
11115	Panel Average	40	atrial_fibrillation	50098	-5	\N	\N	\N
11116	Panel Consensus	40	atrial_fibrillation	50098	-5	\N	\N	\N
10434	Jonathan Chen	40	atrial_fibrillation	45983	0	2	CT Head	\N
10435	Lisa Shieh	40	atrial_fibrillation	45983	0	3	\N	\N
11117	Jason Hom	40	atrial_fibrillation	45983	-5	4	\N	\N
11118	Panel Average	40	atrial_fibrillation	45983	-5	\N	\N	\N
11119	Panel Consensus	40	atrial_fibrillation	45983	-5	\N	\N	\N
10436	Jonathan Chen	40	atrial_fibrillation	49965	0	2	CT Head	\N
10437	Lisa Shieh	40	atrial_fibrillation	49965	0	5	\N	\N
11120	Jason Hom	40	atrial_fibrillation	49965	-5	5	\N	\N
11121	Panel Average	40	atrial_fibrillation	49965	-5	\N	\N	\N
11122	Panel Consensus	40	atrial_fibrillation	49965	-5	\N	\N	\N
10438	Andre Kumar	40	atrial_fibrillation	48871	0	3	D-dimer	\N
10439	Panel Average	40	atrial_fibrillation	48871	0	\N	\N	\N
8236	Panel Average	43	atrial_fibrillation	-100	9	\N	\N	\N
8476	Andre Kumar	43	atrial_fibrillation	-100	7	5	Cardioversion	Less points for delaying
8910	Lisa Shieh	40	atrial_fibrillation	44353	5	3	\N	\N
10440	Jonathan Chen	40	atrial_fibrillation	44353	0	1	\N	This is probably mis-entered Diltiazem (which is a double negative!) Or could it arguably be intended sedation before DCCV? Probably not (that would be midazolam or lorazepam more likely).
10989	Panel Average	40	atrial_fibrillation	44353	-2	\N	\N	\N
10996	Panel Consensus	40	atrial_fibrillation	44353	-2	\N	\N	\N
11123	Andre Kumar	40	atrial_fibrillation	44353	-5	5	Sedation	Patient lethargic and diazepam not good for procedural sedation
11124	Jason Hom	40	atrial_fibrillation	44353	-5	5	\N	\N
8911	Jason Hom	41	atrial_fibrillation	45824	5	4	\N	\N
8912	Lisa Shieh	41	atrial_fibrillation	45824	5	3	\N	\N
9478	Panel Average	41	atrial_fibrillation	45824	4	\N	\N	\N
9963	Andre Kumar	41	atrial_fibrillation	45824	2	4	Diet	\N
10246	Panel Consensus	41	atrial_fibrillation	45824	1	\N	\N	\N
10441	Jonathan Chen	41	atrial_fibrillation	45824	0	2	\N	\N
10247	Andre Kumar	43	atrial_fibrillation	45824	1	2	Diet	\N
10248	Panel Average	43	atrial_fibrillation	45824	1	\N	\N	\N
8477	Panel Consensus	40	atrial_fibrillation	45811	7	\N	\N	\N
8659	Panel Average	40	atrial_fibrillation	45811	7	\N	\N	\N
8913	Andre Kumar	40	atrial_fibrillation	45811	5	5	NPO	\N
8914	Lisa Shieh	40	atrial_fibrillation	45811	5	5	\N	\N
9964	Jonathan Chen	40	atrial_fibrillation	45811	2	3	\N	\N
11321	Jonathan Chen	41	atrial_fibrillation	45811	2	3	\N	\N
8478	Panel Consensus	43	atrial_fibrillation	45811	7	\N	\N	\N
8660	Panel Average	43	atrial_fibrillation	45811	7	\N	\N	\N
8915	Andre Kumar	43	atrial_fibrillation	45811	5	3	NPO	\N
8916	Jason Hom	43	atrial_fibrillation	45811	5	5	\N	\N
9965	Jonathan Chen	43	atrial_fibrillation	45811	2	3	\N	\N
9966	Jonathan Chen	40	atrial_fibrillation	46674	2	3	\N	\N
10442	Lisa Shieh	40	atrial_fibrillation	46674	0	3	\N	\N
11100	Panel Average	40	atrial_fibrillation	46674	-4	\N	\N	\N
11101	Panel Consensus	40	atrial_fibrillation	46674	-4	\N	\N	\N
11125	Jason Hom	40	atrial_fibrillation	46674	-5	4	\N	\N
11173	Andre Kumar	40	atrial_fibrillation	46674	-6	5	Rate Control	too slow acting
11289	Jonathan Chen	43	atrial_fibrillation	46674	-5	3	Negative Inotrope	\N
11126	Jason Hom	40	atrial_fibrillation	35846	-5	5	\N	\N
11127	Jonathan Chen	40	atrial_fibrillation	35846	-5	3	Negative Inotrope	\N
11180	Panel Average	40	atrial_fibrillation	35846	-8	\N	\N	\N
11185	Andre Kumar	40	atrial_fibrillation	35846	-8	4	Rate Control	\N
11186	Panel Consensus	40	atrial_fibrillation	35846	-8	\N	\N	\N
11128	Jonathan Chen	43	atrial_fibrillation	35846	-5	3	Negative Inotrope	\N
11177	Lisa Shieh	43	atrial_fibrillation	35846	-7	3	\N	\N
11204	Panel Average	43	atrial_fibrillation	35846	-9	\N	\N	\N
11205	Panel Consensus	43	atrial_fibrillation	35846	-9	\N	\N	\N
11078	Jonathan Chen	43	atrial_fibrillation	44393	-3	3	Negative Inotrope	Not as bad as IV negative inotropes, but still not the right time given hypotensive
11178	Lisa Shieh	43	atrial_fibrillation	44393	-7	3	\N	\N
11187	Andre Kumar	43	atrial_fibrillation	44393	-8	4	Rate Control	\N
11188	Panel Consensus	43	atrial_fibrillation	44393	-8	\N	\N	\N
11201	Panel Average	43	atrial_fibrillation	44393	-8	\N	\N	\N
9440	Panel Average	10	pulmonary_embolism	44586	5	\N	\N	\N
10443	Jonathan Chen	43	atrial_fibrillation	44251	0	1	\N	Maybe they think low-output heart failure? No other signs of such elsewhere. Would this make Afib RVR even worse?
11129	Lisa Shieh	43	atrial_fibrillation	44251	-5	3	\N	\N
11189	Panel Consensus	43	atrial_fibrillation	44251	-8	\N	\N	\N
11202	Panel Average	43	atrial_fibrillation	44251	-8	\N	\N	\N
10444	Andre Kumar	40	atrial_fibrillation	44204	0	5	Unindicated Med	\N
10445	Jonathan Chen	40	atrial_fibrillation	44204	0	2	\N	What is this doing here?
10446	Lisa Shieh	40	atrial_fibrillation	44204	0	5	\N	\N
10990	Panel Average	40	atrial_fibrillation	44204	-2	\N	\N	\N
10997	Panel Consensus	40	atrial_fibrillation	44204	-2	\N	\N	\N
11130	Jason Hom	40	atrial_fibrillation	44204	-5	4	\N	\N
9479	Andre Kumar	43	atrial_fibrillation	45941	4	2	UTOX	\N
9626	Lisa Shieh	43	atrial_fibrillation	45941	3	3	\N	\N
9967	Jonathan Chen	43	atrial_fibrillation	45941	2	3	\N	\N
9968	Panel Consensus	43	atrial_fibrillation	45941	2	\N	\N	\N
10209	Panel Average	43	atrial_fibrillation	45941	2	\N	\N	\N
10998	Jason Hom	43	atrial_fibrillation	45941	-2	5	\N	\N
8237	Panel Average	40	atrial_fibrillation	45866	9	\N	\N	\N
8238	Panel Consensus	40	atrial_fibrillation	45866	9	\N	\N	\N
8479	Andre Kumar	40	atrial_fibrillation	45866	7	5	ECG + Monitoring	\N
8704	Andre Kumar	41	atrial_fibrillation	45866	6	5	ECG + Monitoring	\N
8866	Panel Average	41	atrial_fibrillation	45866	5	\N	\N	\N
8917	Jason Hom	41	atrial_fibrillation	45866	5	4	\N	\N
8918	Lisa Shieh	41	atrial_fibrillation	45866	5	3	\N	\N
8919	Panel Consensus	41	atrial_fibrillation	45866	5	\N	\N	\N
11393	Jonathan Chen	43	atrial_fibrillation	45866	10	5	\N	\N
11335	Jonathan Chen	40	atrial_fibrillation	62176	3	2	Echo	\N
11295	Jonathan Chen	43	atrial_fibrillation	62176	3	2	Echo	Okay for workup, but not while unstable?
9627	Lisa Shieh	40	atrial_fibrillation	45963	3	3	\N	\N
10447	Jonathan Chen	40	atrial_fibrillation	45963	0	1	\N	Reasonable before DCCV IF stable, but since unstable Afib, would take too long
10999	Panel Consensus	40	atrial_fibrillation	45963	-2	\N	\N	\N
11070	Panel Average	40	atrial_fibrillation	45963	-2	\N	\N	\N
11131	Andre Kumar	40	atrial_fibrillation	45963	-5	4	Imaging	"Delays care a fib seems paroxysmal given no PMH"
11132	Jason Hom	40	atrial_fibrillation	45963	-5	4	\N	\N
9628	Lisa Shieh	43	atrial_fibrillation	45963	3	3	\N	\N
10448	Jonathan Chen	43	atrial_fibrillation	45963	0	1	\N	Reasonable before DCCV IF stable, but since unstable Afib, would take too long
11102	Panel Average	43	atrial_fibrillation	45963	-4	\N	\N	\N
11103	Panel Consensus	43	atrial_fibrillation	45963	-4	\N	\N	\N
11133	Andre Kumar	43	atrial_fibrillation	45963	-5	5	Imaging	delays care
8480	Lisa Shieh	40	atrial_fibrillation	61832	7	3	\N	\N
9629	Jonathan Chen	40	atrial_fibrillation	61832	3	2	Echo	Good for Afib workup, but less points if doing it while unstable?
10971	Panel Average	40	atrial_fibrillation	61832	-1	\N	\N	\N
11134	Andre Kumar	40	atrial_fibrillation	61832	-5	3	Imaging	\N
11135	Jason Hom	40	atrial_fibrillation	61832	-5	4	\N	\N
8450	Panel Average	41	atrial_fibrillation	61832	7	\N	\N	\N
8481	Lisa Shieh	41	atrial_fibrillation	61832	7	3	\N	\N
8482	Panel Consensus	41	atrial_fibrillation	61832	7	\N	\N	\N
8920	Andre Kumar	41	atrial_fibrillation	61832	5	5	imaging	\N
9480	Jonathan Chen	41	atrial_fibrillation	61832	4	2	Echo	\N
11136	Andre Kumar	43	atrial_fibrillation	61832	-5	5	Imaging	delays care
11137	Panel Average	43	atrial_fibrillation	61832	-5	\N	\N	\N
8301	Panel Average	40	atrial_fibrillation	46160	8	\N	\N	\N
8336	Panel Consensus	40	atrial_fibrillation	46160	8	\N	\N	\N
8921	Andre Kumar	40	atrial_fibrillation	46160	5	5	Vitals	\N
10449	Jonathan Chen	40	atrial_fibrillation	46160	0	2	\N	\N
11138	Jonathan Chen	43	atrial_fibrillation	44248	-5	3	Negative Inotrope	\N
11139	Lisa Shieh	43	atrial_fibrillation	44248	-5	3	\N	\N
11190	Panel Consensus	43	atrial_fibrillation	44248	-8	\N	\N	\N
11203	Panel Average	43	atrial_fibrillation	44248	-8	\N	\N	\N
8922	Andre Kumar	40	atrial_fibrillation	44297	5	5	Sedation	\N
8923	Jason Hom	40	atrial_fibrillation	44297	5	4	\N	\N
8924	Lisa Shieh	40	atrial_fibrillation	44297	5	3	\N	\N
8925	Panel Average	40	atrial_fibrillation	44297	5	\N	\N	\N
8926	Panel Consensus	40	atrial_fibrillation	44297	5	\N	\N	\N
9969	Jonathan Chen	40	atrial_fibrillation	44297	2	2	Pre-DCCV	\N
8927	Jason Hom	43	atrial_fibrillation	44297	5	5	\N	\N
9927	Panel Average	43	atrial_fibrillation	44297	2	\N	\N	\N
9970	Andre Kumar	43	atrial_fibrillation	44297	2	2	Sedation	\N
9971	Jonathan Chen	43	atrial_fibrillation	44297	2	2	Pre-DCCV	\N
9972	Panel Consensus	43	atrial_fibrillation	44297	2	\N	\N	\N
10450	Lisa Shieh	43	atrial_fibrillation	44297	0	3	\N	\N
10451	Andre Kumar	40	atrial_fibrillation	46230	0	5	Unindicated Med	\N
10452	Jonathan Chen	40	atrial_fibrillation	46230	0	2	\N	What is this doing here?
10453	Lisa Shieh	40	atrial_fibrillation	46230	0	3	\N	\N
10991	Panel Average	40	atrial_fibrillation	46230	-2	\N	\N	\N
11000	Panel Consensus	40	atrial_fibrillation	46230	-2	\N	\N	\N
11140	Jason Hom	40	atrial_fibrillation	46230	-5	4	\N	\N
10454	Jonathan Chen	40	atrial_fibrillation	44004	0	1	\N	Bad if already hypotensive, or maybe think is volume overload causing the Afib?
11141	Jason Hom	40	atrial_fibrillation	44004	-5	5	\N	\N
11142	Lisa Shieh	40	atrial_fibrillation	44004	-5	3	\N	\N
11174	Panel Consensus	40	atrial_fibrillation	44004	-6	\N	\N	\N
11176	Panel Average	40	atrial_fibrillation	44004	-6	\N	\N	\N
11206	Andre Kumar	40	atrial_fibrillation	44004	-9	5	Diuretics	\N
8928	Jason Hom	41	atrial_fibrillation	44004	5	4	\N	\N
9928	Panel Average	41	atrial_fibrillation	44004	2	\N	\N	\N
9973	Andre Kumar	41	atrial_fibrillation	44004	2	2	Diuretics	\N
9974	Panel Consensus	41	atrial_fibrillation	44004	2	\N	\N	\N
10455	Jonathan Chen	41	atrial_fibrillation	44004	0	1	\N	Bad if already hypotensive, or maybe think is volume overload causing the Afib?
10456	Lisa Shieh	41	atrial_fibrillation	44004	0	3	\N	\N
10457	Jonathan Chen	43	atrial_fibrillation	44004	0	1	\N	Bad if already hypotensive, or maybe think is volume overload causing the Afib?
11143	Lisa Shieh	43	atrial_fibrillation	44004	-5	3	\N	\N
11181	Panel Average	43	atrial_fibrillation	44004	-8	\N	\N	\N
11191	Andre Kumar	43	atrial_fibrillation	44004	-8	3	Diuretics	\N
11192	Panel Consensus	43	atrial_fibrillation	44004	-8	\N	\N	\N
11381	Jonathan Chen	40	atrial_fibrillation	50343	0	0	\N	\N
8929	Jason Hom	41	atrial_fibrillation	45797	5	4	\N	\N
9630	Panel Consensus	41	atrial_fibrillation	45797	3	\N	\N	\N
9925	Panel Average	41	atrial_fibrillation	45797	3	\N	\N	\N
10405	Lisa Shieh	41	atrial_fibrillation	45797	0	3	\N	\N
10458	Andre Kumar	41	atrial_fibrillation	45797	0	3	Diabetes	\N
10459	Jonathan Chen	41	atrial_fibrillation	45797	0	2	\N	\N
7546	Jason Hom	40	atrial_fibrillation	44359	10	5	\N	\N
8483	Panel Consensus	40	atrial_fibrillation	44359	7	\N	\N	\N
8661	Panel Average	40	atrial_fibrillation	44359	7	\N	\N	\N
8930	Andre Kumar	40	atrial_fibrillation	44359	5	4	Anticoagulants	\N
8931	Jonathan Chen	40	atrial_fibrillation	44359	5	3	Anticoagulation	\N
8932	Lisa Shieh	40	atrial_fibrillation	44359	5	3	\N	\N
7547	Andre Kumar	41	atrial_fibrillation	44359	10	5	Anticoagulants	No positive points if combined wiht other anticoagulants
7548	Jason Hom	41	atrial_fibrillation	44359	10	5	\N	\N
8239	Panel Average	41	atrial_fibrillation	44359	9	\N	\N	\N
8240	Panel Consensus	41	atrial_fibrillation	44359	9	\N	\N	\N
8484	Lisa Shieh	41	atrial_fibrillation	44359	7	3	\N	\N
8933	Jonathan Chen	41	atrial_fibrillation	44359	5	3	Anticoagulation	\N
7549	Jason Hom	43	atrial_fibrillation	44359	10	5	\N	\N
8302	Panel Average	43	atrial_fibrillation	44359	8	\N	\N	\N
8337	Andre Kumar	43	atrial_fibrillation	44359	8	4	Anticoagulants	\N
8338	Panel Consensus	43	atrial_fibrillation	44359	8	\N	\N	\N
8485	Lisa Shieh	43	atrial_fibrillation	44359	7	3	\N	\N
8934	Jonathan Chen	43	atrial_fibrillation	44359	5	3	Anticoagulation	\N
7550	Jason Hom	40	atrial_fibrillation	46183	10	5	\N	\N
8681	Panel Average	40	atrial_fibrillation	46183	6	\N	\N	\N
8705	Panel Consensus	40	atrial_fibrillation	46183	6	\N	\N	\N
8935	Lisa Shieh	40	atrial_fibrillation	46183	5	3	\N	\N
9481	Andre Kumar	40	atrial_fibrillation	46183	4	4	Anticoagulants	\N
10460	Jonathan Chen	40	atrial_fibrillation	46183	0	2	\N	\N
7551	Jason Hom	40	atrial_fibrillation	63714	10	5	\N	\N
8682	Panel Average	40	atrial_fibrillation	63714	6	\N	\N	\N
8706	Panel Consensus	40	atrial_fibrillation	63714	6	\N	\N	\N
8936	Lisa Shieh	40	atrial_fibrillation	63714	5	\N	\N	\N
9482	Andre Kumar	40	atrial_fibrillation	63714	4	2	Coags	\N
10461	Jonathan Chen	40	atrial_fibrillation	63714	0	2	\N	\N
9975	Andre Kumar	43	atrial_fibrillation	63714	2	3	Anticoagulants	\N
9976	Panel Average	43	atrial_fibrillation	63714	2	\N	\N	\N
9977	Andre Kumar	40	atrial_fibrillation	49301	2	4	Blood Gas	\N
10249	Jonathan Chen	40	atrial_fibrillation	49301	1	2	Blood Gas	\N
10250	Panel Consensus	40	atrial_fibrillation	49301	1	\N	\N	\N
10381	Panel Average	40	atrial_fibrillation	49301	1	\N	\N	\N
10462	Jason Hom	40	atrial_fibrillation	49301	0	5	\N	\N
10463	Lisa Shieh	40	atrial_fibrillation	49301	0	3	\N	\N
7552	Jason Hom	40	atrial_fibrillation	45888	10	5	\N	\N
9598	Panel Average	40	atrial_fibrillation	45888	3	\N	\N	\N
10251	Jonathan Chen	40	atrial_fibrillation	45888	1	2	Blood Gas	\N
10252	Panel Consensus	40	atrial_fibrillation	45888	1	\N	\N	\N
10464	Andre Kumar	40	atrial_fibrillation	45888	0	4	Blood Gas	\N
10465	Lisa Shieh	40	atrial_fibrillation	45888	0	3	\N	\N
10253	Jonathan Chen	43	atrial_fibrillation	48732	1	2	Blood Gas	\N
10254	Panel Consensus	43	atrial_fibrillation	48732	1	\N	\N	\N
10466	Andre Kumar	43	atrial_fibrillation	48732	0	2	Blood Gases	\N
10467	Jason Hom	43	atrial_fibrillation	48732	0	5	\N	\N
10468	Lisa Shieh	43	atrial_fibrillation	48732	0	3	\N	\N
10469	Panel Average	43	atrial_fibrillation	48732	0	\N	\N	\N
7553	Jason Hom	40	atrial_fibrillation	45942	10	5	\N	\N
8937	Panel Average	40	atrial_fibrillation	45942	5	\N	\N	\N
8938	Panel Consensus	40	atrial_fibrillation	45942	5	\N	\N	\N
9631	Lisa Shieh	40	atrial_fibrillation	45942	3	3	\N	\N
9978	Andre Kumar	40	atrial_fibrillation	45942	2	3	Coags	\N
10470	Jonathan Chen	40	atrial_fibrillation	45942	0	2	\N	\N
7554	Jason Hom	40	atrial_fibrillation	45838	10	5	\N	\N
8707	Jonathan Chen	40	atrial_fibrillation	45838	6	4	Troponin	\N
8708	Panel Average	40	atrial_fibrillation	45838	6	\N	\N	\N
8709	Panel Consensus	40	atrial_fibrillation	45838	6	\N	\N	\N
8939	Lisa Shieh	40	atrial_fibrillation	45838	5	3	\N	\N
9632	Andre Kumar	40	atrial_fibrillation	45838	3	4	Troponin	\N
8940	Jason Hom	40	atrial_fibrillation	62151	5	4	\N	\N
8941	Jonathan Chen	40	atrial_fibrillation	62151	5	3	Lactate	\N
9599	Panel Average	40	atrial_fibrillation	62151	3	\N	\N	\N
9633	Lisa Shieh	40	atrial_fibrillation	62151	3	3	\N	\N
9634	Panel Consensus	40	atrial_fibrillation	62151	3	\N	\N	\N
9979	Andre Kumar	40	atrial_fibrillation	62151	2	2	Lactate	\N
8942	Jonathan Chen	41	atrial_fibrillation	62151	5	3	Lactate	\N
9635	Lisa Shieh	41	atrial_fibrillation	62151	3	3	\N	\N
9980	Andre Kumar	41	atrial_fibrillation	62151	2	2	Lactate	\N
9981	Panel Consensus	41	atrial_fibrillation	62151	2	\N	\N	\N
10210	Panel Average	41	atrial_fibrillation	62151	2	\N	\N	\N
10471	Jason Hom	41	atrial_fibrillation	62151	0	4	\N	\N
8943	Jason Hom	41	atrial_fibrillation	46011	5	4	\N	\N
8944	Lisa Shieh	41	atrial_fibrillation	46011	5	3	\N	\N
9600	Panel Average	41	atrial_fibrillation	46011	3	\N	\N	\N
9636	Panel Consensus	41	atrial_fibrillation	46011	3	\N	\N	\N
10472	Andre Kumar	41	atrial_fibrillation	46011	0	2	Lipid Panel	\N
10473	Jonathan Chen	41	atrial_fibrillation	46011	0	2	\N	\N
8945	Jason Hom	41	atrial_fibrillation	61837	5	4	\N	\N
8946	Lisa Shieh	41	atrial_fibrillation	61837	5	3	\N	\N
9601	Panel Average	41	atrial_fibrillation	61837	3	\N	\N	\N
9637	Panel Consensus	41	atrial_fibrillation	61837	3	\N	\N	\N
10474	Andre Kumar	41	atrial_fibrillation	61837	0	2	Lipid Panel	\N
10475	Jonathan Chen	41	atrial_fibrillation	61837	0	2	\N	\N
11455	Jonathan Chen	43	atrial_fibrillation	61837	0	2	\N	\N
11207	Andre Kumar	40	atrial_fibrillation	44276	-9	5	Sedation	Patient lethargic and lorezepam not good for procedural sedation
11208	Panel Average	40	atrial_fibrillation	44276	-9	\N	\N	\N
7555	Jason Hom	40	atrial_fibrillation	45806	10	5	\N	\N
8486	Lisa Shieh	40	atrial_fibrillation	45806	7	5	\N	\N
8683	Panel Average	40	atrial_fibrillation	45806	6	\N	\N	\N
8710	Panel Consensus	40	atrial_fibrillation	45806	6	\N	\N	\N
9982	Andre Kumar	40	atrial_fibrillation	45806	2	3	Metabolic Panel	\N
9983	Jonathan Chen	40	atrial_fibrillation	45806	2	3	\N	\N
7556	Jason Hom	41	atrial_fibrillation	45806	10	4	\N	\N
8487	Lisa Shieh	41	atrial_fibrillation	45806	7	3	\N	\N
8684	Panel Average	41	atrial_fibrillation	45806	6	\N	\N	\N
8711	Panel Consensus	41	atrial_fibrillation	45806	6	\N	\N	\N
9984	Andre Kumar	41	atrial_fibrillation	45806	2	3	Metabolic Panel	\N
9985	Jonathan Chen	41	atrial_fibrillation	45806	2	3	\N	\N
7557	Jason Hom	40	atrial_fibrillation	45763	10	5	\N	\N
8488	Lisa Shieh	40	atrial_fibrillation	45763	7	3	\N	\N
8489	Panel Consensus	40	atrial_fibrillation	45763	7	\N	\N	\N
8662	Panel Average	40	atrial_fibrillation	45763	7	\N	\N	\N
9638	Andre Kumar	40	atrial_fibrillation	45763	3	3	Metabolic Panel	\N
9639	Jonathan Chen	40	atrial_fibrillation	45763	3	3	Metabolic Panel	\N
11375	Jonathan Chen	41	atrial_fibrillation	45763	3	3	Metabolic Panel	\N
7558	Jason Hom	40	atrial_fibrillation	45771	10	5	\N	\N
8490	Panel Consensus	40	atrial_fibrillation	45771	7	\N	\N	\N
8712	Panel Average	40	atrial_fibrillation	45771	6	\N	\N	\N
8947	Lisa Shieh	40	atrial_fibrillation	45771	5	3	\N	\N
9640	Andre Kumar	40	atrial_fibrillation	45771	3	3	Metabolic Panel	\N
9641	Jonathan Chen	40	atrial_fibrillation	45771	3	3	Metabolic Panel	\N
8491	Lisa Shieh	41	atrial_fibrillation	45771	7	3	\N	\N
8492	Panel Consensus	41	atrial_fibrillation	45771	7	\N	\N	\N
8948	Jason Hom	41	atrial_fibrillation	45771	5	4	\N	\N
9430	Panel Average	41	atrial_fibrillation	45771	5	\N	\N	\N
9642	Jonathan Chen	41	atrial_fibrillation	45771	3	3	Metabolic Panel	\N
9986	Andre Kumar	41	atrial_fibrillation	45771	2	4	Metabolic Panel	\N
8493	Panel Consensus	43	atrial_fibrillation	45771	7	\N	\N	\N
8949	Jason Hom	43	atrial_fibrillation	45771	5	5	\N	\N
8950	Lisa Shieh	43	atrial_fibrillation	45771	5	3	\N	\N
9483	Panel Average	43	atrial_fibrillation	45771	4	\N	\N	\N
9643	Jonathan Chen	43	atrial_fibrillation	45771	3	3	Metabolic Panel	\N
9987	Andre Kumar	43	atrial_fibrillation	45771	2	3	Metabolic Panel	\N
11144	Jason Hom	40	atrial_fibrillation	44327	-5	5	\N	\N
11145	Jonathan Chen	40	atrial_fibrillation	44327	-5	3	Negative Inotrope	\N
11193	Panel Average	40	atrial_fibrillation	44327	-8	\N	\N	\N
11194	Panel Consensus	40	atrial_fibrillation	44327	-8	\N	\N	\N
11209	Andre Kumar	40	atrial_fibrillation	44327	-9	5	Rate Control	\N
8951	Jason Hom	41	atrial_fibrillation	44005	5	4	\N	\N
9484	Panel Consensus	41	atrial_fibrillation	44005	4	\N	\N	\N
9579	Panel Average	41	atrial_fibrillation	44005	4	\N	\N	\N
9644	Andre Kumar	41	atrial_fibrillation	44005	3	2	Rate Control	\N
9645	Jonathan Chen	41	atrial_fibrillation	44005	3	3	\N	Beta-blocker AFTER stabilization reasonable for chronic rate control and or CHF treatment
9646	Lisa Shieh	41	atrial_fibrillation	44005	3	3	\N	\N
8952	Andre Kumar	40	atrial_fibrillation	44000	5	4	Sedation	\N
8953	Jason Hom	40	atrial_fibrillation	44000	5	4	\N	\N
8954	Lisa Shieh	40	atrial_fibrillation	44000	5	3	\N	\N
8955	Panel Average	40	atrial_fibrillation	44000	5	\N	\N	\N
8956	Panel Consensus	40	atrial_fibrillation	44000	5	\N	\N	\N
9988	Jonathan Chen	40	atrial_fibrillation	44000	2	2	Pre-DCCV	\N
8957	Jason Hom	43	atrial_fibrillation	44000	5	5	\N	\N
8958	Lisa Shieh	43	atrial_fibrillation	44000	5	3	\N	\N
9485	Panel Average	43	atrial_fibrillation	44000	4	\N	\N	\N
9486	Panel Consensus	43	atrial_fibrillation	44000	4	\N	\N	\N
9989	Andre Kumar	43	atrial_fibrillation	44000	2	3	Sedation	\N
9990	Jonathan Chen	43	atrial_fibrillation	44000	2	2	Pre-DCCV	\N
11420	Jonathan Chen	40	atrial_fibrillation	44294	2	2	Pre-DCCV	\N
8959	Jason Hom	41	atrial_fibrillation	45792	5	4	\N	\N
10211	Panel Average	41	atrial_fibrillation	45792	2	\N	\N	\N
10476	Andre Kumar	41	atrial_fibrillation	45792	0	5	MRSA Screen	\N
10477	Jonathan Chen	41	atrial_fibrillation	45792	0	2	\N	\N
10478	Lisa Shieh	41	atrial_fibrillation	45792	0	3	\N	\N
10479	Panel Consensus	41	atrial_fibrillation	45792	0	\N	\N	\N
10480	Andre Kumar	43	atrial_fibrillation	45792	0	3	MRSA Screen	\N
10481	Jonathan Chen	43	atrial_fibrillation	45792	0	2	\N	\N
10482	Lisa Shieh	43	atrial_fibrillation	45792	0	3	\N	\N
10966	Panel Average	43	atrial_fibrillation	45792	-1	\N	\N	\N
10972	Panel Consensus	43	atrial_fibrillation	45792	-1	\N	\N	\N
11001	Jason Hom	43	atrial_fibrillation	45792	-2	5	\N	\N
11430	Jonathan Chen	43	atrial_fibrillation	44241	0	2	\N	Trying to relieve preload?
11268	Jonathan Chen	43	atrial_fibrillation	44256	0	2	\N	Trying to relieve preload?
10483	Andre Kumar	40	atrial_fibrillation	48628	0	4	Anticoagulants	\N
10484	Jason Hom	40	atrial_fibrillation	48628	0	4	\N	\N
10485	Jonathan Chen	40	atrial_fibrillation	48628	0	2	\N	\N
10486	Lisa Shieh	40	atrial_fibrillation	48628	0	3	\N	\N
10487	Panel Average	40	atrial_fibrillation	48628	0	\N	\N	\N
10488	Panel Consensus	40	atrial_fibrillation	48628	0	\N	\N	\N
10489	Andre Kumar	40	atrial_fibrillation	46081	0	4	Nursing	\N
10490	Jason Hom	40	atrial_fibrillation	46081	0	4	\N	\N
10491	Jonathan Chen	40	atrial_fibrillation	46081	0	2	\N	\N
10492	Lisa Shieh	40	atrial_fibrillation	46081	0	5	\N	\N
10493	Panel Average	40	atrial_fibrillation	46081	0	\N	\N	\N
10494	Panel Consensus	40	atrial_fibrillation	46081	0	\N	\N	\N
11240	Jonathan Chen	40	atrial_fibrillation	50235	0	3	\N	Not a respiratory issue?
11320	Jonathan Chen	43	atrial_fibrillation	50235	0	3	\N	Not respiratory issue, but maybe thinking manage preload with pulmonary pressure?
11363	Jonathan Chen	43	atrial_fibrillation	36086	0	2	Vasopressor	Adding vasopressor on while hypotensive from negative inotrope?
7559	Jason Hom	40	atrial_fibrillation	45853	10	5	\N	\N
8867	Panel Average	40	atrial_fibrillation	45853	5	\N	\N	\N
8960	Panel Consensus	40	atrial_fibrillation	45853	5	\N	\N	\N
9487	Jonathan Chen	40	atrial_fibrillation	45853	4	4	\N	\N
9647	Andre Kumar	40	atrial_fibrillation	45853	3	4	BNP	\N
9648	Lisa Shieh	40	atrial_fibrillation	45853	3	3	\N	\N
8961	Jason Hom	41	atrial_fibrillation	45853	5	4	\N	\N
8962	Panel Consensus	41	atrial_fibrillation	45853	5	\N	\N	\N
9488	Jonathan Chen	41	atrial_fibrillation	45853	4	4	\N	\N
8185	Jason Hom	10	pulmonary_embolism	45830	10	5	\N	\N
9580	Panel Average	41	atrial_fibrillation	45853	4	\N	\N	\N
9649	Andre Kumar	41	atrial_fibrillation	45853	3	4	BNP	\N
9650	Lisa Shieh	41	atrial_fibrillation	45853	3	3	\N	\N
8963	Jason Hom	43	atrial_fibrillation	45853	5	5	\N	\N
8964	Lisa Shieh	43	atrial_fibrillation	45853	5	3	\N	\N
8965	Panel Consensus	43	atrial_fibrillation	45853	5	\N	\N	\N
9446	Panel Average	43	atrial_fibrillation	45853	4	\N	\N	\N
9489	Jonathan Chen	43	atrial_fibrillation	45853	4	4	\N	\N
9651	Andre Kumar	43	atrial_fibrillation	45853	3	3	BNP	\N
8966	Jason Hom	40	atrial_fibrillation	45787	5	4	\N	\N
10212	Panel Average	40	atrial_fibrillation	45787	2	\N	\N	\N
10495	Andre Kumar	40	atrial_fibrillation	45787	0	5	PT/OT	\N
10496	Jonathan Chen	40	atrial_fibrillation	45787	0	2	\N	\N
10497	Lisa Shieh	40	atrial_fibrillation	45787	0	5	\N	\N
10498	Panel Consensus	40	atrial_fibrillation	45787	0	\N	\N	\N
11339	Jonathan Chen	41	atrial_fibrillation	45787	0	3	\N	\N
7560	Jason Hom	40	atrial_fibrillation	45864	10	5	\N	\N
8713	Panel Consensus	40	atrial_fibrillation	45864	6	\N	\N	\N
8843	Panel Average	40	atrial_fibrillation	45864	6	\N	\N	\N
8967	Lisa Shieh	40	atrial_fibrillation	45864	5	3	\N	\N
9991	Andre Kumar	40	atrial_fibrillation	45864	2	2	Oxygen	\N
10499	Jonathan Chen	40	atrial_fibrillation	45864	0	2	\N	\N
11463	Jonathan Chen	40	atrial_fibrillation	48822	0	0	Oxygen	\N
11398	Jonathan Chen	43	atrial_fibrillation	48822	0	2	Oxygen	\N
7561	Jason Hom	40	atrial_fibrillation	45900	10	5	\N	\N
8714	Panel Consensus	40	atrial_fibrillation	45900	6	\N	\N	\N
8844	Panel Average	40	atrial_fibrillation	45900	6	\N	\N	\N
8968	Lisa Shieh	40	atrial_fibrillation	45900	5	3	\N	\N
9992	Andre Kumar	40	atrial_fibrillation	45900	2	2	Oxygen	\N
10500	Jonathan Chen	40	atrial_fibrillation	45900	0	2	\N	\N
11286	Jonathan Chen	43	atrial_fibrillation	45900	0	2	Oxygen	\N
7562	Lisa Shieh	40	atrial_fibrillation	61823	10	5	\N	\N
7563	Panel Consensus	40	atrial_fibrillation	61823	10	\N	\N	\N
9929	Panel Average	40	atrial_fibrillation	61823	2	\N	\N	\N
9993	Andre Kumar	40	atrial_fibrillation	61823	2	4	Nursing	\N
10501	Jonathan Chen	40	atrial_fibrillation	61823	0	2	\N	\N
11146	Jason Hom	40	atrial_fibrillation	61823	-5	5	\N	\N
11263	Jonathan Chen	43	atrial_fibrillation	43993	0	0	Vasopressor	\N
7564	Jason Hom	40	atrial_fibrillation	45778	10	5	\N	\N
8969	Lisa Shieh	40	atrial_fibrillation	45778	5	3	\N	\N
8970	Panel Average	40	atrial_fibrillation	45778	5	\N	\N	\N
10255	Panel Consensus	40	atrial_fibrillation	45778	1	\N	\N	\N
10502	Andre Kumar	40	atrial_fibrillation	45778	0	3	Metabolic Panel	\N
10503	Jonathan Chen	40	atrial_fibrillation	45778	0	2	\N	\N
9994	Andre Kumar	41	atrial_fibrillation	45778	2	4	Metabolic Panel	\N
9995	Panel Average	41	atrial_fibrillation	45778	2	\N	\N	\N
8971	Jason Hom	43	atrial_fibrillation	45778	5	5	\N	\N
8972	Lisa Shieh	43	atrial_fibrillation	45778	5	\N	\N	\N
9447	Panel Average	43	atrial_fibrillation	45778	4	\N	\N	\N
9652	Andre Kumar	43	atrial_fibrillation	45778	3	2	Metabolic Panel	\N
10256	Panel Consensus	43	atrial_fibrillation	45778	1	\N	\N	\N
10504	Jonathan Chen	43	atrial_fibrillation	45778	0	2	\N	\N
9653	Lisa Shieh	40	atrial_fibrillation	46090	3	3	\N	\N
9654	Panel Consensus	40	atrial_fibrillation	46090	3	\N	\N	\N
10232	Panel Average	40	atrial_fibrillation	46090	1	\N	\N	\N
10257	Andre Kumar	40	atrial_fibrillation	46090	1	3	CBC	\N
10505	Jason Hom	40	atrial_fibrillation	46090	0	4	\N	\N
10506	Jonathan Chen	40	atrial_fibrillation	46090	0	2	\N	\N
7565	Jason Hom	40	atrial_fibrillation	45914	10	5	\N	\N
8715	Jonathan Chen	40	atrial_fibrillation	45914	6	4	Troponin	\N
8716	Panel Average	40	atrial_fibrillation	45914	6	\N	\N	\N
8717	Panel Consensus	40	atrial_fibrillation	45914	6	\N	\N	\N
8973	Lisa Shieh	40	atrial_fibrillation	45914	5	3	\N	\N
9655	Andre Kumar	40	atrial_fibrillation	45914	3	3	Troponin	\N
11256	Jonathan Chen	43	atrial_fibrillation	46185	1	2	Blood Gas	\N
11354	Jonathan Chen	40	atrial_fibrillation	46067	3	3	Metabolic Panel	\N
8974	Jason Hom	40	atrial_fibrillation	45955	5	4	\N	\N
8975	Jonathan Chen	40	atrial_fibrillation	45955	5	3	Lactate	\N
10213	Panel Average	40	atrial_fibrillation	45955	2	\N	\N	\N
10258	Panel Consensus	40	atrial_fibrillation	45955	1	\N	\N	\N
10507	Andre Kumar	40	atrial_fibrillation	45955	0	4	Blood Gas	\N
10508	Lisa Shieh	40	atrial_fibrillation	45955	0	3	\N	\N
8976	Jonathan Chen	43	atrial_fibrillation	45955	5	3	Lactate	\N
9996	Andre Kumar	43	atrial_fibrillation	45955	2	2	Blood Gases	\N
10259	Panel Consensus	43	atrial_fibrillation	45955	1	\N	\N	\N
10509	Jason Hom	43	atrial_fibrillation	45955	0	5	\N	\N
10973	Panel Average	43	atrial_fibrillation	45955	-1	\N	\N	\N
11147	Lisa Shieh	43	atrial_fibrillation	45955	-5	3	\N	\N
9997	Andre Kumar	43	atrial_fibrillation	46000	2	1	Urinalysis	\N
10510	Jonathan Chen	43	atrial_fibrillation	46000	0	2	\N	\N
10511	Lisa Shieh	43	atrial_fibrillation	46000	0	3	\N	\N
10512	Panel Average	43	atrial_fibrillation	46000	0	\N	\N	\N
10513	Panel Consensus	43	atrial_fibrillation	46000	0	\N	\N	\N
11002	Jason Hom	43	atrial_fibrillation	46000	-2	5	\N	\N
7566	Jason Hom	40	atrial_fibrillation	45759	10	5	\N	\N
8977	Panel Average	40	atrial_fibrillation	45759	5	\N	\N	\N
8978	Panel Consensus	40	atrial_fibrillation	45759	5	\N	\N	\N
9656	Lisa Shieh	40	atrial_fibrillation	45759	3	3	\N	\N
9998	Andre Kumar	40	atrial_fibrillation	45759	2	3	Coags	\N
10514	Jonathan Chen	40	atrial_fibrillation	45759	0	2	\N	\N
7567	Jason Hom	41	atrial_fibrillation	45759	10	4	\N	\N
8494	Lisa Shieh	41	atrial_fibrillation	45759	7	3	\N	\N
8663	Panel Average	41	atrial_fibrillation	45759	7	\N	\N	\N
8979	Panel Consensus	41	atrial_fibrillation	45759	5	\N	\N	\N
9657	Andre Kumar	41	atrial_fibrillation	45759	3	4	Coags	\N
10515	Jonathan Chen	41	atrial_fibrillation	45759	0	2	\N	\N
8980	Jason Hom	43	atrial_fibrillation	45759	5	5	\N	\N
8981	Panel Consensus	43	atrial_fibrillation	45759	5	\N	\N	\N
9581	Panel Average	43	atrial_fibrillation	45759	4	\N	\N	\N
9658	Andre Kumar	43	atrial_fibrillation	45759	3	3	Coags	\N
9659	Lisa Shieh	43	atrial_fibrillation	45759	3	3	\N	\N
10516	Jonathan Chen	43	atrial_fibrillation	45759	0	2	\N	\N
8982	Jason Hom	40	atrial_fibrillation	45776	5	4	\N	\N
10214	Panel Average	40	atrial_fibrillation	45776	2	\N	\N	\N
10517	Andre Kumar	40	atrial_fibrillation	45776	0	5	PT/OT	\N
10518	Jonathan Chen	40	atrial_fibrillation	45776	0	2	\N	\N
10519	Lisa Shieh	40	atrial_fibrillation	45776	0	6	\N	\N
10520	Panel Consensus	40	atrial_fibrillation	45776	0	\N	\N	\N
11312	Jonathan Chen	41	atrial_fibrillation	45776	0	3	\N	\N
7568	Jason Hom	40	atrial_fibrillation	45770	10	5	\N	\N
8983	Panel Average	40	atrial_fibrillation	45770	5	\N	\N	\N
8984	Panel Consensus	40	atrial_fibrillation	45770	5	\N	\N	\N
9660	Lisa Shieh	40	atrial_fibrillation	45770	3	3	\N	\N
9999	Andre Kumar	40	atrial_fibrillation	45770	2	3	Coags	\N
10521	Jonathan Chen	40	atrial_fibrillation	45770	0	2	\N	\N
9661	Andre Kumar	41	atrial_fibrillation	45770	3	4	Coags	\N
9662	Panel Average	41	atrial_fibrillation	45770	3	\N	\N	\N
8495	Lisa Shieh	43	atrial_fibrillation	45770	7	3	\N	\N
8985	Jason Hom	43	atrial_fibrillation	45770	5	5	\N	\N
8986	Panel Average	43	atrial_fibrillation	45770	5	\N	\N	\N
8987	Panel Consensus	43	atrial_fibrillation	45770	5	\N	\N	\N
9663	Andre Kumar	43	atrial_fibrillation	45770	3	3	Coags	\N
10522	Jonathan Chen	43	atrial_fibrillation	45770	0	2	\N	\N
11364	Jonathan Chen	43	atrial_fibrillation	49995	0	2	\N	\N
7569	Jason Hom	40	atrial_fibrillation	60178	10	5	\N	\N
8988	Jonathan Chen	40	atrial_fibrillation	60178	5	3	Anticoagulation	Oral admin, is this too slow, and so should be worth less points?
9664	Lisa Shieh	40	atrial_fibrillation	60178	3	3	\N	\N
10215	Panel Average	40	atrial_fibrillation	60178	2	\N	\N	\N
11195	Andre Kumar	40	atrial_fibrillation	60178	-8	4	Anticoagulants	"Per Warden et al (JAHA 2018 PMID 30571504): highest risk of stroke is within 48hrs after cardioversion, and most DOACS take 4-5 doses to reach steady state (e.g. >48 hrs). No prospective trial data evaluating DOACS + EMERGENT DCCV. A few weak trials sugge (...)"
7570	Jason Hom	41	atrial_fibrillation	60178	10	5	\N	\N
8496	Lisa Shieh	41	atrial_fibrillation	60178	7	3	\N	\N
8989	Jonathan Chen	41	atrial_fibrillation	60178	5	3	Anticoagulation	Oral admin, is this too slow, and so should be worth less points?
9665	Panel Average	41	atrial_fibrillation	60178	3	\N	\N	\N
11196	Andre Kumar	41	atrial_fibrillation	60178	-8	5	Anticoagulants	\N
11288	Jonathan Chen	43	atrial_fibrillation	60178	5	3	Anticoagulation	Oral admin, is this too slow, and so should be worth less points?
10523	Andre Kumar	40	atrial_fibrillation	44312	0	5	Statin	\N
10524	Jason Hom	40	atrial_fibrillation	44312	0	4	\N	\N
10525	Jonathan Chen	40	atrial_fibrillation	44312	0	2	\N	\N
10526	Lisa Shieh	40	atrial_fibrillation	44312	0	3	\N	\N
10527	Panel Average	40	atrial_fibrillation	44312	0	\N	\N	\N
8990	Jonathan Chen	40	atrial_fibrillation	63725	5	3	Lactate	\N
9666	Lisa Shieh	40	atrial_fibrillation	63725	3	3	\N	\N
10000	Andre Kumar	40	atrial_fibrillation	63725	2	2	Lactate	\N
10001	Panel Consensus	40	atrial_fibrillation	63725	2	\N	\N	\N
10216	Panel Average	40	atrial_fibrillation	63725	2	\N	\N	\N
10528	Jason Hom	40	atrial_fibrillation	63725	0	4	\N	\N
8497	Lisa Shieh	40	atrial_fibrillation	44198	7	3	\N	\N
8991	Jason Hom	40	atrial_fibrillation	44198	5	4	\N	\N
9490	Jonathan Chen	40	atrial_fibrillation	44198	4	2	\N	Reasonable to attempt, but no indication of dehydration as etiology?
10260	Panel Average	40	atrial_fibrillation	44198	1	\N	\N	\N
11003	Panel Consensus	40	atrial_fibrillation	44198	-2	\N	\N	\N
11210	Andre Kumar	40	atrial_fibrillation	44198	-9	5	Fluids	Patient already shows signs of volume overload
8498	Lisa Shieh	43	atrial_fibrillation	44198	7	3	\N	\N
8992	Jason Hom	43	atrial_fibrillation	44198	5	5	\N	\N
9491	Jonathan Chen	43	atrial_fibrillation	44198	4	2	\N	Reasonable to attempt, but no indication of dehydration as etiology?
9930	Panel Average	43	atrial_fibrillation	44198	2	\N	\N	\N
11004	Panel Consensus	43	atrial_fibrillation	44198	-2	\N	\N	\N
11148	Andre Kumar	43	atrial_fibrillation	44198	-5	4	Fluids	\N
7571	Jason Hom	40	atrial_fibrillation	45870	10	5	\N	\N
8718	Jonathan Chen	40	atrial_fibrillation	45870	6	4	Troponin	\N
8719	Panel Average	40	atrial_fibrillation	45870	6	\N	\N	\N
8720	Panel Consensus	40	atrial_fibrillation	45870	6	\N	\N	\N
8993	Lisa Shieh	40	atrial_fibrillation	45870	5	3	\N	\N
9667	Andre Kumar	40	atrial_fibrillation	45870	3	2	Troponin	\N
8721	Jonathan Chen	41	atrial_fibrillation	45870	6	4	Troponin	\N
8722	Panel Consensus	41	atrial_fibrillation	45870	6	\N	\N	\N
8994	Jason Hom	41	atrial_fibrillation	45870	5	4	\N	\N
8995	Lisa Shieh	41	atrial_fibrillation	45870	5	3	\N	\N
9448	Panel Average	41	atrial_fibrillation	45870	4	\N	\N	\N
9668	Andre Kumar	41	atrial_fibrillation	45870	3	4	Troponin	\N
8723	Jonathan Chen	43	atrial_fibrillation	45870	6	4	Troponin	\N
8724	Panel Consensus	43	atrial_fibrillation	45870	6	\N	\N	\N
8996	Jason Hom	43	atrial_fibrillation	45870	5	5	\N	\N
8997	Lisa Shieh	43	atrial_fibrillation	45870	5	3	\N	\N
9492	Panel Average	43	atrial_fibrillation	45870	4	\N	\N	\N
10002	Andre Kumar	43	atrial_fibrillation	45870	2	4	Troponin	\N
7572	Jason Hom	40	atrial_fibrillation	62105	10	5	\N	\N
8499	Panel Consensus	40	atrial_fibrillation	62105	7	\N	\N	\N
8664	Panel Average	40	atrial_fibrillation	62105	7	\N	\N	\N
8998	Andre Kumar	40	atrial_fibrillation	62105	5	5	Thyroid	\N
8999	Lisa Shieh	40	atrial_fibrillation	62105	5	3	\N	\N
9669	Jonathan Chen	40	atrial_fibrillation	62105	3	4	\N	\N
7573	Jason Hom	41	atrial_fibrillation	62105	10	5	\N	\N
8500	Panel Consensus	41	atrial_fibrillation	62105	7	\N	\N	\N
8665	Panel Average	41	atrial_fibrillation	62105	7	\N	\N	\N
9000	Andre Kumar	41	atrial_fibrillation	62105	5	5	Thyroid	If not done before
9001	Lisa Shieh	41	atrial_fibrillation	62105	5	3	\N	\N
9670	Jonathan Chen	41	atrial_fibrillation	62105	3	4	\N	\N
10529	Andre Kumar	40	atrial_fibrillation	45945	0	3	Type and Screen	\N
10530	Jason Hom	40	atrial_fibrillation	45945	0	4	\N	\N
10531	Jonathan Chen	40	atrial_fibrillation	45945	0	2	\N	\N
10532	Lisa Shieh	40	atrial_fibrillation	45945	0	3	\N	\N
10533	Panel Average	40	atrial_fibrillation	45945	0	\N	\N	\N
10534	Panel Consensus	40	atrial_fibrillation	45945	0	\N	\N	\N
10003	Andre Kumar	43	atrial_fibrillation	45945	2	3	Type and Screen	\N
10535	Jonathan Chen	43	atrial_fibrillation	45945	0	2	\N	\N
10536	Lisa Shieh	43	atrial_fibrillation	45945	0	3	\N	\N
10537	Panel Average	43	atrial_fibrillation	45945	0	\N	\N	\N
10538	Panel Consensus	43	atrial_fibrillation	45945	0	\N	\N	\N
11005	Jason Hom	43	atrial_fibrillation	45945	-2	5	\N	\N
9671	Jonathan Chen	40	atrial_fibrillation	65656	3	3	DVT US	\N
10539	Lisa Shieh	40	atrial_fibrillation	65656	0	3	\N	\N
10974	Panel Consensus	40	atrial_fibrillation	65656	-1	\N	\N	\N
10985	Panel Average	40	atrial_fibrillation	65656	-1	\N	\N	\N
11006	Andre Kumar	40	atrial_fibrillation	65656	-2	1	Imaging	\N
11007	Jason Hom	40	atrial_fibrillation	65656	-2	4	\N	\N
9672	Jonathan Chen	41	atrial_fibrillation	65656	3	3	DVT US	\N
10540	Andre Kumar	41	atrial_fibrillation	65656	0	5	Imaging	\N
10541	Lisa Shieh	41	atrial_fibrillation	65656	0	3	\N	\N
10967	Panel Average	41	atrial_fibrillation	65656	-1	\N	\N	\N
10975	Panel Consensus	41	atrial_fibrillation	65656	-1	\N	\N	\N
11008	Jason Hom	41	atrial_fibrillation	65656	-2	4	\N	\N
9673	Jonathan Chen	40	atrial_fibrillation	65692	3	3	DVT US	\N
10542	Lisa Shieh	40	atrial_fibrillation	65692	0	3	\N	\N
10976	Panel Consensus	40	atrial_fibrillation	65692	-1	\N	\N	\N
10986	Panel Average	40	atrial_fibrillation	65692	-1	\N	\N	\N
11009	Andre Kumar	40	atrial_fibrillation	65692	-2	1	Imaging	\N
11010	Jason Hom	40	atrial_fibrillation	65692	-2	4	\N	\N
9674	Jonathan Chen	41	atrial_fibrillation	65692	3	3	DVT US	\N
10543	Andre Kumar	41	atrial_fibrillation	65692	0	5	Imaging	\N
10544	Lisa Shieh	41	atrial_fibrillation	65692	0	3	\N	\N
10968	Panel Average	41	atrial_fibrillation	65692	-1	\N	\N	\N
10977	Panel Consensus	41	atrial_fibrillation	65692	-1	\N	\N	\N
11011	Jason Hom	41	atrial_fibrillation	65692	-2	4	\N	\N
10545	Andre Kumar	41	atrial_fibrillation	45751	0	4	Urinalysis	\N
10546	Jason Hom	41	atrial_fibrillation	45751	0	4	\N	\N
10547	Jonathan Chen	41	atrial_fibrillation	45751	0	2	\N	Not sure what they're looking for
10548	Lisa Shieh	41	atrial_fibrillation	45751	0	3	\N	\N
10549	Panel Average	41	atrial_fibrillation	45751	0	\N	\N	\N
10550	Panel Consensus	41	atrial_fibrillation	45751	0	\N	\N	\N
11474	Jonathan Chen	40	atrial_fibrillation	46236	2	3	\N	EtOH as part of Afib eval?
7574	Jason Hom	40	atrial_fibrillation	45818	10	5	\N	\N
8501	Lisa Shieh	40	atrial_fibrillation	45818	7	5	\N	\N
9675	Jonathan Chen	40	atrial_fibrillation	45818	3	3	CXR	\N
9676	Panel Average	40	atrial_fibrillation	45818	3	\N	\N	\N
11079	Panel Consensus	40	atrial_fibrillation	45818	-3	\N	\N	\N
11197	Andre Kumar	40	atrial_fibrillation	45818	-8	3	Imaging	\N
8502	Lisa Shieh	41	atrial_fibrillation	45818	7	3	\N	\N
9002	Jason Hom	41	atrial_fibrillation	45818	5	4	\N	\N
9003	Panel Average	41	atrial_fibrillation	45818	5	\N	\N	\N
9677	Andre Kumar	41	atrial_fibrillation	45818	3	3	Imaging	\N
9678	Jonathan Chen	41	atrial_fibrillation	45818	3	3	CXR	\N
9679	Panel Consensus	41	atrial_fibrillation	45818	3	\N	\N	\N
9004	Jason Hom	43	atrial_fibrillation	45818	5	5	\N	\N
9005	Lisa Shieh	43	atrial_fibrillation	45818	5	3	\N	\N
9680	Jonathan Chen	43	atrial_fibrillation	45818	3	3	CXR	\N
9913	Panel Average	43	atrial_fibrillation	45818	3	\N	\N	\N
11012	Andre Kumar	43	atrial_fibrillation	45818	-2	2	Imaging	delays care
11080	Panel Consensus	43	atrial_fibrillation	45818	-3	\N	\N	\N
7575	Jason Hom	40	atrial_fibrillation	50200	10	5	\N	\N
8503	Lisa Shieh	40	atrial_fibrillation	50200	7	3	\N	\N
9006	Panel Average	40	atrial_fibrillation	50200	5	\N	\N	\N
9681	Jonathan Chen	40	atrial_fibrillation	50200	3	3	CXR	\N
9682	Panel Consensus	40	atrial_fibrillation	50200	3	\N	\N	\N
11013	Andre Kumar	40	atrial_fibrillation	50200	-2	2	Imaging	Delays care
8504	Lisa Shieh	41	atrial_fibrillation	50200	7	3	\N	\N
9007	Jason Hom	41	atrial_fibrillation	50200	5	4	\N	\N
9008	Panel Average	41	atrial_fibrillation	50200	5	\N	\N	\N
9683	Andre Kumar	41	atrial_fibrillation	50200	3	3	Imaging	\N
9684	Jonathan Chen	41	atrial_fibrillation	50200	3	3	CXR	\N
9685	Panel Consensus	41	atrial_fibrillation	50200	3	\N	\N	\N
7576	Jason Hom	40	atrial_fibrillation	45801	10	5	\N	\N
8505	Lisa Shieh	40	atrial_fibrillation	45801	7	3	\N	\N
9686	Jonathan Chen	40	atrial_fibrillation	45801	3	3	CXR	\N
9687	Panel Average	40	atrial_fibrillation	45801	3	\N	\N	\N
11081	Andre Kumar	40	atrial_fibrillation	45801	-3	5	Imaging	CXR delays care
11082	Panel Consensus	40	atrial_fibrillation	45801	-3	\N	\N	\N
9009	Jason Hom	43	atrial_fibrillation	45801	5	5	\N	\N
9010	Lisa Shieh	43	atrial_fibrillation	45801	5	3	\N	\N
9688	Jonathan Chen	43	atrial_fibrillation	45801	3	3	CXR	\N
9914	Panel Average	43	atrial_fibrillation	45801	3	\N	\N	\N
11014	Andre Kumar	43	atrial_fibrillation	45801	-2	2	Imaging	delays care
11083	Panel Consensus	43	atrial_fibrillation	45801	-3	\N	\N	\N
9011	Jason Hom	14	gi_bleed	44281	5	4	\N	\N
10382	Panel Average	14	gi_bleed	44281	1	\N	\N	\N
10551	Jonathan Chen	14	gi_bleed	44281	0	2	\N	\N
10552	Lisa Shieh	14	gi_bleed	44281	0	5	\N	\N
10978	Panel Consensus	14	gi_bleed	44281	-1	\N	\N	\N
11084	Andre Kumar	14	gi_bleed	44281	-3	4	Acetaminophen	\N
10261	Andre Kumar	2	gi_bleed	48829	1	2	Pain Medication	\N
10262	Jonathan Chen	2	gi_bleed	48829	1	2	\N	Workup for liver injury. Okay I guess
10263	Panel Consensus	2	gi_bleed	48829	1	\N	\N	\N
10391	Panel Average	2	gi_bleed	48829	0	\N	\N	\N
10553	Jason Hom	2	gi_bleed	48829	0	4	\N	\N
10554	Lisa Shieh	2	gi_bleed	48829	0	3	\N	\N
11280	Jonathan Chen	14	gi_bleed	44416	0	2	\N	Acetaminophen overdose, non-specific hepatitis treatment?
9689	Andre Kumar	14	gi_bleed	45932	3	4	Hepatitis Panel	\N
9690	Panel Average	14	gi_bleed	45932	3	\N	\N	\N
11368	Jonathan Chen	15	gi_bleed	45932	2	2	\N	\N
11366	Jonathan Chen	14	gi_bleed	65641	0	4	\N	\N
11431	Jonathan Chen	16	gi_bleed	65641	0	4	\N	\N
7577	Jason Hom	16	gi_bleed	45814	10	5	\N	\N
7578	Lisa Shieh	16	gi_bleed	45814	10	5	\N	\N
7579	Panel Consensus	16	gi_bleed	45814	10	\N	\N	\N
8303	Panel Average	16	gi_bleed	45814	8	\N	\N	\N
9012	Andre Kumar	16	gi_bleed	45814	5	3	Admit	\N
10555	Jonathan Chen	16	gi_bleed	45814	0	2	\N	\N
11273	Jonathan Chen	2	gi_bleed	65641	0	4	\N	\N
9013	Andre Kumar	2	gi_bleed	45814	5	4	Admit	\N
9014	Panel Average	2	gi_bleed	45814	5	\N	\N	\N
7580	Jason Hom	14	gi_bleed	61982	10	5	\N	\N
7581	Lisa Shieh	14	gi_bleed	61982	10	5	\N	\N
7582	Panel Consensus	14	gi_bleed	61982	10	\N	\N	\N
8451	Panel Average	14	gi_bleed	61982	7	\N	\N	\N
10004	Andre Kumar	14	gi_bleed	61982	2	5	Admit	\N
10556	Jonathan Chen	14	gi_bleed	61982	0	2	\N	\N
7583	Jason Hom	15	gi_bleed	61982	10	5	\N	\N
7584	Lisa Shieh	15	gi_bleed	61982	10	5	\N	\N
7585	Panel Consensus	15	gi_bleed	61982	10	\N	\N	\N
8304	Panel Average	15	gi_bleed	61982	8	\N	\N	\N
9015	Andre Kumar	15	gi_bleed	61982	5	5	Admit	\N
10557	Jonathan Chen	15	gi_bleed	61982	0	2	\N	\N
11440	Jonathan Chen	15	gi_bleed	44275	3	3	IVF	\N
11298	Jonathan Chen	15	gi_bleed	48744	0	3	\N	Probably want complete hepatic panel, so give points there
10005	Andre Kumar	14	gi_bleed	46136	2	1	Ammonia	\N
10264	Jonathan Chen	14	gi_bleed	46136	1	2	\N	May be interesting, but not main point of case
10383	Panel Average	14	gi_bleed	46136	1	\N	\N	\N
10558	Jason Hom	14	gi_bleed	46136	0	4	\N	\N
10559	Lisa Shieh	14	gi_bleed	46136	0	3	\N	\N
10560	Panel Consensus	14	gi_bleed	46136	0	\N	\N	\N
7586	Andre Kumar	15	gi_bleed	46136	10	5	Hepatic Encephalopathy	\N
9602	Panel Average	15	gi_bleed	46136	3	\N	\N	\N
10265	Jonathan Chen	15	gi_bleed	46136	1	2	\N	May be interesting, but not main point of case
10561	Jason Hom	15	gi_bleed	46136	0	4	\N	\N
10562	Lisa Shieh	15	gi_bleed	46136	0	3	\N	\N
10563	Panel Consensus	15	gi_bleed	46136	0	\N	\N	\N
10006	Andre Kumar	2	gi_bleed	46136	2	1	Hepatic Encephalopathy	\N
10266	Jonathan Chen	2	gi_bleed	46136	1	2	\N	May be interesting, but not main point of case
10384	Panel Average	2	gi_bleed	46136	1	\N	\N	\N
10564	Jason Hom	2	gi_bleed	46136	0	4	\N	\N
10565	Lisa Shieh	2	gi_bleed	46136	0	3	\N	\N
10566	Panel Consensus	2	gi_bleed	46136	0	\N	\N	\N
11372	Jonathan Chen	15	gi_bleed	63723	0	3	\N	\N
10567	Jonathan Chen	14	gi_bleed	50962	0	4	\N	Mistake, must be looking for blood
11015	Andre Kumar	14	gi_bleed	50962	-2	5	\N	\N
11099	Panel Average	14	gi_bleed	50962	-4	\N	\N	\N
11104	Panel Consensus	14	gi_bleed	50962	-4	\N	\N	\N
11149	Jason Hom	14	gi_bleed	50962	-5	5	\N	\N
9016	Lisa Shieh	15	gi_bleed	46245	5	3	\N	\N
9931	Panel Average	15	gi_bleed	46245	2	\N	\N	\N
10007	Andre Kumar	15	gi_bleed	46245	2	5	Metabolic Panel	\N
10008	Panel Consensus	15	gi_bleed	46245	2	\N	\N	\N
10568	Jason Hom	15	gi_bleed	46245	0	5	\N	\N
10569	Jonathan Chen	15	gi_bleed	46245	0	2	\N	Looking to explain hyperbilirubin I guess?
11276	Jonathan Chen	14	gi_bleed	48513	0	2	\N	\N
9017	Jason Hom	14	gi_bleed	45901	5	4	\N	\N
9932	Panel Average	14	gi_bleed	45901	2	\N	\N	\N
10009	Andre Kumar	14	gi_bleed	45901	2	2	Blood Cultures	\N
10570	Jonathan Chen	14	gi_bleed	45901	0	2	\N	Irrelevant diagnostic?
10571	Lisa Shieh	14	gi_bleed	45901	0	3	\N	\N
10572	Panel Consensus	14	gi_bleed	45901	0	\N	\N	\N
9018	Jason Hom	14	gi_bleed	45752	5	4	\N	\N
9933	Panel Average	14	gi_bleed	45752	2	\N	\N	\N
10010	Andre Kumar	14	gi_bleed	45752	2	4	Blood Cultures	\N
10573	Jonathan Chen	14	gi_bleed	45752	0	2	\N	\N
10574	Lisa Shieh	14	gi_bleed	45752	0	3	\N	\N
10575	Panel Consensus	14	gi_bleed	45752	0	\N	\N	\N
9691	Andre Kumar	14	gi_bleed	45760	3	4	Blood Gas	\N
10011	Jason Hom	14	gi_bleed	45760	2	4	\N	\N
10012	Jonathan Chen	14	gi_bleed	45760	2	3	Blood Gas	Check for acidosis?
10217	Panel Average	14	gi_bleed	45760	2	\N	\N	\N
10576	Lisa Shieh	14	gi_bleed	45760	0	3	\N	\N
10577	Panel Consensus	14	gi_bleed	45760	0	\N	\N	\N
10013	Andre Kumar	15	gi_bleed	45919	2	4	Blood Gas	\N
10014	Jason Hom	15	gi_bleed	45919	2	4	\N	\N
10015	Jonathan Chen	15	gi_bleed	45919	2	3	Blood Gas	Check for acidosis?
10233	Panel Average	15	gi_bleed	45919	1	\N	\N	\N
10578	Lisa Shieh	15	gi_bleed	45919	0	3	\N	\N
10579	Panel Consensus	15	gi_bleed	45919	0	\N	\N	\N
7587	Jason Hom	14	gi_bleed	45823	10	5	\N	\N
7588	Lisa Shieh	14	gi_bleed	45823	10	5	\N	\N
7589	Panel Consensus	14	gi_bleed	45823	10	\N	\N	\N
8305	Panel Average	14	gi_bleed	45823	8	\N	\N	\N
9019	Andre Kumar	14	gi_bleed	45823	5	5	Transfuse	\N
10267	Jonathan Chen	14	gi_bleed	45823	1	2	Type and Screen	Just a step in RBC transfusion prep
11395	Jonathan Chen	15	gi_bleed	45823	1	2	Type and Screen	\N
11317	Jonathan Chen	14	gi_bleed	44439	3	3	IVF	\N
7590	Jason Hom	14	gi_bleed	44290	10	4	\N	\N
7591	Lisa Shieh	14	gi_bleed	44290	10	5	ivf	\N
8306	Panel Average	14	gi_bleed	44290	8	\N	\N	\N
8339	Panel Consensus	14	gi_bleed	44290	8	\N	\N	\N
9020	Andre Kumar	14	gi_bleed	44290	5	4	Fluids	\N
9692	Jonathan Chen	14	gi_bleed	44290	3	3	IVF	\N
11248	Jonathan Chen	15	gi_bleed	44439	3	3	\N	\N
7592	Jason Hom	15	gi_bleed	44290	10	4	\N	\N
7593	Lisa Shieh	15	gi_bleed	44290	10	5	\N	\N
8224	Panel Average	15	gi_bleed	44290	9	\N	\N	\N
8340	Andre Kumar	15	gi_bleed	44290	8	4	Fluids	\N
8341	Panel Consensus	15	gi_bleed	44290	8	\N	\N	\N
9693	Jonathan Chen	15	gi_bleed	44290	3	3	IVF	\N
9021	Jason Hom	15	gi_bleed	45887	5	4	\N	\N
9022	Lisa Shieh	15	gi_bleed	45887	5	3	\N	\N
9493	Panel Average	15	gi_bleed	45887	4	\N	\N	\N
10016	Andre Kumar	15	gi_bleed	45887	2	4	Metabolic Panel	\N
10580	Jonathan Chen	15	gi_bleed	45887	0	2	\N	Not sure why necessary
10581	Panel Consensus	15	gi_bleed	45887	0	\N	\N	\N
9023	Jason Hom	2	gi_bleed	45887	5	4	\N	\N
9024	Lisa Shieh	2	gi_bleed	45887	5	3	\N	\N
9494	Panel Average	2	gi_bleed	45887	4	\N	\N	\N
10017	Andre Kumar	2	gi_bleed	45887	2	3	Metabolic Panel	\N
10582	Jonathan Chen	2	gi_bleed	45887	0	2	\N	\N
10583	Panel Consensus	2	gi_bleed	45887	0	\N	\N	\N
7594	Jason Hom	14	gi_bleed	45793	10	5	\N	\N
7595	Lisa Shieh	14	gi_bleed	45793	10	5	blood count	\N
7596	Panel Consensus	14	gi_bleed	45793	10	\N	\N	\N
8225	Panel Average	14	gi_bleed	45793	9	\N	\N	\N
8342	Andre Kumar	14	gi_bleed	45793	8	5	CBC	\N
8506	Jonathan Chen	14	gi_bleed	45793	7	4	CBC	\N
7597	Jason Hom	15	gi_bleed	45793	10	5	\N	\N
7598	Lisa Shieh	15	gi_bleed	45793	10	5	\N	\N
7599	Panel Consensus	15	gi_bleed	45793	10	\N	\N	\N
8293	Panel Average	15	gi_bleed	45793	9	\N	\N	\N
8507	Jonathan Chen	15	gi_bleed	45793	7	4	CBC	\N
8725	Andre Kumar	15	gi_bleed	45793	6	4	CBC	\N
7600	Jason Hom	16	gi_bleed	45793	10	5	\N	\N
7601	Lisa Shieh	16	gi_bleed	45793	10	5	\N	\N
7602	Panel Consensus	16	gi_bleed	45793	10	\N	\N	\N
8307	Panel Average	16	gi_bleed	45793	8	\N	\N	\N
8508	Jonathan Chen	16	gi_bleed	45793	7	4	CBC	\N
9025	Andre Kumar	16	gi_bleed	45793	5	1	CBC	\N
7603	Jason Hom	2	gi_bleed	45793	10	5	\N	\N
7604	Lisa Shieh	2	gi_bleed	45793	10	5	\N	\N
7605	Panel Consensus	2	gi_bleed	45793	10	\N	\N	\N
8452	Panel Average	2	gi_bleed	45793	7	\N	\N	\N
8509	Jonathan Chen	2	gi_bleed	45793	7	4	CBC	\N
10018	Andre Kumar	2	gi_bleed	45793	2	3	CBC	\N
7606	Lisa Shieh	14	gi_bleed	45788	10	3	blood count	\N
7607	Panel Consensus	14	gi_bleed	45788	10	\N	\N	\N
8241	Jason Hom	14	gi_bleed	45788	9	5	\N	\N
8242	Panel Average	14	gi_bleed	45788	9	\N	\N	\N
8343	Andre Kumar	14	gi_bleed	45788	8	5	CBC	\N
8510	Jonathan Chen	14	gi_bleed	45788	7	4	CBC	\N
7608	Lisa Shieh	15	gi_bleed	45788	10	5	\N	\N
7609	Panel Consensus	15	gi_bleed	45788	10	\N	\N	\N
8243	Jason Hom	15	gi_bleed	45788	9	5	\N	\N
8308	Panel Average	15	gi_bleed	45788	8	\N	\N	\N
8511	Jonathan Chen	15	gi_bleed	45788	7	4	CBC	\N
8726	Andre Kumar	15	gi_bleed	45788	6	5	CBC	\N
7610	Lisa Shieh	2	gi_bleed	45788	10	5	\N	\N
7611	Panel Consensus	2	gi_bleed	45788	10	\N	\N	\N
8244	Jason Hom	2	gi_bleed	45788	9	5	\N	\N
8512	Jonathan Chen	2	gi_bleed	45788	7	4	CBC	\N
8513	Panel Average	2	gi_bleed	45788	7	\N	\N	\N
10019	Andre Kumar	2	gi_bleed	45788	2	3	CBC	\N
11386	Jonathan Chen	15	gi_bleed	44255	0	2	\N	Not reliable to cover Gram negative enterics (e.g., E coli)
8344	Andre Kumar	15	gi_bleed	44637	8	5	Antibiotics	\N
8345	Jason Hom	15	gi_bleed	44637	8	5	\N	\N
8727	Jonathan Chen	15	gi_bleed	44637	6	5	Antibiotics	Would cover same as ceftriaxone, though odd choice
8868	Panel Average	15	gi_bleed	44637	5	\N	\N	\N
9026	Panel Consensus	15	gi_bleed	44637	5	\N	\N	\N
10584	Lisa Shieh	15	gi_bleed	44637	0	3	\N	\N
8245	Andre Kumar	14	gi_bleed	45060	9	3	Antibiotics	\N
8514	Jonathan Chen	14	gi_bleed	45060	7	5	Antibiotics	\N
9934	Panel Average	14	gi_bleed	45060	2	\N	\N	\N
10020	Panel Consensus	14	gi_bleed	45060	2	\N	\N	\N
10585	Lisa Shieh	14	gi_bleed	45060	0	3	\N	\N
11016	Jason Hom	14	gi_bleed	45060	-2	4	\N	\N
8246	Andre Kumar	15	gi_bleed	45060	9	5	Antibiotics	\N
8515	Jonathan Chen	15	gi_bleed	45060	7	5	Antibiotics	\N
9027	Lisa Shieh	15	gi_bleed	45060	5	3	\N	\N
9495	Panel Average	15	gi_bleed	45060	4	\N	\N	\N
10021	Panel Consensus	15	gi_bleed	45060	2	\N	\N	\N
11017	Jason Hom	15	gi_bleed	45060	-2	4	\N	\N
7612	Andre Kumar	14	gi_bleed	35733	10	5	Antibiotics	\N
7613	Jason Hom	14	gi_bleed	35733	10	5	\N	\N
7614	Panel Consensus	14	gi_bleed	35733	10	\N	\N	\N
8247	Panel Average	14	gi_bleed	35733	9	\N	\N	\N
8516	Jonathan Chen	14	gi_bleed	35733	7	5	Antibiotics	\N
8517	Lisa Shieh	14	gi_bleed	35733	7	3	\N	\N
7615	Andre Kumar	15	gi_bleed	35733	10	5	Antibiotics	\N
7616	Jason Hom	15	gi_bleed	35733	10	5	\N	\N
7617	Panel Consensus	15	gi_bleed	35733	10	\N	\N	\N
8248	Panel Average	15	gi_bleed	35733	9	\N	\N	\N
8518	Jonathan Chen	15	gi_bleed	35733	7	5	Antibiotics	\N
8519	Lisa Shieh	15	gi_bleed	35733	7	3	\N	If already given, do not give credit again
7618	Andre Kumar	16	gi_bleed	35733	10	5	Antibiotics	Points if not ordered before
7619	Jason Hom	16	gi_bleed	35733	10	5	\N	\N
7620	Lisa Shieh	16	gi_bleed	35733	10	5	\N	\N
7621	Panel Average	16	gi_bleed	35733	10	\N	\N	\N
7622	Panel Consensus	16	gi_bleed	35733	10	\N	\N	\N
8520	Jonathan Chen	16	gi_bleed	35733	7	5	Antibiotics	\N
7623	Jason Hom	2	gi_bleed	35733	10	5	\N	\N
7624	Lisa Shieh	2	gi_bleed	35733	10	5	\N	If antibiotics, imaging already done, would not give again
7625	Panel Consensus	2	gi_bleed	35733	10	\N	\N	\N
8226	Panel Average	2	gi_bleed	35733	9	\N	\N	\N
8346	Andre Kumar	2	gi_bleed	35733	8	3	Antibiotics	\N
8521	Jonathan Chen	2	gi_bleed	35733	7	5	Antibiotics	\N
11397	Jonathan Chen	2	gi_bleed	44249	7	5	Antibiotics	Reasonable empiric choice for GNRs
11423	Jonathan Chen	14	gi_bleed	62027	0	2	\N	\N
7626	Jason Hom	2	gi_bleed	63720	10	5	\N	\N
8522	Lisa Shieh	2	gi_bleed	63720	7	3	\N	\N
8523	Panel Average	2	gi_bleed	63720	7	\N	\N	\N
9028	Panel Consensus	2	gi_bleed	63720	5	\N	\N	\N
9496	Andre Kumar	2	gi_bleed	63720	4	1	Hepatitis Panel	\N
10022	Jonathan Chen	2	gi_bleed	63720	2	2	\N	Workup for liver injury. Okay I guess
7627	Jason Hom	15	gi_bleed	50400	10	5	\N	\N
8728	Panel Consensus	15	gi_bleed	50400	6	\N	\N	\N
8845	Panel Average	15	gi_bleed	50400	6	\N	\N	\N
9029	Lisa Shieh	15	gi_bleed	50400	5	3	\N	\N
10023	Andre Kumar	15	gi_bleed	50400	2	1	Consult	\N
10586	Jonathan Chen	15	gi_bleed	50400	0	2	\N	\N
7628	Jason Hom	14	gi_bleed	49481	10	5	\N	\N
7629	Jonathan Chen	14	gi_bleed	49481	10	5	GI-EGD	\N
7630	Lisa Shieh	14	gi_bleed	49481	10	5	\N	\N
7631	Panel Consensus	14	gi_bleed	49481	10	\N	\N	\N
8309	Panel Average	14	gi_bleed	49481	8	\N	\N	\N
9030	Andre Kumar	14	gi_bleed	49481	5	5	Consult	\N
7632	Andre Kumar	15	gi_bleed	49481	10	5	Consult	\N
7633	Jason Hom	15	gi_bleed	49481	10	5	\N	\N
7634	Jonathan Chen	15	gi_bleed	49481	10	5	GI-EGD	\N
7635	Lisa Shieh	15	gi_bleed	49481	10	5	\N	\N
7636	Panel Average	15	gi_bleed	49481	10	\N	\N	\N
7637	Panel Consensus	15	gi_bleed	49481	10	\N	\N	\N
7638	Jason Hom	16	gi_bleed	49481	10	5	\N	\N
7639	Jonathan Chen	16	gi_bleed	49481	10	5	GI-EGD	\N
7640	Lisa Shieh	16	gi_bleed	49481	10	5	\N	\N
7641	Panel Consensus	16	gi_bleed	49481	10	\N	\N	\N
8453	Panel Average	16	gi_bleed	49481	7	\N	\N	\N
10024	Andre Kumar	16	gi_bleed	49481	2	3	Consult	\N
9031	Jason Hom	14	gi_bleed	61323	5	5	\N	\N
9032	Lisa Shieh	14	gi_bleed	61323	5	3	\N	\N
9449	Panel Average	14	gi_bleed	61323	4	\N	\N	\N
9694	Andre Kumar	14	gi_bleed	61323	3	4	Consult	\N
10025	Panel Consensus	14	gi_bleed	61323	2	\N	\N	\N
10587	Jonathan Chen	14	gi_bleed	61323	0	2	\N	\N
7642	Jason Hom	15	gi_bleed	61323	10	5	\N	\N
7643	Lisa Shieh	15	gi_bleed	61323	10	3	\N	\N
8249	Panel Average	15	gi_bleed	61323	9	\N	\N	\N
8250	Panel Consensus	15	gi_bleed	61323	9	\N	\N	\N
8524	Andre Kumar	15	gi_bleed	61323	7	3	Consult	\N
10588	Jonathan Chen	15	gi_bleed	61323	0	2	\N	\N
11445	Jonathan Chen	16	gi_bleed	61323	0	2	\N	\N
7644	Jason Hom	14	gi_bleed	49207	10	5	\N	\N
9033	Lisa Shieh	14	gi_bleed	49207	5	3	\N	\N
9450	Panel Average	14	gi_bleed	49207	4	\N	\N	\N
9497	Panel Consensus	14	gi_bleed	49207	4	\N	\N	\N
10589	Jonathan Chen	14	gi_bleed	49207	0	3	\N	\N
11018	Andre Kumar	14	gi_bleed	49207	-2	2	Admit	\N
11269	Jonathan Chen	14	gi_bleed	49867	0	2	\N	Not DIC, more total coagulant deficiency
11019	Andre Kumar	14	gi_bleed	46072	-2	3	Imaging	Delays care
11020	Panel Average	14	gi_bleed	46072	-2	\N	\N	\N
9034	Lisa Shieh	16	gi_bleed	45858	5	3	\N	\N
10026	Jonathan Chen	16	gi_bleed	45858	2	2	CT Abdomen	Diagnostic workup okay, but seems like off choice for cirrhosis diagnosis?
10268	Panel Average	16	gi_bleed	45858	1	\N	\N	\N
10590	Jason Hom	16	gi_bleed	45858	0	4	\N	\N
10591	Panel Consensus	16	gi_bleed	45858	0	\N	\N	\N
11021	Andre Kumar	16	gi_bleed	45858	-2	2	Imaging	\N
11309	Jonathan Chen	14	gi_bleed	45852	2	2	CT Abdomen	\N
11022	Andre Kumar	16	gi_bleed	45852	-2	2	Imaging	\N
11023	Panel Average	16	gi_bleed	45852	-2	\N	\N	\N
8525	Lisa Shieh	2	gi_bleed	49836	7	3	\N	\N
10027	Jonathan Chen	2	gi_bleed	49836	2	2	CT Abdomen	Diagnostic workup okay, but seems like off choice for cirrhosis diagnosis?
10392	Panel Average	2	gi_bleed	49836	0	\N	\N	\N
10979	Andre Kumar	2	gi_bleed	49836	-1	4	Imaging	\N
11150	Jason Hom	2	gi_bleed	49836	-5	4	\N	\N
11151	Panel Consensus	2	gi_bleed	49836	-5	\N	\N	\N
10592	Jonathan Chen	2	gi_bleed	50737	0	2	\N	Looks like mistake. Probably looking for abdomen
10593	Lisa Shieh	2	gi_bleed	50737	0	5	\N	\N
10980	Andre Kumar	2	gi_bleed	50737	-1	5	Imaging	\N
11024	Panel Average	2	gi_bleed	50737	-2	\N	\N	\N
11152	Jason Hom	2	gi_bleed	50737	-5	4	\N	\N
11153	Panel Consensus	2	gi_bleed	50737	-5	\N	\N	\N
11387	Jonathan Chen	14	gi_bleed	48871	0	2	\N	\N
7645	Lisa Shieh	14	gi_bleed	46286	10	5	\N	\N
8526	Jonathan Chen	14	gi_bleed	46286	7	4	Coags	\N
8527	Panel Consensus	14	gi_bleed	46286	7	\N	\N	\N
8666	Panel Average	14	gi_bleed	46286	7	\N	\N	\N
9035	Andre Kumar	14	gi_bleed	46286	5	4	Coags	\N
9036	Jason Hom	14	gi_bleed	46286	5	4	\N	\N
7646	Lisa Shieh	16	gi_bleed	46286	10	5	\N	\N
8528	Jonathan Chen	16	gi_bleed	46286	7	4	Coags	\N
8529	Panel Consensus	16	gi_bleed	46286	7	\N	\N	\N
8667	Panel Average	16	gi_bleed	46286	7	\N	\N	\N
9037	Andre Kumar	16	gi_bleed	46286	5	2	Coags	\N
9038	Jason Hom	16	gi_bleed	46286	5	4	\N	\N
9695	Andre Kumar	2	gi_bleed	46286	3	3	Coags	\N
9696	Panel Average	2	gi_bleed	46286	3	\N	\N	\N
10028	Andre Kumar	2	gi_bleed	45784	2	2	Clear Liquid	\N
10029	Panel Average	2	gi_bleed	45784	2	\N	\N	\N
7647	Jason Hom	14	gi_bleed	45811	10	5	\N	\N
7648	Lisa Shieh	14	gi_bleed	45811	10	5	\N	\N
8310	Panel Average	14	gi_bleed	45811	8	\N	\N	\N
8347	Panel Consensus	14	gi_bleed	45811	8	\N	\N	\N
9039	Andre Kumar	14	gi_bleed	45811	5	5	NPO	\N
9697	Jonathan Chen	14	gi_bleed	45811	3	3	\N	\N
7649	Jason Hom	15	gi_bleed	45811	10	5	\N	\N
7650	Lisa Shieh	15	gi_bleed	45811	10	5	\N	\N
8311	Panel Average	15	gi_bleed	45811	8	\N	\N	\N
8348	Panel Consensus	15	gi_bleed	45811	8	\N	\N	\N
9040	Andre Kumar	15	gi_bleed	45811	5	5	NPO	\N
9698	Jonathan Chen	15	gi_bleed	45811	3	3	\N	\N
11464	Jonathan Chen	14	gi_bleed	45941	0	2	\N	\N
9041	Lisa Shieh	14	gi_bleed	45866	5	3	\N	\N
9935	Panel Average	14	gi_bleed	45866	2	\N	\N	\N
10030	Jason Hom	14	gi_bleed	45866	2	4	\N	\N
10031	Jonathan Chen	14	gi_bleed	45866	2	2	\N	\N
10032	Panel Consensus	14	gi_bleed	45866	2	\N	\N	\N
10594	Andre Kumar	14	gi_bleed	45866	0	4	ECG + Monitoring	\N
8530	Lisa Shieh	15	gi_bleed	45866	7	3	\N	\N
9936	Panel Average	15	gi_bleed	45866	2	\N	\N	\N
10033	Jason Hom	15	gi_bleed	45866	2	4	\N	\N
10034	Jonathan Chen	15	gi_bleed	45866	2	2	\N	\N
10035	Panel Consensus	15	gi_bleed	45866	2	\N	\N	\N
11025	Andre Kumar	15	gi_bleed	45866	-2	4	ECG + Monitoring	\N
10595	Andre Kumar	2	gi_bleed	61832	0	2	Imaging	\N
10596	Jonathan Chen	2	gi_bleed	61832	0	2	\N	Working up ascites I guess? History all suggests primary liver though
10597	Lisa Shieh	2	gi_bleed	61832	0	5	\N	\N
10598	Panel Consensus	2	gi_bleed	61832	0	\N	\N	\N
10969	Panel Average	2	gi_bleed	61832	-1	\N	\N	\N
11154	Jason Hom	2	gi_bleed	61832	-5	4	\N	\N
7651	Jason Hom	14	gi_bleed	46160	10	5	\N	\N
7652	Lisa Shieh	14	gi_bleed	46160	10	5	\N	\N
7653	Panel Consensus	14	gi_bleed	46160	10	\N	\N	\N
8432	Panel Average	14	gi_bleed	46160	8	\N	\N	\N
9699	Andre Kumar	14	gi_bleed	46160	3	2	Vitals	\N
10599	Jonathan Chen	14	gi_bleed	46160	0	2	\N	\N
11477	Jonathan Chen	15	gi_bleed	46160	0	2	\N	\N
11330	Jonathan Chen	15	gi_bleed	46078	0	2	\N	\N
7654	Andre Kumar	14	gi_bleed	63759	10	4	Transfuse	\N
7655	Jonathan Chen	14	gi_bleed	63759	10	5	RBC	\N
9042	Jason Hom	14	gi_bleed	63759	5	4	\N	\N
9043	Panel Average	14	gi_bleed	63759	5	\N	\N	\N
10600	Lisa Shieh	14	gi_bleed	63759	0	3	\N	\N
10601	Panel Consensus	14	gi_bleed	63759	0	\N	\N	\N
7656	Andre Kumar	15	gi_bleed	63759	10	5	Transfuse	\N
7657	Jason Hom	15	gi_bleed	63759	10	4	\N	\N
7658	Jonathan Chen	15	gi_bleed	63759	10	5	RBC	\N
7659	Lisa Shieh	15	gi_bleed	63759	10	5	\N	\N
7660	Panel Average	15	gi_bleed	63759	10	\N	\N	\N
7661	Panel Consensus	15	gi_bleed	63759	10	\N	\N	\N
9044	Jason Hom	14	gi_bleed	46028	5	4	\N	\N
9498	Panel Consensus	14	gi_bleed	46028	4	\N	\N	\N
9582	Panel Average	14	gi_bleed	46028	4	\N	\N	\N
9700	Andre Kumar	14	gi_bleed	46028	3	3	Coags	\N
9701	Lisa Shieh	14	gi_bleed	46028	3	3	\N	\N
10602	Jonathan Chen	14	gi_bleed	46028	0	2	\N	\N
7662	Jason Hom	14	gi_bleed	45872	10	5	\N	\N
7663	Lisa Shieh	14	gi_bleed	45872	10	3	\N	\N
8227	Panel Average	14	gi_bleed	45872	9	\N	\N	\N
8251	Jonathan Chen	14	gi_bleed	45872	9	4	FFP	\N
8252	Panel Consensus	14	gi_bleed	45872	9	\N	\N	\N
8349	Andre Kumar	14	gi_bleed	45872	8	5	Transfuse	\N
7664	Jason Hom	15	gi_bleed	45872	10	5	\N	\N
7665	Lisa Shieh	15	gi_bleed	45872	10	5	\N	\N
8228	Panel Average	15	gi_bleed	45872	9	\N	\N	\N
8253	Jonathan Chen	15	gi_bleed	45872	9	4	FFP	\N
8254	Panel Consensus	15	gi_bleed	45872	9	\N	\N	\N
8350	Andre Kumar	15	gi_bleed	45872	8	5	Transfuse	\N
7666	Jason Hom	16	gi_bleed	45872	10	5	\N	\N
7667	Lisa Shieh	16	gi_bleed	45872	10	5	\N	\N
8255	Jonathan Chen	16	gi_bleed	45872	9	4	FFP	\N
8256	Panel Average	16	gi_bleed	45872	9	\N	\N	\N
8257	Panel Consensus	16	gi_bleed	45872	9	\N	\N	\N
8531	Andre Kumar	16	gi_bleed	45872	7	1	Transfuse	no points if done previously
10603	Andre Kumar	14	gi_bleed	41788	0	1	\N	?Order set?
10604	Panel Average	14	gi_bleed	41788	0	\N	\N	\N
11324	Jonathan Chen	14	gi_bleed	44237	6	4	Antibiotics	A bit overkill, but would cover GNRs
9045	Andre Kumar	14	gi_bleed	48724	5	4	H pylori	\N
9046	Jason Hom	14	gi_bleed	48724	5	4	\N	\N
9047	Lisa Shieh	14	gi_bleed	48724	5	3	h pylori	\N
9048	Panel Average	14	gi_bleed	48724	5	\N	\N	\N
9049	Panel Consensus	14	gi_bleed	48724	5	\N	\N	\N
10269	Jonathan Chen	14	gi_bleed	48724	1	2	\N	Antibody not as relevant as stool test
9050	Jason Hom	14	gi_bleed	45948	5	4	\N	\N
9051	Lisa Shieh	14	gi_bleed	45948	5	3	\N	\N
9052	Panel Consensus	14	gi_bleed	45948	5	\N	\N	\N
9583	Panel Average	14	gi_bleed	45948	4	\N	\N	\N
9702	Jonathan Chen	14	gi_bleed	45948	3	3	\N	\N
10270	Andre Kumar	14	gi_bleed	45948	1	4	H pylori	\N
8532	Lisa Shieh	15	gi_bleed	45948	7	3	\N	\N
9053	Jason Hom	15	gi_bleed	45948	5	4	\N	\N
9054	Panel Consensus	15	gi_bleed	45948	5	\N	\N	\N
9451	Panel Average	15	gi_bleed	45948	4	\N	\N	\N
9703	Jonathan Chen	15	gi_bleed	45948	3	3	\N	\N
10271	Andre Kumar	15	gi_bleed	45948	1	3	H pylori	\N
7668	Jason Hom	15	gi_bleed	45891	10	5	\N	\N
7669	Lisa Shieh	15	gi_bleed	45891	10	5	\N	\N
7670	Panel Consensus	15	gi_bleed	45891	10	\N	\N	\N
8312	Panel Average	15	gi_bleed	45891	8	\N	\N	\N
8533	Jonathan Chen	15	gi_bleed	45891	7	4	CBC	\N
9055	Andre Kumar	15	gi_bleed	45891	5	4	CBC	\N
7671	Jason Hom	15	gi_bleed	46051	10	5	\N	\N
7672	Lisa Shieh	15	gi_bleed	46051	10	5	\N	\N
7673	Panel Consensus	15	gi_bleed	46051	10	\N	\N	\N
8313	Panel Average	15	gi_bleed	46051	8	\N	\N	\N
8534	Jonathan Chen	15	gi_bleed	46051	7	4	CBC	\N
9056	Andre Kumar	15	gi_bleed	46051	5	5	CBC	\N
11384	Jonathan Chen	15	gi_bleed	46068	0	2	\N	\N
7674	Jason Hom	14	gi_bleed	45910	10	5	\N	\N
8454	Panel Average	14	gi_bleed	45910	7	\N	\N	\N
8535	Jonathan Chen	14	gi_bleed	45910	7	4	Metabolic Panel	\N
8536	Lisa Shieh	14	gi_bleed	45910	7	3	\N	\N
8537	Panel Consensus	14	gi_bleed	45910	7	\N	\N	\N
9057	Andre Kumar	14	gi_bleed	45910	5	4	Liver Function Test	\N
11441	Jonathan Chen	2	gi_bleed	62029	0	2	\N	Covered in hepatitis panel?
7675	Jason Hom	15	gi_bleed	71083	10	5	\N	\N
8729	Andre Kumar	15	gi_bleed	71083	6	4	ICU Bundle	\N
8869	Panel Average	15	gi_bleed	71083	5	\N	\N	\N
9058	Panel Consensus	15	gi_bleed	71083	5	\N	\N	\N
10605	Jonathan Chen	15	gi_bleed	71083	0	2	\N	Not supposed to be directly ordered
10606	Lisa Shieh	15	gi_bleed	71083	0	3	\N	\N
7676	Lisa Shieh	14	gi_bleed	65649	10	3	\N	\N
9452	Panel Average	14	gi_bleed	65649	4	\N	\N	\N
9499	Panel Consensus	14	gi_bleed	65649	4	\N	\N	\N
9704	Andre Kumar	14	gi_bleed	65649	3	3	NG tube	\N
10036	Jonathan Chen	14	gi_bleed	65649	2	2	Airway Protection	May not be necessary, but reasonable
10607	Jason Hom	14	gi_bleed	65649	0	4	\N	\N
8538	Andre Kumar	15	gi_bleed	62022	7	5	Intubate	\N
8539	Panel Consensus	15	gi_bleed	62022	7	\N	\N	\N
9059	Jason Hom	15	gi_bleed	62022	5	4	\N	\N
9500	Panel Average	15	gi_bleed	62022	4	\N	\N	\N
10037	Jonathan Chen	15	gi_bleed	62022	2	2	Airway Protection	Wasn't supposed to be necessary, but not unreasonable if worried about ongoing hematemesis
10608	Lisa Shieh	15	gi_bleed	62022	0	5	\N	\N
7677	Jason Hom	14	gi_bleed	45942	10	5	\N	\N
7678	Lisa Shieh	14	gi_bleed	45942	10	6	coags	\N
8314	Panel Average	14	gi_bleed	45942	8	\N	\N	\N
8351	Panel Consensus	14	gi_bleed	45942	8	\N	\N	\N
8540	Jonathan Chen	14	gi_bleed	45942	7	4	Coags	\N
9060	Andre Kumar	14	gi_bleed	45942	5	5	Coags	\N
9061	Lisa Shieh	15	gi_bleed	45838	5	3	\N	\N
10038	Jonathan Chen	15	gi_bleed	45838	2	3	Troponin	\N
10218	Panel Average	15	gi_bleed	45838	2	\N	\N	\N
10609	Andre Kumar	15	gi_bleed	45838	0	2	Troponin	\N
10610	Jason Hom	15	gi_bleed	45838	0	4	\N	\N
10611	Panel Consensus	15	gi_bleed	45838	0	\N	\N	\N
7679	Jason Hom	14	gi_bleed	48954	10	4	\N	\N
7680	Lisa Shieh	14	gi_bleed	48954	10	5	ivf	\N
7681	Panel Consensus	14	gi_bleed	48954	10	\N	\N	\N
8541	Panel Average	14	gi_bleed	48954	7	\N	\N	\N
10039	Jonathan Chen	14	gi_bleed	48954	2	2	IV Access	\N
10272	Andre Kumar	14	gi_bleed	48954	1	5	Nursing	\N
11433	Jonathan Chen	15	gi_bleed	44978	0	2	\N	Peri-procedure sedation???
9062	Jason Hom	14	gi_bleed	62151	5	4	\N	\N
9937	Panel Average	14	gi_bleed	62151	2	\N	\N	\N
10040	Andre Kumar	14	gi_bleed	62151	2	4	Lactate	\N
10041	Jonathan Chen	14	gi_bleed	62151	2	4	Lactate	\N
10042	Panel Consensus	14	gi_bleed	62151	2	\N	\N	\N
10612	Lisa Shieh	14	gi_bleed	62151	0	3	\N	\N
11360	Jonathan Chen	15	gi_bleed	62151	2	4	Lactate	\N
11341	Jonathan Chen	16	gi_bleed	62151	2	4	Lactate	\N
10043	Andre Kumar	14	gi_bleed	45918	2	4	Lactate	\N
10044	Panel Average	14	gi_bleed	45918	2	\N	\N	\N
10613	Lisa Shieh	15	gi_bleed	46289	0	3	\N	\N
11026	Andre Kumar	15	gi_bleed	46289	-2	1	Hepatic Encephalopathy	\N
11027	Jonathan Chen	15	gi_bleed	46289	-2	2	Lactulose	Maybe even negative points? Giving lactulose to make patient have diarrhea while they are actively bleeding out seems bad
11028	Panel Consensus	15	gi_bleed	46289	-2	\N	\N	\N
11071	Panel Average	15	gi_bleed	46289	-2	\N	\N	\N
11155	Jason Hom	15	gi_bleed	46289	-5	4	\N	\N
10614	Lisa Shieh	15	gi_bleed	44302	0	3	\N	\N
11029	Andre Kumar	15	gi_bleed	44302	-2	5	Hepatic Encephalopathy	\N
11030	Jonathan Chen	15	gi_bleed	44302	-2	2	Lactulose	Maybe even negative points? Giving lactulose to make patient have diarrhea while they are actively bleeding out seems bad
11031	Panel Consensus	15	gi_bleed	44302	-2	\N	\N	\N
11072	Panel Average	15	gi_bleed	44302	-2	\N	\N	\N
11156	Jason Hom	15	gi_bleed	44302	-5	4	\N	\N
10615	Lisa Shieh	15	gi_bleed	44593	0	3	\N	\N
11032	Andre Kumar	15	gi_bleed	44593	-2	5	Hepatic Encephalopathy	\N
11033	Jonathan Chen	15	gi_bleed	44593	-2	2	Lactulose	Maybe even negative points? Giving lactulose to make patient have diarrhea while they are actively bleeding out seems bad
11034	Panel Consensus	15	gi_bleed	44593	-2	\N	\N	\N
11073	Panel Average	15	gi_bleed	44593	-2	\N	\N	\N
11157	Jason Hom	15	gi_bleed	44593	-5	4	\N	\N
11316	Jonathan Chen	14	gi_bleed	45903	0	2	\N	\N
11426	Jonathan Chen	14	gi_bleed	62144	0	0	\N	\N
9705	Andre Kumar	16	gi_bleed	62144	3	3	Imaging	\N
9706	Panel Average	16	gi_bleed	62144	3	\N	\N	\N
10616	Andre Kumar	14	gi_bleed	45894	0	2	Lipase	\N
10617	Jason Hom	14	gi_bleed	45894	0	4	\N	\N
10618	Jonathan Chen	14	gi_bleed	45894	0	2	\N	Irrelevant diagnostic?
10619	Lisa Shieh	14	gi_bleed	45894	0	3	\N	\N
10620	Panel Average	14	gi_bleed	45894	0	\N	\N	\N
10621	Panel Consensus	14	gi_bleed	45894	0	\N	\N	\N
7682	Jason Hom	15	gi_bleed	45806	10	4	\N	\N
9603	Panel Average	15	gi_bleed	45806	3	\N	\N	\N
10045	Panel Consensus	15	gi_bleed	45806	2	\N	\N	\N
10622	Andre Kumar	15	gi_bleed	45806	0	5	Metabolic Panel	\N
10623	Jonathan Chen	15	gi_bleed	45806	0	2	\N	\N
10624	Lisa Shieh	15	gi_bleed	45806	0	3	\N	\N
10046	Andre Kumar	2	gi_bleed	45806	2	3	Metabolic Panel	\N
10047	Panel Average	2	gi_bleed	45806	2	\N	\N	\N
9063	Andre Kumar	14	gi_bleed	63745	5	2	Transfuse	\N
9064	Jason Hom	14	gi_bleed	63745	5	4	\N	\N
9604	Panel Average	14	gi_bleed	63745	3	\N	\N	\N
10625	Jonathan Chen	14	gi_bleed	63745	0	2	\N	\N
10626	Lisa Shieh	14	gi_bleed	63745	0	3	\N	\N
10627	Panel Consensus	14	gi_bleed	63745	0	\N	\N	\N
11244	Jonathan Chen	15	gi_bleed	63745	0	2	\N	\N
7683	Jason Hom	14	gi_bleed	45763	10	4	\N	\N
7684	Lisa Shieh	14	gi_bleed	45763	10	5	\N	\N
8352	Panel Consensus	14	gi_bleed	45763	8	\N	\N	\N
8433	Panel Average	14	gi_bleed	45763	8	\N	\N	\N
8542	Jonathan Chen	14	gi_bleed	45763	7	4	Metabolic Panel	\N
9707	Andre Kumar	14	gi_bleed	45763	3	3	Metabolic Panel	\N
7685	Jason Hom	15	gi_bleed	45763	10	4	\N	\N
7686	Lisa Shieh	15	gi_bleed	45763	10	5	\N	\N
8353	Panel Consensus	15	gi_bleed	45763	8	\N	\N	\N
8434	Panel Average	15	gi_bleed	45763	8	\N	\N	\N
8543	Jonathan Chen	15	gi_bleed	45763	7	4	Metabolic Panel	\N
9708	Andre Kumar	15	gi_bleed	45763	3	4	Metabolic Panel	\N
7687	Jason Hom	2	gi_bleed	45763	10	4	\N	\N
7688	Lisa Shieh	2	gi_bleed	45763	10	5	\N	\N
8315	Panel Average	2	gi_bleed	45763	8	\N	\N	\N
8354	Panel Consensus	2	gi_bleed	45763	8	\N	\N	\N
8544	Jonathan Chen	2	gi_bleed	45763	7	4	Metabolic Panel	\N
9065	Andre Kumar	2	gi_bleed	45763	5	2	Metabolic Panel	\N
7689	Jason Hom	14	gi_bleed	45771	10	4	\N	\N
7690	Lisa Shieh	14	gi_bleed	45771	10	5	\N	\N
8258	Panel Consensus	14	gi_bleed	45771	9	\N	\N	\N
8355	Panel Average	14	gi_bleed	45771	8	\N	\N	\N
8545	Jonathan Chen	14	gi_bleed	45771	7	4	Metabolic Panel	\N
9501	Andre Kumar	14	gi_bleed	45771	4	5	Metabolic Panel	\N
7691	Jason Hom	15	gi_bleed	45771	10	4	\N	\N
7692	Lisa Shieh	15	gi_bleed	45771	10	5	\N	\N
8259	Panel Consensus	15	gi_bleed	45771	9	\N	\N	\N
8435	Panel Average	15	gi_bleed	45771	8	\N	\N	\N
8546	Jonathan Chen	15	gi_bleed	45771	7	4	Metabolic Panel	\N
9709	Andre Kumar	15	gi_bleed	45771	3	4	Metabolic Panel	\N
11342	Jonathan Chen	2	gi_bleed	45771	7	4	Metabolic Panel	\N
11035	Andre Kumar	14	gi_bleed	44294	-2	5	Pain Medication	\N
11036	Panel Average	14	gi_bleed	44294	-2	\N	\N	\N
10628	Andre Kumar	15	gi_bleed	45792	0	2	MRSA	\N
10629	Jason Hom	15	gi_bleed	45792	0	4	\N	\N
10630	Jonathan Chen	15	gi_bleed	45792	0	2	\N	\N
10631	Lisa Shieh	15	gi_bleed	45792	0	3	\N	\N
10632	Panel Average	15	gi_bleed	45792	0	\N	\N	\N
10633	Panel Consensus	15	gi_bleed	45792	0	\N	\N	\N
7693	Jason Hom	14	gi_bleed	45785	10	4	\N	\N
9605	Panel Average	14	gi_bleed	45785	3	\N	\N	\N
10634	Andre Kumar	14	gi_bleed	45785	0	1	Nursing	\N
10635	Jonathan Chen	14	gi_bleed	45785	0	2	\N	\N
10636	Lisa Shieh	14	gi_bleed	45785	0	\N	\N	\N
10637	Panel Consensus	14	gi_bleed	45785	0	\N	\N	\N
8730	Andre Kumar	15	gi_bleed	36086	6	3	Pressors	\N
9066	Jason Hom	15	gi_bleed	36086	5	4	\N	\N
9067	Panel Consensus	15	gi_bleed	36086	5	\N	\N	\N
9584	Panel Average	15	gi_bleed	36086	4	\N	\N	\N
10638	Jonathan Chen	15	gi_bleed	36086	0	2	Pressors	\N
10639	Lisa Shieh	15	gi_bleed	36086	0	3	\N	\N
10273	Andre Kumar	14	gi_bleed	48815	1	3	Stool test	\N
10274	Panel Average	14	gi_bleed	48815	1	\N	\N	\N
11422	Jonathan Chen	14	gi_bleed	51110	0	2	\N	Largely irrelevant in acute setting
9710	Jonathan Chen	14	gi_bleed	46451	3	3	Octreotide	Subcutaneous probably not the correct route
10640	Lisa Shieh	14	gi_bleed	46451	0	3	Octreotide	\N
10987	Panel Average	14	gi_bleed	46451	-1	\N	\N	\N
11037	Andre Kumar	14	gi_bleed	46451	-2	2	Bleeding Medication	\N
11038	Jason Hom	14	gi_bleed	46451	-2	4	\N	\N
11039	Panel Consensus	14	gi_bleed	46451	-2	\N	\N	\N
9068	Lisa Shieh	15	gi_bleed	46451	5	3	\N	\N
9711	Jonathan Chen	15	gi_bleed	46451	3	3	Octreotide	Subcutaneous probably not the correct route
10393	Panel Average	15	gi_bleed	46451	0	\N	\N	\N
11040	Andre Kumar	15	gi_bleed	46451	-2	3	Bleeding Medication	\N
11041	Jason Hom	15	gi_bleed	46451	-2	4	\N	\N
11042	Panel Consensus	15	gi_bleed	46451	-2	\N	\N	\N
7694	Andre Kumar	14	gi_bleed	43996	10	5	Bleeding Medication	\N
7695	Jason Hom	14	gi_bleed	43996	10	5	\N	\N
7696	Panel Consensus	14	gi_bleed	43996	10	\N	\N	\N
8260	Panel Average	14	gi_bleed	43996	9	\N	\N	\N
8547	Lisa Shieh	14	gi_bleed	43996	7	3	\N	no known cirrhosis but angiomata on exam
9069	Jonathan Chen	14	gi_bleed	43996	5	4	Octreotide	Presumptive variceal bleed
7697	Andre Kumar	15	gi_bleed	43996	10	4	Bleeding Medication	\N
7698	Jason Hom	15	gi_bleed	43996	10	5	\N	\N
7699	Lisa Shieh	15	gi_bleed	43996	10	5	\N	\N
7700	Panel Average	15	gi_bleed	43996	10	\N	\N	\N
7701	Panel Consensus	15	gi_bleed	43996	10	\N	\N	\N
9070	Jonathan Chen	15	gi_bleed	43996	5	4	Octreotide	Presumptive variceal bleed
7702	Jason Hom	16	gi_bleed	43996	10	5	\N	\N
7703	Lisa Shieh	16	gi_bleed	43996	10	5	\N	\N
7704	Panel Consensus	16	gi_bleed	43996	10	\N	\N	\N
8668	Panel Average	16	gi_bleed	43996	7	\N	\N	\N
9071	Jonathan Chen	16	gi_bleed	43996	5	4	Octreotide	Presumptive variceal bleed
10641	Andre Kumar	16	gi_bleed	43996	0	2	Bleeding Medication	\N
7705	Jason Hom	2	gi_bleed	43996	10	5	\N	\N
7706	Lisa Shieh	2	gi_bleed	43996	10	5	\N	\N
7707	Panel Consensus	2	gi_bleed	43996	10	\N	\N	\N
8669	Panel Average	2	gi_bleed	43996	7	\N	\N	\N
9072	Jonathan Chen	2	gi_bleed	43996	5	4	Octreotide	Presumptive variceal bleed
10642	Andre Kumar	2	gi_bleed	43996	0	2	Bleeding Medication	\N
9073	Lisa Shieh	15	gi_bleed	46449	5	3	\N	\N
9712	Jonathan Chen	15	gi_bleed	46449	3	3	Octreotide	Subcutaneous probably not the correct route
10394	Panel Average	15	gi_bleed	46449	0	\N	\N	\N
11043	Andre Kumar	15	gi_bleed	46449	-2	3	Bleeding Medication	\N
11044	Jason Hom	15	gi_bleed	46449	-2	4	\N	\N
11045	Panel Consensus	15	gi_bleed	46449	-2	\N	\N	\N
9074	Jason Hom	14	gi_bleed	44216	5	4	\N	\N
10048	Panel Average	14	gi_bleed	44216	2	\N	\N	\N
10049	Panel Consensus	14	gi_bleed	44216	2	\N	\N	\N
10275	Andre Kumar	14	gi_bleed	44216	1	2	Nausea Medication	\N
10643	Jonathan Chen	14	gi_bleed	44216	0	2	\N	\N
10644	Lisa Shieh	14	gi_bleed	44216	0	3	\N	\N
7708	Lisa Shieh	14	gi_bleed	45868	10	5	\N	\N
8356	Jason Hom	14	gi_bleed	45868	8	4	\N	\N
8357	Panel Consensus	14	gi_bleed	45868	8	\N	\N	\N
8731	Panel Average	14	gi_bleed	45868	6	\N	\N	\N
9713	Jonathan Chen	14	gi_bleed	45868	3	2	\N	\N
10645	Andre Kumar	14	gi_bleed	45868	0	5	Vitals	\N
10050	Andre Kumar	2	gi_bleed	45787	2	1	PT/OT	\N
10051	Panel Average	2	gi_bleed	45787	2	\N	\N	\N
11410	Jonathan Chen	14	gi_bleed	48822	0	2	Oxygen	No specific hypoxia in case
11264	Jonathan Chen	14	gi_bleed	45900	0	2	Oxygen	No specific hypoxia in case
7709	Andre Kumar	14	gi_bleed	44219	10	5	PPI	\N
7710	Jason Hom	14	gi_bleed	44219	10	5	\N	\N
7711	Lisa Shieh	14	gi_bleed	44219	10	5	\N	\N
7712	Panel Average	14	gi_bleed	44219	10	\N	\N	\N
7713	Panel Consensus	14	gi_bleed	44219	10	\N	\N	\N
9075	Jonathan Chen	14	gi_bleed	44219	5	4	\N	\N
7714	Andre Kumar	15	gi_bleed	44219	10	5	Bleeding Medication	\N
7715	Jason Hom	15	gi_bleed	44219	10	5	\N	\N
7716	Lisa Shieh	15	gi_bleed	44219	10	5	\N	\N
7717	Panel Average	15	gi_bleed	44219	10	\N	\N	\N
7718	Panel Consensus	15	gi_bleed	44219	10	\N	\N	\N
9076	Jonathan Chen	15	gi_bleed	44219	5	4	\N	\N
7719	Jason Hom	16	gi_bleed	44219	10	5	\N	\N
7720	Lisa Shieh	16	gi_bleed	44219	10	5	\N	\N
7721	Panel Average	16	gi_bleed	44219	10	\N	\N	\N
7722	Panel Consensus	16	gi_bleed	44219	10	\N	\N	\N
9077	Jonathan Chen	16	gi_bleed	44219	5	4	\N	\N
11261	Jonathan Chen	14	gi_bleed	44236	0	3	\N	Mistake, should be giving oral med while vomiting blood
9078	Lisa Shieh	15	gi_bleed	44236	5	3	\N	\N
10052	Andre Kumar	15	gi_bleed	44236	2	4	Bleeding Medication	\N
10385	Panel Average	15	gi_bleed	44236	1	\N	\N	\N
10646	Jonathan Chen	15	gi_bleed	44236	0	3	\N	Mistake, should be giving oral med while vomiting blood
10647	Panel Consensus	15	gi_bleed	44236	0	\N	\N	\N
11158	Jason Hom	15	gi_bleed	44236	-5	5	\N	\N
11303	Jonathan Chen	15	gi_bleed	62171	0	2	\N	Active bleeding, probably not right time for para, though SBP always to consider?
7723	Jason Hom	14	gi_bleed	61823	10	5	\N	\N
7724	Lisa Shieh	14	gi_bleed	61823	10	5	\N	\N
7725	Panel Consensus	14	gi_bleed	61823	10	\N	\N	\N
8316	Panel Average	14	gi_bleed	61823	8	\N	\N	\N
9079	Andre Kumar	14	gi_bleed	61823	5	4	Nursing	\N
10053	Jonathan Chen	14	gi_bleed	61823	2	2	IV Access	\N
7726	Jason Hom	15	gi_bleed	61823	10	5	\N	\N
7727	Lisa Shieh	15	gi_bleed	61823	10	5	\N	\N
7728	Panel Consensus	15	gi_bleed	61823	10	\N	\N	\N
8317	Panel Average	15	gi_bleed	61823	8	\N	\N	\N
9080	Andre Kumar	15	gi_bleed	61823	5	1	Nursing	\N
10054	Jonathan Chen	15	gi_bleed	61823	2	2	IV Access	\N
7729	Jason Hom	14	gi_bleed	45802	10	5	\N	\N
7730	Lisa Shieh	14	gi_bleed	45802	10	5	\N	\N
7731	Panel Consensus	14	gi_bleed	45802	10	\N	\N	\N
8318	Panel Average	14	gi_bleed	45802	8	\N	\N	\N
9081	Andre Kumar	14	gi_bleed	45802	5	5	Nursing	\N
10055	Jonathan Chen	14	gi_bleed	45802	2	2	IV Access	Maybe trying to capture placing large bore IVs. Is important, but don't want to have others lose too many points for missing this, because many won't realize that can order this (usually you just tell a nurse)
8732	Andre Kumar	15	gi_bleed	43993	6	3	Pressors	\N
9714	Panel Consensus	15	gi_bleed	43993	3	\N	\N	\N
10395	Panel Average	15	gi_bleed	43993	0	\N	\N	\N
10648	Jonathan Chen	15	gi_bleed	43993	0	2	Pressors	\N
10649	Lisa Shieh	15	gi_bleed	43993	0	3	\N	\N
11159	Jason Hom	15	gi_bleed	43993	-5	5	\N	\N
7732	Jason Hom	15	gi_bleed	45778	10	5	\N	\N
9453	Panel Average	15	gi_bleed	45778	4	\N	\N	\N
9502	Panel Consensus	15	gi_bleed	45778	4	\N	\N	\N
9715	Andre Kumar	15	gi_bleed	45778	3	4	Coags	\N
10650	Jonathan Chen	15	gi_bleed	45778	0	2	\N	\N
10651	Lisa Shieh	15	gi_bleed	45778	0	3	\N	\N
7733	Jason Hom	2	gi_bleed	45778	10	5	\N	\N
8846	Panel Average	2	gi_bleed	45778	6	\N	\N	\N
9082	Lisa Shieh	2	gi_bleed	45778	5	3	\N	\N
9503	Panel Consensus	2	gi_bleed	45778	4	\N	\N	\N
10056	Andre Kumar	2	gi_bleed	45778	2	1	Metabolic Panel	\N
10652	Jonathan Chen	2	gi_bleed	45778	0	2	\N	\N
8358	Jason Hom	14	gi_bleed	45875	8	4	\N	\N
9915	Panel Average	14	gi_bleed	45875	3	\N	\N	\N
10057	Jonathan Chen	14	gi_bleed	45875	2	2	\N	Some points for preparing platelets, even though ends up not being necessary
10653	Andre Kumar	14	gi_bleed	45875	0	1	Transfuse	\N
10654	Lisa Shieh	14	gi_bleed	45875	0	5	\N	\N
10655	Panel Consensus	14	gi_bleed	45875	0	\N	\N	\N
7734	Jason Hom	15	gi_bleed	45875	10	5	\N	\N
9938	Panel Average	15	gi_bleed	45875	2	\N	\N	\N
10058	Jonathan Chen	15	gi_bleed	45875	2	2	\N	Some points for preparing platelets, even though ends up not being necessary
10656	Lisa Shieh	15	gi_bleed	45875	0	5	\N	\N
10657	Panel Consensus	15	gi_bleed	45875	0	\N	\N	\N
11085	Andre Kumar	15	gi_bleed	45875	-3	5	Transfuse	\N
11351	Jonathan Chen	15	gi_bleed	45955	2	4	Lactate	\N
9083	Lisa Shieh	14	gi_bleed	50267	5	3	\N	\N
10059	Jonathan Chen	14	gi_bleed	50267	2	2	\N	Okay, but again, don't do too many points, since most people just do this or see in physical exam, not an order
10060	Panel Average	14	gi_bleed	50267	2	\N	\N	\N
10276	Andre Kumar	14	gi_bleed	50267	1	1	Stool test	\N
10658	Jason Hom	14	gi_bleed	50267	0	5	\N	\N
10659	Panel Consensus	14	gi_bleed	50267	0	\N	\N	\N
11365	Jonathan Chen	15	gi_bleed	44292	0	2	\N	Pre-procedure sedation?
10660	Jonathan Chen	14	gi_bleed	49904	0	4	\N	Wrong, they were looking for Prothrombin Time
10661	Lisa Shieh	14	gi_bleed	49904	0	5	\N	\N
10992	Panel Average	14	gi_bleed	49904	-2	\N	\N	\N
11046	Jason Hom	14	gi_bleed	49904	-2	5	\N	\N
11047	Panel Consensus	14	gi_bleed	49904	-2	\N	\N	\N
11086	Andre Kumar	14	gi_bleed	49904	-3	3	Thrombophilia	\N
7735	Jason Hom	14	gi_bleed	45759	10	5	\N	\N
7736	Lisa Shieh	14	gi_bleed	45759	10	5	\N	\N
8319	Panel Average	14	gi_bleed	45759	8	\N	\N	\N
8359	Panel Consensus	14	gi_bleed	45759	8	\N	\N	\N
8548	Jonathan Chen	14	gi_bleed	45759	7	4	Coags	Key diagnostic
9084	Andre Kumar	14	gi_bleed	45759	5	5	Coags	\N
7737	Jason Hom	15	gi_bleed	45759	10	5	\N	\N
7738	Lisa Shieh	15	gi_bleed	45759	10	5	\N	\N
8320	Panel Average	15	gi_bleed	45759	8	\N	\N	\N
8360	Panel Consensus	15	gi_bleed	45759	8	\N	\N	\N
8549	Jonathan Chen	15	gi_bleed	45759	7	4	Coags	Key diagnostic
9085	Andre Kumar	15	gi_bleed	45759	5	5	Coags	\N
7739	Jason Hom	16	gi_bleed	45759	10	5	\N	\N
7740	Lisa Shieh	16	gi_bleed	45759	10	5	\N	\N
8361	Panel Consensus	16	gi_bleed	45759	8	\N	\N	\N
8550	Jonathan Chen	16	gi_bleed	45759	7	4	Coags	Key diagnostic
8551	Panel Average	16	gi_bleed	45759	7	\N	\N	\N
10277	Andre Kumar	16	gi_bleed	45759	1	2	Coags	\N
7741	Jason Hom	2	gi_bleed	45759	10	5	\N	\N
7742	Lisa Shieh	2	gi_bleed	45759	10	5	\N	\N
8362	Panel Consensus	2	gi_bleed	45759	8	\N	\N	\N
8436	Panel Average	2	gi_bleed	45759	8	\N	\N	\N
8552	Jonathan Chen	2	gi_bleed	45759	7	4	Coags	Key diagnostic
9716	Andre Kumar	2	gi_bleed	45759	3	2	Coags	\N
10061	Andre Kumar	2	gi_bleed	45776	2	1	Coags	\N
10062	Panel Average	2	gi_bleed	45776	2	\N	\N	\N
7743	Jason Hom	14	gi_bleed	45770	10	4	\N	\N
7744	Lisa Shieh	14	gi_bleed	45770	10	5	\N	\N
8321	Panel Average	14	gi_bleed	45770	8	\N	\N	\N
8363	Panel Consensus	14	gi_bleed	45770	8	\N	\N	\N
8553	Jonathan Chen	14	gi_bleed	45770	7	4	Coags	Key diagnostic
9086	Andre Kumar	14	gi_bleed	45770	5	5	Coags	\N
7745	Jason Hom	15	gi_bleed	45770	10	4	\N	\N
7746	Lisa Shieh	15	gi_bleed	45770	10	5	\N	\N
8322	Panel Average	15	gi_bleed	45770	8	\N	\N	\N
8364	Panel Consensus	15	gi_bleed	45770	8	\N	\N	\N
8554	Jonathan Chen	15	gi_bleed	45770	7	4	Coags	Key diagnostic
9087	Andre Kumar	15	gi_bleed	45770	5	4	Coags	\N
7747	Jason Hom	2	gi_bleed	45770	10	4	\N	\N
7748	Lisa Shieh	2	gi_bleed	45770	10	5	\N	\N
8365	Panel Consensus	2	gi_bleed	45770	8	\N	\N	\N
8437	Panel Average	2	gi_bleed	45770	8	\N	\N	\N
8555	Jonathan Chen	2	gi_bleed	45770	7	4	Coags	Key diagnostic
9717	Andre Kumar	2	gi_bleed	45770	3	2	Coags	\N
9504	Andre Kumar	2	gi_bleed	62103	4	5	HIV	\N
10234	Panel Average	2	gi_bleed	62103	1	\N	\N	\N
10662	Jason Hom	2	gi_bleed	62103	0	4	\N	\N
10663	Jonathan Chen	2	gi_bleed	62103	0	2	\N	\N
10664	Lisa Shieh	2	gi_bleed	62103	0	3	\N	\N
10665	Panel Consensus	2	gi_bleed	62103	0	\N	\N	\N
7749	Jason Hom	14	gi_bleed	45927	10	5	\N	\N
7750	Jonathan Chen	14	gi_bleed	45927	10	5	RBC	\N
7751	Panel Consensus	14	gi_bleed	45927	10	\N	\N	\N
8366	Andre Kumar	14	gi_bleed	45927	8	5	Transfuse	\N
8733	Panel Average	14	gi_bleed	45927	6	\N	\N	\N
10666	Lisa Shieh	14	gi_bleed	45927	0	3	\N	\N
7752	Andre Kumar	15	gi_bleed	45927	10	5	Transfuse	\N
7753	Jason Hom	15	gi_bleed	45927	10	5	\N	\N
7754	Jonathan Chen	15	gi_bleed	45927	10	5	RBC	\N
7755	Lisa Shieh	15	gi_bleed	45927	10	5	\N	\N
7756	Panel Average	15	gi_bleed	45927	10	\N	\N	\N
7757	Panel Consensus	15	gi_bleed	45927	10	\N	\N	\N
7758	Jason Hom	16	gi_bleed	45927	10	5	\N	\N
7759	Jonathan Chen	16	gi_bleed	45927	10	5	RBC	\N
7760	Lisa Shieh	16	gi_bleed	45927	10	5	\N	\N
7761	Panel Consensus	16	gi_bleed	45927	10	\N	\N	\N
8261	Panel Average	16	gi_bleed	45927	9	\N	\N	\N
8556	Andre Kumar	16	gi_bleed	45927	7	1	Transfuse	\N
7762	Jason Hom	2	gi_bleed	45927	10	5	\N	\N
7763	Jonathan Chen	2	gi_bleed	45927	10	5	RBC	\N
7764	Lisa Shieh	2	gi_bleed	45927	10	5	\N	\N
7765	Panel Consensus	2	gi_bleed	45927	10	\N	\N	\N
8262	Panel Average	2	gi_bleed	45927	9	\N	\N	\N
8557	Andre Kumar	2	gi_bleed	45927	7	2	Transfuse	If not done previously, otherwise 0
11349	Jonathan Chen	15	gi_bleed	45832	0	2	\N	?Mechanical ventilation? Airway protection?
10278	Andre Kumar	15	gi_bleed	44424	1	1	Hepatic Encephalopathy	\N
10667	Lisa Shieh	15	gi_bleed	44424	0	3	\N	\N
10668	Panel Consensus	15	gi_bleed	44424	0	\N	\N	\N
10988	Panel Average	15	gi_bleed	44424	-1	\N	\N	\N
11048	Jonathan Chen	15	gi_bleed	44424	-2	2	Lactulose	Maybe even negative points? Giving lactulose to make patient have diarrhea while they are actively bleeding out seems bad
11160	Jason Hom	15	gi_bleed	44424	-5	4	\N	\N
11437	Jonathan Chen	14	gi_bleed	49173	0	2	\N	?Intoxication not really active issue
9718	Jonathan Chen	14	gi_bleed	63725	3	4	Lactate	\N
10063	Andre Kumar	14	gi_bleed	63725	2	4	Lactate	\N
10279	Panel Consensus	14	gi_bleed	63725	1	\N	\N	\N
10386	Panel Average	14	gi_bleed	63725	1	\N	\N	\N
10669	Jason Hom	14	gi_bleed	63725	0	4	\N	\N
10670	Lisa Shieh	14	gi_bleed	63725	0	3	\N	\N
7766	Jason Hom	14	gi_bleed	44198	10	4	\N	\N
7767	Lisa Shieh	14	gi_bleed	44198	10	5	ivf	\N
8323	Panel Average	14	gi_bleed	44198	8	\N	\N	\N
8367	Panel Consensus	14	gi_bleed	44198	8	\N	\N	\N
9088	Andre Kumar	14	gi_bleed	44198	5	2	Fluids	\N
9719	Jonathan Chen	14	gi_bleed	44198	3	3	IVF	Okay for resuscitation, but needs blood more
7768	Jason Hom	15	gi_bleed	44198	10	4	\N	\N
7769	Lisa Shieh	15	gi_bleed	44198	10	5	\N	\N
8229	Panel Average	15	gi_bleed	44198	9	\N	\N	\N
8368	Andre Kumar	15	gi_bleed	44198	8	2	Fluids	\N
8369	Panel Consensus	15	gi_bleed	44198	8	\N	\N	\N
9720	Jonathan Chen	15	gi_bleed	44198	3	3	IVF	Okay for resuscitation, but needs blood more
11457	Jonathan Chen	15	gi_bleed	44441	0	2	\N	?Pre-intubation for airway protection?
11450	Jonathan Chen	14	gi_bleed	61993	9	4	FFP	\N
7770	Jason Hom	14	gi_bleed	45877	10	5	\N	\N
8263	Jonathan Chen	14	gi_bleed	45877	9	4	FFP	\N
8370	Andre Kumar	14	gi_bleed	45877	8	5	Transfuse	\N
8371	Panel Consensus	14	gi_bleed	45877	8	\N	\N	\N
8734	Panel Average	14	gi_bleed	45877	6	\N	\N	\N
10671	Lisa Shieh	14	gi_bleed	45877	0	3	\N	\N
11391	Jonathan Chen	15	gi_bleed	61993	9	4	FFP	\N
7771	Jason Hom	15	gi_bleed	45877	10	5	\N	\N
7772	Lisa Shieh	15	gi_bleed	45877	10	5	\N	\N
8230	Panel Average	15	gi_bleed	45877	9	\N	\N	\N
8264	Jonathan Chen	15	gi_bleed	45877	9	4	FFP	\N
8372	Andre Kumar	15	gi_bleed	45877	8	5	Transfuse	\N
8373	Panel Consensus	15	gi_bleed	45877	8	\N	\N	\N
11407	Jonathan Chen	16	gi_bleed	61993	9	4	FFP	\N
7773	Jason Hom	16	gi_bleed	45877	10	5	\N	\N
7774	Lisa Shieh	16	gi_bleed	45877	10	5	\N	\N
8265	Jonathan Chen	16	gi_bleed	45877	9	4	FFP	\N
8266	Panel Average	16	gi_bleed	45877	9	\N	\N	\N
8374	Panel Consensus	16	gi_bleed	45877	8	\N	\N	\N
8558	Andre Kumar	16	gi_bleed	45877	7	2	Transfuse	no points if done previously
7775	Jason Hom	14	gi_bleed	65702	10	5	\N	\N
7776	Lisa Shieh	14	gi_bleed	65702	10	3	\N	\N
8231	Panel Average	14	gi_bleed	65702	9	\N	\N	\N
8267	Jonathan Chen	14	gi_bleed	65702	9	4	FFP	\N
8375	Andre Kumar	14	gi_bleed	65702	8	5	Transfuse	\N
8376	Panel Consensus	14	gi_bleed	65702	8	\N	\N	\N
7777	Jason Hom	15	gi_bleed	65702	10	5	\N	\N
7778	Lisa Shieh	15	gi_bleed	65702	10	5	\N	\N
8232	Panel Average	15	gi_bleed	65702	9	\N	\N	\N
8268	Jonathan Chen	15	gi_bleed	65702	9	4	FFP	\N
8377	Andre Kumar	15	gi_bleed	65702	8	5	Transfuse	\N
8378	Panel Consensus	15	gi_bleed	65702	8	\N	\N	\N
7779	Jason Hom	16	gi_bleed	65702	10	5	\N	\N
7780	Lisa Shieh	16	gi_bleed	65702	10	5	\N	\N
8269	Jonathan Chen	16	gi_bleed	65702	9	4	FFP	\N
8270	Panel Average	16	gi_bleed	65702	9	\N	\N	\N
8379	Panel Consensus	16	gi_bleed	65702	8	\N	\N	\N
8559	Andre Kumar	16	gi_bleed	65702	7	2	Transfuse	no points if done previously
8380	Jason Hom	14	gi_bleed	65646	8	4	\N	\N
10219	Panel Average	14	gi_bleed	65646	2	\N	\N	\N
10672	Jonathan Chen	14	gi_bleed	65646	0	2	\N	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
10673	Lisa Shieh	14	gi_bleed	65646	0	3	\N	\N
10674	Panel Consensus	14	gi_bleed	65646	0	\N	\N	\N
11087	Andre Kumar	14	gi_bleed	65646	-3	5	Transfuse	No indication
8381	Jason Hom	15	gi_bleed	65646	8	4	\N	\N
10220	Panel Average	15	gi_bleed	65646	2	\N	\N	\N
10675	Jonathan Chen	15	gi_bleed	65646	0	2	\N	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
10676	Lisa Shieh	15	gi_bleed	65646	0	3	\N	\N
10677	Panel Consensus	15	gi_bleed	65646	0	\N	\N	\N
11088	Andre Kumar	15	gi_bleed	65646	-3	5	Transfuse	\N
11465	Jonathan Chen	14	gi_bleed	45956	0	2	\N	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
11306	Jonathan Chen	15	gi_bleed	61976	0	2	\N	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
7781	Jason Hom	15	gi_bleed	45956	10	5	\N	\N
7782	Lisa Shieh	15	gi_bleed	45956	10	5	\N	\N
8847	Panel Average	15	gi_bleed	45956	6	\N	\N	\N
10678	Jonathan Chen	15	gi_bleed	45956	0	2	\N	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
10679	Panel Consensus	15	gi_bleed	45956	0	\N	\N	\N
11089	Andre Kumar	15	gi_bleed	45956	-3	5	Transfuse	\N
11408	Jonathan Chen	14	gi_bleed	45748	10	5	RBC	\N
7783	Jason Hom	14	gi_bleed	61975	10	5	\N	\N
7784	Jonathan Chen	14	gi_bleed	61975	10	5	RBC	\N
7785	Lisa Shieh	14	gi_bleed	61975	10	3	\N	do not know hbg yet
7786	Panel Consensus	14	gi_bleed	61975	10	\N	\N	\N
8233	Panel Average	14	gi_bleed	61975	9	\N	\N	\N
8382	Andre Kumar	14	gi_bleed	61975	8	5	Transfuse	\N
11467	Jonathan Chen	15	gi_bleed	45748	10	5	RBC	\N
7787	Andre Kumar	15	gi_bleed	61975	10	5	Transfuse	\N
7788	Jason Hom	15	gi_bleed	61975	10	5	\N	\N
7789	Jonathan Chen	15	gi_bleed	61975	10	5	RBC	\N
7790	Lisa Shieh	15	gi_bleed	61975	10	5	\N	\N
7791	Panel Average	15	gi_bleed	61975	10	\N	\N	\N
7792	Panel Consensus	15	gi_bleed	61975	10	\N	\N	\N
7793	Jason Hom	16	gi_bleed	61975	10	5	\N	\N
7794	Jonathan Chen	16	gi_bleed	61975	10	5	RBC	\N
7795	Lisa Shieh	16	gi_bleed	61975	10	5	\N	\N
7796	Panel Consensus	16	gi_bleed	61975	10	\N	\N	\N
8271	Panel Average	16	gi_bleed	61975	9	\N	\N	\N
8560	Andre Kumar	16	gi_bleed	61975	7	2	Transfuse	no points if done previously
7797	Jason Hom	14	gi_bleed	65640	10	5	\N	\N
7798	Jonathan Chen	14	gi_bleed	65640	10	5	RBC	\N
7799	Lisa Shieh	14	gi_bleed	65640	10	3	\N	\N
7800	Panel Consensus	14	gi_bleed	65640	10	\N	\N	\N
8234	Panel Average	14	gi_bleed	65640	9	\N	\N	\N
8383	Andre Kumar	14	gi_bleed	65640	8	5	Transfuse	\N
7801	Andre Kumar	15	gi_bleed	65640	10	5	Transfuse	\N
7802	Jason Hom	15	gi_bleed	65640	10	5	\N	\N
7803	Jonathan Chen	15	gi_bleed	65640	10	5	RBC	\N
7804	Lisa Shieh	15	gi_bleed	65640	10	5	\N	\N
7805	Panel Average	15	gi_bleed	65640	10	\N	\N	\N
7806	Panel Consensus	15	gi_bleed	65640	10	\N	\N	\N
7807	Jason Hom	16	gi_bleed	65640	10	5	\N	\N
7808	Jonathan Chen	16	gi_bleed	65640	10	5	RBC	\N
7809	Lisa Shieh	16	gi_bleed	65640	10	5	\N	\N
7810	Panel Consensus	16	gi_bleed	65640	10	\N	\N	\N
8272	Panel Average	16	gi_bleed	65640	9	\N	\N	\N
8561	Andre Kumar	16	gi_bleed	65640	7	2	Transfuse	no points if done previously
7811	Jason Hom	2	gi_bleed	65640	10	5	\N	\N
7812	Jonathan Chen	2	gi_bleed	65640	10	5	RBC	\N
7813	Lisa Shieh	2	gi_bleed	65640	10	5	\N	\N
7814	Panel Consensus	2	gi_bleed	65640	10	\N	\N	\N
8273	Panel Average	2	gi_bleed	65640	9	\N	\N	\N
8562	Andre Kumar	2	gi_bleed	65640	7	3	Transfuse	\N
11356	Jonathan Chen	14	gi_bleed	50581	0	2	\N	\N
11291	Jonathan Chen	15	gi_bleed	50581	0	2	\N	\N
7815	Jason Hom	14	gi_bleed	50618	10	5	\N	\N
7816	Jonathan Chen	14	gi_bleed	50618	10	5	RBC	\N
7817	Panel Consensus	14	gi_bleed	50618	10	\N	\N	\N
8384	Andre Kumar	14	gi_bleed	50618	8	3	Transfuse	\N
8735	Panel Average	14	gi_bleed	50618	6	\N	\N	\N
10680	Lisa Shieh	14	gi_bleed	50618	0	3	\N	\N
7818	Andre Kumar	15	gi_bleed	50618	10	5	Transfuse	\N
7819	Jason Hom	15	gi_bleed	50618	10	5	\N	\N
7820	Jonathan Chen	15	gi_bleed	50618	10	5	RBC	\N
7821	Lisa Shieh	15	gi_bleed	50618	10	5	\N	\N
7822	Panel Average	15	gi_bleed	50618	10	\N	\N	\N
7823	Panel Consensus	15	gi_bleed	50618	10	\N	\N	\N
11235	Jonathan Chen	14	gi_bleed	45870	2	3	\N	Hemodynamic stability assessment?
7824	Jason Hom	14	gi_bleed	45945	10	5	\N	\N
7825	Lisa Shieh	14	gi_bleed	45945	10	5	blood type verification	\N
7826	Panel Consensus	14	gi_bleed	45945	10	\N	\N	\N
8274	Panel Average	14	gi_bleed	45945	9	\N	\N	\N
8563	Andre Kumar	14	gi_bleed	45945	7	5	Transfuse	\N
10280	Jonathan Chen	14	gi_bleed	45945	1	2	Type and Screen	\N
7827	Andre Kumar	15	gi_bleed	45945	10	5	Transfuse	\N
7828	Jason Hom	15	gi_bleed	45945	10	5	\N	\N
7829	Lisa Shieh	15	gi_bleed	45945	10	5	\N	\N
7830	Panel Average	15	gi_bleed	45945	10	\N	\N	\N
7831	Panel Consensus	15	gi_bleed	45945	10	\N	\N	\N
10281	Jonathan Chen	15	gi_bleed	45945	1	2	Type and Screen	\N
7832	Jason Hom	14	gi_bleed	45869	10	5	\N	\N
8564	Lisa Shieh	14	gi_bleed	45869	7	3	\N	\N
8736	Panel Average	14	gi_bleed	45869	6	\N	\N	\N
8737	Panel Consensus	14	gi_bleed	45869	6	\N	\N	\N
9089	Jonathan Chen	14	gi_bleed	45869	5	2	US Abdomen	Okay to think about checking this, as long as not delaying immediate treatment
10282	Andre Kumar	14	gi_bleed	45869	1	1	Imaging	\N
11049	Andre Kumar	16	gi_bleed	45869	-2	4	Imaging	delays care
11050	Panel Average	16	gi_bleed	45869	-2	\N	\N	\N
7833	Jason Hom	2	gi_bleed	45869	10	5	\N	\N
8455	Panel Average	2	gi_bleed	45869	7	\N	\N	\N
8565	Lisa Shieh	2	gi_bleed	45869	7	3	imaging	\N
8738	Panel Consensus	2	gi_bleed	45869	6	\N	\N	\N
9090	Andre Kumar	2	gi_bleed	45869	5	2	Imaging	\N
9091	Jonathan Chen	2	gi_bleed	45869	5	2	US Abdomen	\N
11051	Andre Kumar	14	gi_bleed	49408	-2	3	Imaging	\N
11052	Panel Average	14	gi_bleed	49408	-2	\N	\N	\N
11053	Andre Kumar	16	gi_bleed	49408	-2	5	Imaging	delays care
11054	Panel Average	16	gi_bleed	49408	-2	\N	\N	\N
7834	Jason Hom	2	gi_bleed	49408	10	5	\N	\N
8456	Panel Average	2	gi_bleed	49408	7	\N	\N	\N
8566	Lisa Shieh	2	gi_bleed	49408	7	3	\N	\N
8739	Panel Consensus	2	gi_bleed	49408	6	\N	\N	\N
9092	Andre Kumar	2	gi_bleed	49408	5	4	Imaging	\N
9093	Jonathan Chen	2	gi_bleed	49408	5	2	US Abdomen	\N
7835	Jason Hom	14	gi_bleed	46343	10	5	\N	\N
8567	Lisa Shieh	14	gi_bleed	46343	7	5	ultrasound	\N
8740	Panel Consensus	14	gi_bleed	46343	6	\N	\N	\N
9094	Jonathan Chen	14	gi_bleed	46343	5	2	US Abdomen	\N
9095	Panel Average	14	gi_bleed	46343	5	\N	\N	\N
11055	Andre Kumar	14	gi_bleed	46343	-2	2	Imaging	\N
11056	Andre Kumar	16	gi_bleed	46343	-2	5	Imaging	delays care
11057	Panel Average	16	gi_bleed	46343	-2	\N	\N	\N
7836	Jason Hom	2	gi_bleed	46343	10	5	\N	\N
7837	Lisa Shieh	2	gi_bleed	46343	10	5	\N	\N
8324	Panel Average	2	gi_bleed	46343	8	\N	\N	\N
8741	Panel Consensus	2	gi_bleed	46343	6	\N	\N	\N
9096	Andre Kumar	2	gi_bleed	46343	5	3	Imaging	\N
9097	Jonathan Chen	2	gi_bleed	46343	5	2	US Abdomen	\N
7838	Andre Kumar	14	gi_bleed	45969	10	5	Endoscopy	\N
7839	Jason Hom	14	gi_bleed	45969	10	5	\N	\N
7840	Jonathan Chen	14	gi_bleed	45969	10	5	GI-EGD	GI won't take patient yet, but points for preparing
7841	Lisa Shieh	14	gi_bleed	45969	10	5	\N	\N
7842	Panel Average	14	gi_bleed	45969	10	\N	\N	\N
7843	Panel Consensus	14	gi_bleed	45969	10	\N	\N	\N
7844	Andre Kumar	15	gi_bleed	45969	10	5	Endoscopy	\N
7845	Jason Hom	15	gi_bleed	45969	10	5	\N	\N
7846	Jonathan Chen	15	gi_bleed	45969	10	5	GI-EGD	\N
7847	Lisa Shieh	15	gi_bleed	45969	10	5	\N	\N
7848	Panel Average	15	gi_bleed	45969	10	\N	\N	\N
7849	Panel Consensus	15	gi_bleed	45969	10	\N	\N	\N
7850	Andre Kumar	16	gi_bleed	45969	10	4	Endoscopy	\N
7851	Jason Hom	16	gi_bleed	45969	10	5	\N	\N
7852	Jonathan Chen	16	gi_bleed	45969	10	5	GI-EGD	\N
7853	Lisa Shieh	16	gi_bleed	45969	10	5	\N	\N
7854	Panel Average	16	gi_bleed	45969	10	\N	\N	\N
7855	Panel Consensus	16	gi_bleed	45969	10	\N	\N	\N
10283	Andre Kumar	14	gi_bleed	45873	1	3	Urinalysis	\N
10396	Panel Average	14	gi_bleed	45873	0	\N	\N	\N
10681	Jason Hom	14	gi_bleed	45873	0	4	\N	\N
10682	Jonathan Chen	14	gi_bleed	45873	0	2	\N	Irrelevant diagnostic?
10683	Lisa Shieh	14	gi_bleed	45873	0	3	\N	\N
10684	Panel Consensus	14	gi_bleed	45873	0	\N	\N	\N
11281	Jonathan Chen	14	gi_bleed	46348	0	4	\N	\N
7856	Jason Hom	14	gi_bleed	50372	10	5	\N	\N
7857	Lisa Shieh	14	gi_bleed	50372	10	5	\N	\N
7858	Panel Consensus	14	gi_bleed	50372	10	\N	\N	\N
8438	Panel Average	14	gi_bleed	50372	8	\N	\N	\N
9721	Andre Kumar	14	gi_bleed	50372	3	4	Informed Consent	\N
10685	Jonathan Chen	14	gi_bleed	50372	0	2	\N	\N
8275	Jonathan Chen	14	gi_bleed	44001	9	4	Vitamin K	\N
8385	Jason Hom	14	gi_bleed	44001	8	4	\N	\N
8568	Lisa Shieh	14	gi_bleed	44001	7	3	\N	risk of anaphylaxis
8569	Panel Consensus	14	gi_bleed	44001	7	\N	\N	\N
8670	Panel Average	14	gi_bleed	44001	7	\N	\N	\N
9098	Andre Kumar	14	gi_bleed	44001	5	4	Coagulopathy Reversal	\N
7859	Lisa Shieh	15	gi_bleed	44001	10	5	\N	\N
8276	Jonathan Chen	15	gi_bleed	44001	9	4	Vitamin K	\N
8386	Jason Hom	15	gi_bleed	44001	8	4	\N	\N
8439	Panel Average	15	gi_bleed	44001	8	\N	\N	\N
8570	Panel Consensus	15	gi_bleed	44001	7	\N	\N	\N
9099	Andre Kumar	15	gi_bleed	44001	5	3	Coagulopathy Reversal	\N
7860	Lisa Shieh	16	gi_bleed	44001	10	5	\N	\N
8277	Jonathan Chen	16	gi_bleed	44001	9	4	Vitamin K	\N
8387	Jason Hom	16	gi_bleed	44001	8	4	\N	\N
8440	Panel Average	16	gi_bleed	44001	8	\N	\N	\N
8571	Panel Consensus	16	gi_bleed	44001	7	\N	\N	\N
9100	Andre Kumar	16	gi_bleed	44001	5	5	Coagulopathy Reversal	5 pts if no FFP or vitamin K given previously, otherwise 0
9101	Andre Kumar	2	gi_bleed	44001	5	5	Coagulopathy Reversal	\N
9102	Panel Average	2	gi_bleed	44001	5	\N	\N	\N
7861	Lisa Shieh	15	gi_bleed	44404	10	5	\N	\N
8388	Jason Hom	15	gi_bleed	44404	8	4	\N	\N
8572	Panel Consensus	15	gi_bleed	44404	7	\N	\N	\N
8671	Panel Average	15	gi_bleed	44404	7	\N	\N	\N
9103	Jonathan Chen	15	gi_bleed	44404	5	2	Vitamin K	Onset of action a bit too slow
10064	Andre Kumar	15	gi_bleed	44404	2	2	Bleeding Medication	\N
7862	Lisa Shieh	16	gi_bleed	44404	10	5	\N	\N
8389	Jason Hom	16	gi_bleed	44404	8	4	\N	\N
8441	Panel Average	16	gi_bleed	44404	8	\N	\N	\N
8573	Panel Consensus	16	gi_bleed	44404	7	\N	\N	\N
9104	Andre Kumar	16	gi_bleed	44404	5	2	Coagulopathy Reversal	5 pts if no FFP or vitamin K given previously, otherwise 0
9105	Jonathan Chen	16	gi_bleed	44404	5	2	Vitamin K	Onset of action a bit too slow
8390	Jason Hom	14	gi_bleed	44382	8	4	\N	\N
9106	Jonathan Chen	14	gi_bleed	44382	5	2	Vitamin K	Onset of action a bit too slow
9107	Lisa Shieh	14	gi_bleed	44382	5	3	\N	\N
9606	Panel Average	14	gi_bleed	44382	3	\N	\N	\N
11058	Panel Consensus	14	gi_bleed	44382	-2	\N	\N	\N
11090	Andre Kumar	14	gi_bleed	44382	-3	5	Coagulopathy Reversal	Studies have shown SubQ vitamin K is similar to placebo (PMID: 16505257 )
8391	Jason Hom	15	gi_bleed	44382	8	4	\N	\N
8574	Lisa Shieh	15	gi_bleed	44382	7	3	\N	\N
9108	Jonathan Chen	15	gi_bleed	44382	5	2	Vitamin K	Onset of action a bit too slow
9505	Panel Average	15	gi_bleed	44382	4	\N	\N	\N
11059	Panel Consensus	15	gi_bleed	44382	-2	\N	\N	\N
11091	Andre Kumar	15	gi_bleed	44382	-3	5	Bleeding Medication	\N
11419	Jonathan Chen	14	gi_bleed	46096	0	2	\N	\N
10981	Andre Kumar	14	gi_bleed	46018	-1	3	Imaging	Delays care
10982	Panel Average	14	gi_bleed	46018	-1	\N	\N	\N
8392	Jason Hom	14	gi_bleed	45818	8	4	\N	\N
9916	Panel Average	14	gi_bleed	45818	3	\N	\N	\N
10686	Andre Kumar	14	gi_bleed	45818	0	1	Imaging	\N
10687	Jonathan Chen	14	gi_bleed	45818	0	2	CXR	Irrelevant diagnostic?
10688	Lisa Shieh	14	gi_bleed	45818	0	3	\N	\N
10689	Panel Consensus	14	gi_bleed	45818	0	\N	\N	\N
8393	Jason Hom	15	gi_bleed	45818	8	4	\N	\N
10065	Panel Average	15	gi_bleed	45818	2	\N	\N	\N
10690	Jonathan Chen	15	gi_bleed	45818	0	2	CXR	Irrelevant diagnostic?
10691	Lisa Shieh	15	gi_bleed	45818	0	3	\N	\N
10692	Panel Consensus	15	gi_bleed	45818	0	\N	\N	\N
11060	Andre Kumar	15	gi_bleed	45818	-2	1	Imaging	delays care
10693	Andre Kumar	2	gi_bleed	45818	0	1	Imaging	\N
10694	Panel Average	2	gi_bleed	45818	0	\N	\N	\N
11389	Jonathan Chen	14	gi_bleed	50200	0	2	CXR	Irrelevant diagnostic?
8394	Jason Hom	14	gi_bleed	45801	8	4	\N	\N
9917	Panel Average	14	gi_bleed	45801	3	\N	\N	\N
10695	Andre Kumar	14	gi_bleed	45801	0	2	Imaging	\N
10696	Jonathan Chen	14	gi_bleed	45801	0	2	CXR	Irrelevant diagnostic?
10697	Lisa Shieh	14	gi_bleed	45801	0	3	\N	\N
10698	Panel Consensus	14	gi_bleed	45801	0	\N	\N	\N
11299	Jonathan Chen	30	meningitis	56492	1	3	Pain Control	Minor points for symptom control?
11236	Jonathan Chen	31	meningitis	56492	1	3	Pain Control	Minor points for symptom control?
8395	Jason Hom	30	meningitis	44281	8	4	\N	\N
9109	Panel Consensus	30	meningitis	44281	5	\N	\N	\N
9431	Panel Average	30	meningitis	44281	5	\N	\N	\N
9506	Lisa Shieh	30	meningitis	44281	4	4	\N	\N
10066	Andre Kumar	30	meningitis	44281	2	2	Fever Medication	\N
10284	Jonathan Chen	30	meningitis	44281	1	3	Pain Control	Minor points for symptom control?
8396	Jason Hom	31	meningitis	44281	8	4	\N	\N
8575	Lisa Shieh	31	meningitis	44281	7	3	\N	\N
8742	Panel Average	31	meningitis	44281	6	\N	\N	\N
9110	Panel Consensus	31	meningitis	44281	5	\N	\N	\N
9722	Andre Kumar	31	meningitis	44281	3	2	Fever Medication	\N
10285	Jonathan Chen	31	meningitis	44281	1	3	Pain Control	Minor points for symptom control?
11300	Jonathan Chen	33	meningitis	44281	1	3	Pain Control	Minor points for symptom control?
11415	Jonathan Chen	30	meningitis	44310	1	3	Pain Control	Minor points for symptom control?
8397	Jason Hom	30	meningitis	44278	8	4	\N	\N
9507	Panel Consensus	30	meningitis	44278	4	\N	\N	\N
9585	Panel Average	30	meningitis	44278	4	\N	\N	\N
9723	Lisa Shieh	30	meningitis	44278	3	3	\N	\N
10286	Jonathan Chen	30	meningitis	44278	1	3	Pain Control	Minor points for symptom control?
10699	Andre Kumar	30	meningitis	44278	0	1	Fever Medication	\N
11466	Jonathan Chen	31	meningitis	44310	1	3	Pain Control	Minor points for symptom control?
10067	Andre Kumar	31	meningitis	44278	2	2	Fever Medication	\N
10068	Panel Average	31	meningitis	44278	2	\N	\N	\N
11257	Jonathan Chen	30	meningitis	48829	0	4	\N	Irrelevant diagnostics. Probably trying to order medicine
8398	Jason Hom	30	meningitis	44615	8	4	\N	\N
8870	Panel Average	30	meningitis	44615	5	\N	\N	\N
9111	Andre Kumar	30	meningitis	44615	5	4	Antiviral	reasonable for mollaret's meningitis
9724	Lisa Shieh	30	meningitis	44615	3	3	\N	\N
10700	Jonathan Chen	30	meningitis	44615	0	3	\N	Doesn't meet guideline recs for empiric treatment
10701	Panel Consensus	30	meningitis	44615	0	\N	\N	\N
9112	Andre Kumar	31	meningitis	44615	5	3	Antiviral	No points if already ordered
9113	Lisa Shieh	31	meningitis	44615	5	3	\N	\N
9607	Panel Average	31	meningitis	44615	3	\N	\N	\N
10702	Jason Hom	31	meningitis	44615	0	4	\N	\N
10703	Jonathan Chen	31	meningitis	44615	0	3	\N	Doesn't meet guideline recs for empiric treatment
10704	Panel Consensus	31	meningitis	44615	0	\N	\N	\N
9508	Andre Kumar	33	meningitis	44615	4	2	Antivirals	\N
9509	Jason Hom	33	meningitis	44615	4	4	\N	\N
9586	Panel Average	33	meningitis	44615	4	\N	\N	\N
9725	Lisa Shieh	33	meningitis	44615	3	3	\N	\N
10705	Jonathan Chen	33	meningitis	44615	0	3	\N	Doesn't meet guideline recs for empiric treatment
10706	Panel Consensus	33	meningitis	44615	0	\N	\N	\N
11332	Jonathan Chen	30	meningitis	48770	0	3	\N	Low yield
11260	Jonathan Chen	33	meningitis	48770	0	3	\N	Low yield
7863	Lisa Shieh	30	meningitis	44595	10	4	\N	\N
9918	Panel Average	30	meningitis	44595	3	\N	\N	\N
10707	Andre Kumar	30	meningitis	44595	0	3	Antibiotics	\N
10708	Jonathan Chen	30	meningitis	44595	0	3	\N	Doesn't meet guideline recs for empiric treatment
10709	Panel Consensus	30	meningitis	44595	0	\N	\N	\N
11061	Jason Hom	30	meningitis	44595	-2	5	\N	\N
9114	Lisa Shieh	31	meningitis	44595	5	3	\N	\N
10287	Panel Average	31	meningitis	44595	1	\N	\N	\N
10710	Andre Kumar	31	meningitis	44595	0	5	Antibiotics	\N
10711	Jonathan Chen	31	meningitis	44595	0	3	\N	Doesn't meet guideline recs for empiric treatment
10712	Panel Consensus	31	meningitis	44595	0	\N	\N	\N
11062	Jason Hom	31	meningitis	44595	-2	5	\N	\N
9726	Lisa Shieh	33	meningitis	44595	3	3	\N	\N
10397	Panel Average	33	meningitis	44595	0	\N	\N	\N
10713	Andre Kumar	33	meningitis	44595	0	5	Antibiotics	\N
10714	Jonathan Chen	33	meningitis	44595	0	3	\N	Doesn't meet guideline recs for empiric treatment
10715	Panel Consensus	33	meningitis	44595	0	\N	\N	\N
11063	Jason Hom	33	meningitis	44595	-2	5	\N	\N
9115	Jason Hom	31	meningitis	61864	5	5	\N	\N
9727	Lisa Shieh	31	meningitis	61864	3	3	\N	\N
9728	Panel Consensus	31	meningitis	61864	3	\N	\N	\N
9919	Panel Average	31	meningitis	61864	3	\N	\N	\N
10069	Jonathan Chen	31	meningitis	61864	2	2	HIV	\N
10716	Andre Kumar	31	meningitis	61864	0	4	STD Testing	\N
9116	Andre Kumar	30	meningitis	46093	5	5	CSF	\N
9117	Jason Hom	30	meningitis	46093	5	5	\N	\N
9118	Lisa Shieh	30	meningitis	46093	5	3	\N	\N
9119	Panel Average	30	meningitis	46093	5	\N	\N	\N
9120	Panel Consensus	30	meningitis	46093	5	\N	\N	\N
10288	Jonathan Chen	30	meningitis	46093	1	3	Pregnancy Test	\N
7864	Jason Hom	30	meningitis	45901	10	5	\N	\N
7865	Lisa Shieh	30	meningitis	45901	10	5	\N	\N
7866	Panel Consensus	30	meningitis	45901	10	\N	\N	\N
8294	Panel Average	30	meningitis	45901	9	\N	\N	\N
8576	Jonathan Chen	30	meningitis	45901	7	4	Blood Cultures	\N
8743	Andre Kumar	30	meningitis	45901	6	5	Blood Cultures	\N
7867	Panel Consensus	31	meningitis	45901	10	\N	\N	\N
8577	Jonathan Chen	31	meningitis	45901	7	4	Blood Cultures	\N
9729	Lisa Shieh	31	meningitis	45901	3	3	\N	\N
10070	Jason Hom	31	meningitis	45901	2	5	\N	\N
10071	Panel Average	31	meningitis	45901	2	\N	\N	\N
10289	Andre Kumar	31	meningitis	45901	1	1	Blood Cultures	\N
7868	Panel Consensus	33	meningitis	45901	10	\N	\N	\N
8578	Jonathan Chen	33	meningitis	45901	7	4	Blood Cultures	\N
9510	Andre Kumar	33	meningitis	45901	4	4	Blood Cultures	\N
9730	Lisa Shieh	33	meningitis	45901	3	3	\N	\N
9731	Panel Average	33	meningitis	45901	3	\N	\N	\N
10072	Jason Hom	33	meningitis	45901	2	5	\N	\N
7869	Jason Hom	30	meningitis	45752	10	5	\N	\N
7870	Lisa Shieh	30	meningitis	45752	10	4	\N	\N
7871	Panel Consensus	30	meningitis	45752	10	\N	\N	\N
8295	Panel Average	30	meningitis	45752	9	\N	\N	\N
8579	Jonathan Chen	30	meningitis	45752	7	4	Blood Cultures	\N
8744	Andre Kumar	30	meningitis	45752	6	5	Blood Cultures	\N
7872	Panel Consensus	31	meningitis	45752	10	\N	\N	\N
8580	Jonathan Chen	31	meningitis	45752	7	4	Blood Cultures	\N
9732	Lisa Shieh	31	meningitis	45752	3	3	\N	\N
10073	Jason Hom	31	meningitis	45752	2	5	\N	\N
10074	Panel Average	31	meningitis	45752	2	\N	\N	\N
10290	Andre Kumar	31	meningitis	45752	1	2	Blood cultures	"No points if already ordered lower points here assuming pt got abx already"
7873	Panel Consensus	33	meningitis	45752	10	\N	\N	\N
8581	Jonathan Chen	33	meningitis	45752	7	4	Blood Cultures	\N
9511	Andre Kumar	33	meningitis	45752	4	4	Blood Cultures	\N
9733	Lisa Shieh	33	meningitis	45752	3	3	\N	\N
9734	Panel Average	33	meningitis	45752	3	\N	\N	\N
10075	Jason Hom	33	meningitis	45752	2	5	\N	\N
11383	Jonathan Chen	30	meningitis	44439	5	3	IVF	\N
8582	Lisa Shieh	30	meningitis	44290	7	4	\N	\N
9121	Jason Hom	30	meningitis	44290	5	4	\N	\N
9122	Jonathan Chen	30	meningitis	44290	5	3	IVF	\N
9123	Panel Average	30	meningitis	44290	5	\N	\N	\N
9124	Panel Consensus	30	meningitis	44290	5	\N	\N	\N
9735	Andre Kumar	30	meningitis	44290	3	5	Fluids	\N
7874	Jason Hom	30	meningitis	45793	10	4	cbc	\N
8457	Panel Average	30	meningitis	45793	7	\N	\N	\N
8583	Lisa Shieh	30	meningitis	45793	7	4	\N	\N
8584	Panel Consensus	30	meningitis	45793	7	\N	\N	\N
9125	Andre Kumar	30	meningitis	45793	5	4	CBC	\N
9736	Jonathan Chen	30	meningitis	45793	3	4	CBC	\N
7875	Jason Hom	30	meningitis	45788	10	4	cbc	\N
8458	Panel Average	30	meningitis	45788	7	\N	\N	\N
8585	Lisa Shieh	30	meningitis	45788	7	4	\N	\N
8586	Panel Consensus	30	meningitis	45788	7	\N	\N	\N
9126	Andre Kumar	30	meningitis	45788	5	5	CBC	\N
9737	Jonathan Chen	30	meningitis	45788	3	4	CBC	\N
11337	Jonathan Chen	30	meningitis	45966	3	4	CBC	\N
8399	Andre Kumar	33	meningitis	36210	8	2	Antibiotics	\N
9127	Jason Hom	33	meningitis	36210	5	5	\N	\N
9128	Panel Consensus	33	meningitis	36210	5	\N	\N	\N
9454	Panel Average	33	meningitis	36210	4	\N	\N	\N
9512	Jonathan Chen	33	meningitis	36210	4	5	CNS Cephalosporin	Can replace ceftriaxone, but slightly less points, as is a little unnecessary overkill
10717	Lisa Shieh	33	meningitis	36210	0	3	\N	\N
7876	Andre Kumar	30	meningitis	35733	10	\N	Antibiotics	\N
7877	Jason Hom	30	meningitis	35733	10	5	\N	\N
7878	Jonathan Chen	30	meningitis	35733	10	5	CNS Cephalosporin	\N
7879	Lisa Shieh	30	meningitis	35733	10	5	\N	\N
7880	Panel Average	30	meningitis	35733	10	\N	\N	\N
7881	Panel Consensus	30	meningitis	35733	10	\N	\N	\N
7882	Jason Hom	31	meningitis	35733	10	5	\N	\N
7883	Jonathan Chen	31	meningitis	35733	10	5	CNS Cephalosporin	\N
7884	Panel Consensus	31	meningitis	35733	10	\N	\N	\N
8400	Andre Kumar	31	meningitis	35733	8	3	Antibiotics	No points if already ordered
8442	Panel Average	31	meningitis	35733	8	\N	\N	\N
9129	Lisa Shieh	31	meningitis	35733	5	3	\N	\N
8401	Andre Kumar	33	meningitis	35733	8	2	Antibiotics	less points if delayed
8871	Panel Average	33	meningitis	35733	5	\N	\N	\N
9130	Jason Hom	33	meningitis	35733	5	5	\N	\N
9131	Jonathan Chen	33	meningitis	35733	5	4	CNS Cephalosporin	Good antibiotic, but didn't prescribe until got to the worsened" state, meaning waited over an hour before prescribing. Don't give as many points"
9132	Panel Consensus	33	meningitis	35733	5	\N	\N	\N
9738	Lisa Shieh	33	meningitis	35733	3	3	already did LP_ so no credit for running LP tests- maybe for cocci or other  rarer tests since no improvement	\N
7885	Andre Kumar	30	meningitis	48880	10	5	CSF	max points if before antibiotics, otherwise 8 points
7886	Jason Hom	30	meningitis	48880	10	5	\N	\N
7887	Lisa Shieh	30	meningitis	48880	10	5	\N	\N
7888	Panel Average	30	meningitis	48880	10	\N	\N	\N
7889	Panel Consensus	30	meningitis	48880	10	\N	\N	\N
8745	Jonathan Chen	30	meningitis	48880	6	4	LP	Panel of CSF tests, should get point for each? Adds up to more than value of antibiotics
11233	Jonathan Chen	31	meningitis	48880	6	4	LP	Panel of CSF tests, should get point for each? Adds up to more than value of antibiotics
8746	Andre Kumar	33	meningitis	48880	6	3	CSF	max points if before antibiotics, otherwise 3 points
8747	Jonathan Chen	33	meningitis	48880	6	4	LP	Panel of CSF tests, should get point for each? Adds up to more than value of antibiotics
9133	Jason Hom	33	meningitis	48880	5	5	\N	\N
9134	Panel Consensus	33	meningitis	48880	5	\N	\N	\N
9587	Panel Average	33	meningitis	48880	4	\N	\N	\N
10718	Lisa Shieh	33	meningitis	48880	0	3	\N	\N
11425	Jonathan Chen	30	meningitis	50930	0	2	\N	Wrong order. Synovial fluid not CSF
10719	Andre Kumar	30	meningitis	49079	0	4	STD Testing	\N
10720	Jason Hom	30	meningitis	49079	0	4	\N	\N
10721	Jonathan Chen	30	meningitis	49079	0	2	\N	\N
10722	Lisa Shieh	30	meningitis	49079	0	3	\N	\N
10723	Panel Average	30	meningitis	49079	0	\N	\N	\N
10724	Panel Consensus	30	meningitis	49079	0	\N	\N	\N
10291	Andre Kumar	30	meningitis	48603	1	4	CSF	\N
10292	Panel Average	30	meningitis	48603	1	\N	\N	\N
11373	Jonathan Chen	33	meningitis	48603	0	2	\N	Not relevant to test?
11343	Jonathan Chen	33	meningitis	61973	0	2	\N	Not relevant to test?
10293	Andre Kumar	30	meningitis	61853	1	1	CSF	\N
10294	Panel Average	30	meningitis	61853	1	\N	\N	\N
11362	Jonathan Chen	33	meningitis	48752	0	2	\N	Not relevant to test?
11231	Jonathan Chen	30	meningitis	61826	0	2	\N	Not relevant to test?
9739	Lisa Shieh	33	meningitis	61826	3	3	\N	\N
10235	Panel Average	33	meningitis	61826	1	\N	\N	\N
10295	Andre Kumar	33	meningitis	61826	1	4	3	\N
10725	Jason Hom	33	meningitis	61826	0	4	\N	\N
10726	Jonathan Chen	33	meningitis	61826	0	2	\N	No good indication
10727	Panel Consensus	33	meningitis	61826	0	\N	\N	\N
9135	Jason Hom	31	meningitis	48980	5	5	\N	\N
9136	Lisa Shieh	31	meningitis	48980	5	3	\N	\N
9137	Panel Consensus	31	meningitis	48980	5	\N	\N	\N
9432	Panel Average	31	meningitis	48980	5	\N	\N	\N
9513	Andre Kumar	31	meningitis	48980	4	2	Consult	\N
10728	Jonathan Chen	31	meningitis	48980	0	3	\N	Fine, but don't offer direct points for this?
7890	Jason Hom	33	meningitis	48980	10	5	\N	\N
8848	Panel Average	33	meningitis	48980	6	\N	\N	\N
9138	Lisa Shieh	33	meningitis	48980	5	3	\N	\N
9139	Panel Consensus	33	meningitis	48980	5	\N	\N	\N
10076	Andre Kumar	33	meningitis	48980	2	2	Consult	\N
10729	Jonathan Chen	33	meningitis	48980	0	3	\N	\N
7891	Jason Hom	31	meningitis	49207	10	5	\N	\N
7892	Panel Consensus	31	meningitis	49207	10	\N	\N	\N
8748	Panel Average	31	meningitis	49207	6	\N	\N	\N
9140	Andre Kumar	31	meningitis	49207	5	5	Consult	\N
9740	Lisa Shieh	31	meningitis	49207	3	3	\N	\N
10730	Jonathan Chen	31	meningitis	49207	0	3	\N	\N
10296	Andre Kumar	31	meningitis	50841	1	1	Isolation	\N
10297	Panel Average	31	meningitis	50841	1	\N	\N	\N
11439	Jonathan Chen	31	meningitis	49649	0	2	\N	\N
11328	Jonathan Chen	30	meningitis	49594	0	2	\N	No good indication
10298	Andre Kumar	33	meningitis	49594	1	1	CSF	\N
10398	Panel Average	33	meningitis	49594	0	\N	\N	\N
10731	Jason Hom	33	meningitis	49594	0	4	\N	\N
10732	Jonathan Chen	33	meningitis	49594	0	2	\N	No good indication
10733	Lisa Shieh	33	meningitis	49594	0	3	\N	\N
10734	Panel Consensus	33	meningitis	49594	0	\N	\N	\N
7893	Andre Kumar	30	meningitis	49083	10	5	CSF	max points if before antibiotics, otherwise 8 points
7894	Jason Hom	30	meningitis	49083	10	5	\N	\N
7895	Lisa Shieh	30	meningitis	49083	10	5	\N	\N
7896	Panel Average	30	meningitis	49083	10	\N	\N	\N
7897	Panel Consensus	30	meningitis	49083	10	\N	\N	\N
8749	Jonathan Chen	30	meningitis	49083	6	5	\N	\N
11353	Jonathan Chen	31	meningitis	49083	6	5	\N	\N
8750	Andre Kumar	33	meningitis	49083	6	3	Consult	max points if before antibiotics, otherwise 3 points
8751	Jonathan Chen	33	meningitis	49083	6	5	\N	\N
9141	Jason Hom	33	meningitis	49083	5	5	\N	\N
9142	Panel Consensus	33	meningitis	49083	5	\N	\N	\N
9588	Panel Average	33	meningitis	49083	4	\N	\N	\N
10735	Lisa Shieh	33	meningitis	49083	0	3	\N	\N
11447	Jonathan Chen	30	meningitis	50692	4	4	\N	\N
9741	Jonathan Chen	30	meningitis	45983	3	3	CT Head	Okay to order CT scan, but not okay if delay antibiotics awaiting result
10736	Lisa Shieh	30	meningitis	45983	0	3	\N	\N
11092	Panel Consensus	30	meningitis	45983	-3	\N	\N	\N
11098	Panel Average	30	meningitis	45983	-3	\N	\N	\N
11161	Andre Kumar	30	meningitis	45983	-5	4	Imaging	"No indication delays care"
11162	Jason Hom	30	meningitis	45983	-5	4	\N	\N
11333	Jonathan Chen	31	meningitis	45983	3	3	CT Head	\N
9742	Jonathan Chen	30	meningitis	50241	3	3	CT Head	\N
9743	Lisa Shieh	30	meningitis	50241	3	3	\N	\N
11074	Panel Average	30	meningitis	50241	-3	\N	\N	\N
11093	Panel Consensus	30	meningitis	50241	-3	\N	\N	\N
11163	Andre Kumar	30	meningitis	50241	-5	4	Imaging	"No indication delays care"
11175	Jason Hom	30	meningitis	50241	-6	4	\N	\N
9143	Lisa Shieh	30	meningitis	48871	5	3	\N	\N
10221	Panel Average	30	meningitis	48871	2	\N	\N	\N
10737	Andre Kumar	30	meningitis	48871	0	3	D-dimer	\N
10738	Jason Hom	30	meningitis	48871	0	4	\N	\N
10739	Jonathan Chen	30	meningitis	48871	0	3	\N	\N
10740	Panel Consensus	30	meningitis	48871	0	\N	\N	\N
7898	Andre Kumar	30	meningitis	44017	10	5	Steroids	\N
7899	Lisa Shieh	30	meningitis	44017	10	5	\N	\N
7900	Panel Consensus	30	meningitis	44017	10	\N	\N	\N
8278	Jonathan Chen	30	meningitis	44017	9	4	\N	\N
8325	Panel Average	30	meningitis	44017	8	\N	\N	\N
9144	Jason Hom	30	meningitis	44017	5	4	\N	\N
7901	Panel Consensus	31	meningitis	44017	10	\N	\N	\N
8279	Jonathan Chen	31	meningitis	44017	9	4	\N	\N
9145	Andre Kumar	31	meningitis	44017	5	2	Steroids	5 points if ordered late
9146	Jason Hom	31	meningitis	44017	5	4	\N	\N
9147	Lisa Shieh	31	meningitis	44017	5	3	\N	\N
9148	Panel Average	31	meningitis	44017	5	\N	\N	\N
11262	Jonathan Chen	33	meningitis	44017	9	4	\N	\N
9149	Jason Hom	33	meningitis	35969	5	4	\N	\N
10741	Lisa Shieh	33	meningitis	35969	0	3	\N	\N
10742	Panel Average	33	meningitis	35969	0	\N	\N	\N
11164	Andre Kumar	33	meningitis	35969	-5	5	Sedation	\N
11165	Jonathan Chen	33	meningitis	35969	-5	2	\N	Must be erroneous entry trying to get Dexamethasone
11166	Panel Consensus	33	meningitis	35969	-5	\N	\N	\N
9150	Jason Hom	30	meningitis	46286	5	4	\N	\N
9151	Panel Consensus	30	meningitis	46286	5	\N	\N	\N
9744	Lisa Shieh	30	meningitis	46286	3	3	\N	\N
9745	Panel Average	30	meningitis	46286	3	\N	\N	\N
10299	Andre Kumar	30	meningitis	46286	1	2	Coags	\N
10743	Jonathan Chen	30	meningitis	46286	0	3	\N	\N
9746	Andre Kumar	30	meningitis	45811	3	2	NPO	\N
9747	Lisa Shieh	30	meningitis	45811	3	3	\N	\N
10077	Panel Average	30	meningitis	45811	2	\N	\N	\N
10078	Panel Consensus	30	meningitis	45811	2	\N	\N	\N
10744	Jason Hom	30	meningitis	45811	0	4	\N	\N
10745	Jonathan Chen	30	meningitis	45811	0	3	\N	\N
10746	Andre Kumar	30	meningitis	44626	0	1	Antibiotics	\N
10747	Panel Average	30	meningitis	44626	0	\N	\N	\N
8587	Lisa Shieh	30	meningitis	49054	7	3	\N	\N
8752	Panel Consensus	30	meningitis	49054	6	\N	\N	\N
8849	Panel Average	30	meningitis	49054	6	\N	\N	\N
9152	Andre Kumar	30	meningitis	49054	5	3	Isolation	\N
9153	Jason Hom	30	meningitis	49054	5	4	\N	\N
10300	Jonathan Chen	30	meningitis	49054	1	2	\N	\N
8753	Panel Consensus	31	meningitis	49054	6	\N	\N	\N
9154	Lisa Shieh	31	meningitis	49054	5	3	\N	\N
9514	Andre Kumar	31	meningitis	49054	4	2	Isolation	\N
9748	Panel Average	31	meningitis	49054	3	\N	\N	\N
10301	Jonathan Chen	31	meningitis	49054	1	2	\N	\N
10748	Jason Hom	31	meningitis	49054	0	4	\N	\N
10302	Andre Kumar	30	meningitis	61843	1	1	CSF	\N
10303	Panel Average	30	meningitis	61843	1	\N	\N	\N
9749	Lisa Shieh	30	meningitis	45866	3	3	\N	\N
10079	Jason Hom	30	meningitis	45866	2	4	\N	\N
10222	Panel Average	30	meningitis	45866	2	\N	\N	\N
10749	Andre Kumar	30	meningitis	45866	0	1	ECG + Monitoring	\N
10750	Jonathan Chen	30	meningitis	45866	0	3	\N	\N
10751	Panel Consensus	30	meningitis	45866	0	\N	\N	\N
9750	Lisa Shieh	31	meningitis	45866	3	3	\N	\N
10080	Jason Hom	31	meningitis	45866	2	4	\N	\N
10223	Panel Average	31	meningitis	45866	2	\N	\N	\N
10752	Andre Kumar	31	meningitis	45866	0	2	ECG + Monitoring	\N
10753	Jonathan Chen	31	meningitis	45866	0	3	\N	\N
10754	Panel Consensus	31	meningitis	45866	0	\N	\N	\N
10304	Andre Kumar	30	meningitis	46160	1	3	Nursing	\N
10305	Panel Average	30	meningitis	46160	1	\N	\N	\N
11232	Jonathan Chen	33	meningitis	63761	1	3	\N	Common meningitis cause, okay to review
10306	Andre Kumar	30	meningitis	49142	1	1	CSF	\N
10307	Panel Average	30	meningitis	49142	1	\N	\N	\N
11344	Jonathan Chen	33	meningitis	49142	1	3	\N	Common meningitis cause, okay to review
9155	Andre Kumar	30	meningitis	46103	5	4	CSF	\N
9751	Lisa Shieh	30	meningitis	46103	3	3	\N	\N
9920	Panel Average	30	meningitis	46103	3	\N	\N	\N
10755	Jason Hom	30	meningitis	46103	0	4	\N	\N
10756	Jonathan Chen	30	meningitis	46103	0	3	\N	\N
10757	Panel Consensus	30	meningitis	46103	0	\N	\N	\N
10308	Andre Kumar	31	meningitis	46103	1	5	CSF	\N
10309	Panel Average	31	meningitis	46103	1	\N	\N	\N
11275	Jonathan Chen	30	meningitis	50685	0	2	\N	Mostly irrelevant STD testing?
11379	Jonathan Chen	30	meningitis	44252	2	4	\N	Doesn't penetrate CNS
9156	Lisa Shieh	30	meningitis	44237	5	3	\N	\N
10081	Jonathan Chen	30	meningitis	44237	2	4	\N	Doesn't penetrate CNS
11105	Panel Average	30	meningitis	44237	-4	\N	\N	\N
11198	Andre Kumar	30	meningitis	44237	-8	5	Antibiotics	Doesn't cross CSF
11199	Panel Consensus	30	meningitis	44237	-8	\N	\N	\N
7902	Andre Kumar	30	meningitis	48577	10	5	CSF	max points if before antibiotics, otherwise 8 points
7903	Jason Hom	30	meningitis	48577	10	5	\N	\N
7904	Panel Consensus	30	meningitis	48577	10	\N	\N	\N
8280	Panel Average	30	meningitis	48577	9	\N	\N	\N
8588	Lisa Shieh	30	meningitis	48577	7	3	\N	\N
9515	Jonathan Chen	30	meningitis	48577	4	5	\N	\N
11325	Jonathan Chen	31	meningitis	48577	4	5	\N	\N
7905	Panel Consensus	33	meningitis	48577	10	\N	\N	\N
8754	Andre Kumar	33	meningitis	48577	6	3	CSF	max points if before antibiotics, otherwise 3 points
9157	Jason Hom	33	meningitis	48577	5	5	\N	\N
9516	Jonathan Chen	33	meningitis	48577	4	5	\N	\N
9589	Panel Average	33	meningitis	48577	4	\N	\N	\N
10758	Lisa Shieh	33	meningitis	48577	0	3	\N	\N
7906	Andre Kumar	30	meningitis	46006	10	5	CSF	\N
7907	Jason Hom	30	meningitis	46006	10	5	\N	\N
7908	Lisa Shieh	30	meningitis	46006	10	10	\N	\N
7909	Panel Average	30	meningitis	46006	10	\N	\N	\N
7910	Panel Consensus	30	meningitis	46006	10	\N	\N	\N
9517	Jonathan Chen	30	meningitis	46006	4	4	\N	\N
11348	Jonathan Chen	33	meningitis	46006	4	4	\N	\N
11278	Jonathan Chen	30	meningitis	42197	0	5	\N	\N
7911	Jason Hom	30	meningitis	49109	10	5	\N	\N
8281	Andre Kumar	30	meningitis	49109	9	5	CSF	\N
8459	Panel Average	30	meningitis	49109	7	\N	\N	\N
8589	Panel Consensus	30	meningitis	49109	7	\N	\N	\N
9752	Jonathan Chen	30	meningitis	49109	3	2	HSV CSF	\N
9753	Lisa Shieh	30	meningitis	49109	3	3	\N	\N
11301	Jonathan Chen	33	meningitis	49109	3	2	HSV CSF	\N
10310	Andre Kumar	30	meningitis	50425	1	1	CSF	\N
10311	Panel Average	30	meningitis	50425	1	\N	\N	\N
11385	Jonathan Chen	30	meningitis	62011	0	2	\N	Not the right screening test for HIV
7912	Jason Hom	30	meningitis	63767	10	5	\N	\N
8282	Andre Kumar	30	meningitis	63767	9	4	CSF	\N
8402	Panel Average	30	meningitis	63767	8	\N	\N	\N
8590	Panel Consensus	30	meningitis	63767	7	\N	\N	\N
9158	Lisa Shieh	30	meningitis	63767	5	3	\N	\N
9754	Jonathan Chen	30	meningitis	63767	3	2	HSV CSF	\N
8591	Panel Consensus	31	meningitis	63767	7	\N	\N	\N
9159	Jason Hom	31	meningitis	63767	5	5	\N	\N
9755	Jonathan Chen	31	meningitis	63767	3	2	HSV CSF	\N
9756	Lisa Shieh	31	meningitis	63767	3	3	\N	\N
9757	Panel Average	31	meningitis	63767	3	\N	\N	\N
10312	Andre Kumar	31	meningitis	63767	1	3	CSF	\N
8592	Panel Consensus	33	meningitis	63767	7	\N	\N	\N
9160	Jason Hom	33	meningitis	63767	5	5	\N	\N
9608	Panel Average	33	meningitis	63767	3	\N	\N	\N
9758	Jonathan Chen	33	meningitis	63767	3	2	HSV CSF	\N
9759	Lisa Shieh	33	meningitis	63767	3	3	\N	\N
10082	Andre Kumar	33	meningitis	63767	2	4	4	\N
9161	Andre Kumar	30	meningitis	44230	5	1	Steroids	Dexamethasone, not hydrocort recommended?
9162	Panel Average	30	meningitis	44230	5	\N	\N	\N
9760	Lisa Shieh	30	meningitis	44319	3	3	\N	\N
10083	Jason Hom	30	meningitis	44319	2	4	\N	\N
10084	Panel Consensus	30	meningitis	44319	2	\N	\N	\N
10224	Panel Average	30	meningitis	44319	2	\N	\N	\N
10313	Jonathan Chen	30	meningitis	44319	1	3	Pain Control	\N
10759	Andre Kumar	30	meningitis	44319	0	1	Pain Medication	\N
11272	Jonathan Chen	30	meningitis	48732	0	2	\N	Blood gases?
7913	Jason Hom	30	meningitis	48954	10	5	\N	\N
7914	Lisa Shieh	30	meningitis	48954	10	5	\N	\N
7915	Panel Consensus	30	meningitis	48954	10	\N	\N	\N
8593	Panel Average	30	meningitis	48954	7	\N	\N	\N
10314	Andre Kumar	30	meningitis	48954	1	1	Nursing	\N
10760	Jonathan Chen	30	meningitis	48954	0	3	\N	\N
9163	Andre Kumar	30	meningitis	62151	5	5	Lactate	\N
9164	Jason Hom	30	meningitis	62151	5	4	\N	\N
9165	Jonathan Chen	30	meningitis	62151	5	3	Lactate	\N
9166	Lisa Shieh	30	meningitis	62151	5	3	\N	\N
9167	Panel Average	30	meningitis	62151	5	\N	\N	\N
9168	Panel Consensus	30	meningitis	62151	5	\N	\N	\N
9169	Jonathan Chen	31	meningitis	62151	5	3	Lactate	\N
9170	Panel Consensus	31	meningitis	62151	5	\N	\N	\N
9761	Lisa Shieh	31	meningitis	62151	3	3	\N	\N
10085	Andre Kumar	31	meningitis	62151	2	2	Lactate	\N
10225	Panel Average	31	meningitis	62151	2	\N	\N	\N
10761	Jason Hom	31	meningitis	62151	0	4	\N	\N
11412	Jonathan Chen	33	meningitis	62151	5	3	Lactate	\N
9171	Andre Kumar	30	meningitis	45918	5	5	Lactate	\N
9172	Jason Hom	30	meningitis	45918	5	4	\N	\N
9173	Jonathan Chen	30	meningitis	45918	5	3	Lactate	\N
9174	Panel Consensus	30	meningitis	45918	5	\N	\N	\N
9455	Panel Average	30	meningitis	45918	4	\N	\N	\N
9762	Lisa Shieh	30	meningitis	45918	3	3	\N	\N
10086	Andre Kumar	31	meningitis	45918	2	2	Lactate	\N
10087	Panel Average	31	meningitis	45918	2	\N	\N	\N
8403	Jason Hom	33	meningitis	45918	8	4	\N	\N
9175	Jonathan Chen	33	meningitis	45918	5	3	Lactate	\N
9176	Panel Consensus	33	meningitis	45918	5	\N	\N	\N
9433	Panel Average	33	meningitis	45918	5	\N	\N	\N
9763	Andre Kumar	33	meningitis	45918	3	4	Lactate	\N
9764	Lisa Shieh	33	meningitis	45918	3	3	\N	\N
11421	Jonathan Chen	30	meningitis	50510	2	3	\N	Reasonable, though not standard guidelines to check
9177	Andre Kumar	33	meningitis	50510	5	4	CSF	very sensitive marker
9178	Panel Consensus	33	meningitis	50510	5	\N	\N	\N
10088	Jonathan Chen	33	meningitis	50510	2	3	\N	Reasonable, though not standard guidelines to check
10226	Panel Average	33	meningitis	50510	2	\N	\N	\N
10762	Jason Hom	33	meningitis	50510	0	4	\N	\N
10763	Lisa Shieh	33	meningitis	50510	0	3	\N	\N
7916	Andre Kumar	30	meningitis	63811	10	5	Lumbar Puncture	"Max points before antibiotics 5 points if after antibiotics"
7917	Jason Hom	30	meningitis	63811	10	5	\N	\N
7918	Lisa Shieh	30	meningitis	63811	10	5	\N	\N
7919	Panel Average	30	meningitis	63811	10	\N	\N	\N
7920	Panel Consensus	30	meningitis	63811	10	\N	\N	\N
8755	Jonathan Chen	30	meningitis	63811	6	2	LP	Group with CSF Cell count as implicit that going to do LP if order that
7921	Jason Hom	31	meningitis	63811	10	5	\N	\N
8756	Jonathan Chen	31	meningitis	63811	6	2	LP	Group with CSF Cell count as implicit that going to do LP if order that
9179	Panel Consensus	31	meningitis	63811	5	\N	\N	\N
9596	Panel Average	31	meningitis	63811	4	\N	\N	\N
11094	Andre Kumar	31	meningitis	63811	-3	0	Lumbar Puncture	Why repeat LP? Is it they improved with ABX without LP and now are getting procedure? If so, I would say minus points for delay in care
8404	Andre Kumar	33	meningitis	63811	8	5	5	less points if delayed
8757	Jonathan Chen	33	meningitis	63811	6	2	LP	Group with CSF Cell count as implicit that going to do LP if order that
9180	Jason Hom	33	meningitis	63811	5	5	\N	\N
9181	Panel Consensus	33	meningitis	63811	5	\N	\N	\N
9456	Panel Average	33	meningitis	63811	4	\N	\N	\N
10764	Lisa Shieh	33	meningitis	63811	0	3	\N	\N
7922	Andre Kumar	30	meningitis	62167	10	5	Lumbar Puncture	"Max points before antibiotics 5 points if after antibiotics"
7923	Jason Hom	30	meningitis	62167	10	5	\N	\N
7924	Lisa Shieh	30	meningitis	62167	10	5	\N	\N
7925	Panel Average	30	meningitis	62167	10	\N	\N	\N
7926	Panel Consensus	30	meningitis	62167	10	\N	\N	\N
8758	Jonathan Chen	30	meningitis	62167	6	2	LP	Group with CSF Cell count as implicit that going to do LP if order that
8405	Andre Kumar	33	meningitis	62167	8	5	5	less points if delayed
8759	Jonathan Chen	33	meningitis	62167	6	2	LP	Group with CSF Cell count as implicit that going to do LP if order that
9182	Jason Hom	33	meningitis	62167	5	5	\N	\N
9183	Panel Consensus	33	meningitis	62167	5	\N	\N	\N
9457	Panel Average	33	meningitis	62167	4	\N	\N	\N
10765	Lisa Shieh	33	meningitis	62167	0	3	\N	\N
9184	Jason Hom	30	meningitis	45763	5	4	\N	\N
9185	Lisa Shieh	30	meningitis	45763	5	4	\N	\N
9186	Panel Consensus	30	meningitis	45763	5	\N	\N	\N
9458	Panel Average	30	meningitis	45763	4	\N	\N	\N
9765	Andre Kumar	30	meningitis	45763	3	4	Metabolic panel	\N
10089	Jonathan Chen	30	meningitis	45763	2	3	Metabolic Panel	\N
8594	Lisa Shieh	30	meningitis	45771	7	4	\N	\N
9187	Jason Hom	30	meningitis	45771	5	4	\N	\N
9188	Panel Average	30	meningitis	45771	5	\N	\N	\N
9189	Panel Consensus	30	meningitis	45771	5	\N	\N	\N
9766	Andre Kumar	30	meningitis	45771	3	4	Metabolic panel	\N
10090	Jonathan Chen	30	meningitis	45771	2	3	Metabolic Panel	\N
8406	Andre Kumar	30	meningitis	44586	8	1	Steroids	Only dexamethasone recommended?
8407	Panel Average	30	meningitis	44586	8	\N	\N	\N
11334	Jonathan Chen	31	meningitis	44199	0	2	\N	Symptomatic management
10315	Andre Kumar	31	meningitis	44641	1	1	Pain Medication	\N
10316	Panel Average	31	meningitis	44641	1	\N	\N	\N
10091	Andre Kumar	31	meningitis	46065	2	1	Imaging	\N
10092	Panel Average	31	meningitis	46065	2	\N	\N	\N
11307	Jonathan Chen	30	meningitis	45792	0	2	\N	\N
10317	Andre Kumar	31	meningitis	45792	1	4	MRSA	\N
10399	Panel Average	31	meningitis	45792	0	\N	\N	\N
10766	Jason Hom	31	meningitis	45792	0	4	\N	\N
10767	Jonathan Chen	31	meningitis	45792	0	2	\N	\N
10768	Lisa Shieh	31	meningitis	45792	0	3	\N	\N
10769	Panel Consensus	31	meningitis	45792	0	\N	\N	\N
10318	Andre Kumar	30	meningitis	61852	1	1	CSF	\N
10400	Panel Average	30	meningitis	61852	0	\N	\N	\N
10770	Jason Hom	30	meningitis	61852	0	4	\N	\N
10771	Jonathan Chen	30	meningitis	61852	0	2	\N	No good indication
10772	Lisa Shieh	30	meningitis	61852	0	3	\N	\N
10773	Panel Consensus	30	meningitis	61852	0	\N	\N	\N
10319	Andre Kumar	30	meningitis	45750	1	5	Nursing	\N
10320	Panel Average	30	meningitis	45750	1	\N	\N	\N
10774	Andre Kumar	30	meningitis	44216	0	1	Nausea Medication	\N
10775	Panel Average	30	meningitis	44216	0	\N	\N	\N
11250	Jonathan Chen	30	meningitis	61823	0	4	\N	\N
10321	Andre Kumar	30	meningitis	45802	1	4	Nursing	\N
10322	Panel Average	30	meningitis	45802	1	\N	\N	\N
11253	Jonathan Chen	31	meningitis	49334	0	2	\N	Irrelevant?
11476	Jonathan Chen	30	meningitis	46090	0	2	\N	\N
9190	Jason Hom	30	meningitis	45955	5	4	\N	\N
9191	Jonathan Chen	30	meningitis	45955	5	3	Lactate	\N
9192	Panel Consensus	30	meningitis	45955	5	\N	\N	\N
10093	Panel Average	30	meningitis	45955	2	\N	\N	\N
10323	Andre Kumar	30	meningitis	45955	1	1	Blood Gas	\N
10776	Lisa Shieh	30	meningitis	45955	0	3	\N	\N
9193	Andre Kumar	30	meningitis	48561	5	5	Upreg	\N
9194	Panel Average	30	meningitis	48561	5	\N	\N	\N
11277	Jonathan Chen	30	meningitis	45798	1	3	Pregnancy Test	\N
9195	Panel Consensus	33	meningitis	49134	5	\N	\N	\N
10324	Andre Kumar	33	meningitis	49134	1	1	UPreg	\N
10325	Jonathan Chen	33	meningitis	49134	1	3	Pregnancy Test	\N
10401	Panel Average	33	meningitis	49134	0	\N	\N	\N
10777	Jason Hom	33	meningitis	49134	0	4	\N	\N
10778	Lisa Shieh	33	meningitis	49134	0	3	\N	\N
9767	Lisa Shieh	30	meningitis	62042	3	3	\N	\N
9939	Panel Average	30	meningitis	62042	2	\N	\N	\N
10094	Andre Kumar	30	meningitis	62042	2	2	Procalcitonin	\N
10095	Jason Hom	30	meningitis	62042	2	4	\N	\N
10096	Panel Consensus	30	meningitis	62042	2	\N	\N	\N
10326	Jonathan Chen	30	meningitis	62042	1	2	\N	\N
7927	Andre Kumar	30	meningitis	49020	10	5	CSF	max points if before antibiotics, otherwise 8 points
7928	Jason Hom	30	meningitis	49020	10	5	\N	\N
7929	Panel Consensus	30	meningitis	49020	10	\N	\N	\N
8283	Panel Average	30	meningitis	49020	9	\N	\N	\N
8595	Lisa Shieh	30	meningitis	49020	7	3	\N	\N
9518	Jonathan Chen	30	meningitis	49020	4	4	\N	\N
11435	Jonathan Chen	31	meningitis	49020	4	4	\N	\N
8760	Andre Kumar	33	meningitis	49020	6	3	CSF	max points if before antibiotics, otherwise 3 points
9196	Jason Hom	33	meningitis	49020	5	5	\N	\N
9197	Panel Consensus	33	meningitis	49020	5	\N	\N	\N
9519	Jonathan Chen	33	meningitis	49020	4	4	\N	\N
9590	Panel Average	33	meningitis	49020	4	\N	\N	\N
10779	Lisa Shieh	33	meningitis	49020	0	3	\N	\N
8596	Lisa Shieh	30	meningitis	45759	7	4	\N	\N
8761	Panel Consensus	30	meningitis	45759	6	\N	\N	\N
8850	Panel Average	30	meningitis	45759	6	\N	\N	\N
9198	Andre Kumar	30	meningitis	45759	5	5	Coags	\N
9199	Jason Hom	30	meningitis	45759	5	5	\N	\N
10780	Jonathan Chen	30	meningitis	45759	0	3	\N	\N
11347	Jonathan Chen	31	meningitis	45776	0	4	\N	Process
8597	Lisa Shieh	30	meningitis	45770	7	4	\N	\N
8762	Panel Consensus	30	meningitis	45770	6	\N	\N	\N
8851	Panel Average	30	meningitis	45770	6	\N	\N	\N
9200	Andre Kumar	30	meningitis	45770	5	4	Coags	\N
9201	Jason Hom	30	meningitis	45770	5	5	\N	\N
10781	Jonathan Chen	30	meningitis	45770	0	3	\N	\N
8408	Jason Hom	30	meningitis	62103	8	5	\N	\N
9202	Panel Consensus	30	meningitis	62103	5	\N	\N	\N
9520	Andre Kumar	30	meningitis	62103	4	1	STD Testing	\N
9521	Panel Average	30	meningitis	62103	4	\N	\N	\N
10097	Jonathan Chen	30	meningitis	62103	2	2	HIV	\N
10782	Lisa Shieh	30	meningitis	62103	0	3	\N	\N
11460	Jonathan Chen	31	meningitis	62103	2	2	HIV	\N
9203	Lisa Shieh	33	meningitis	62103	5	3	\N	\N
9204	Panel Consensus	33	meningitis	62103	5	\N	\N	\N
9522	Jason Hom	33	meningitis	62103	4	5	\N	\N
9609	Panel Average	33	meningitis	62103	3	\N	\N	\N
10098	Jonathan Chen	33	meningitis	62103	2	2	HIV	\N
10327	Andre Kumar	33	meningitis	62103	1	3	7	\N
11367	Jonathan Chen	30	meningitis	48728	0	2	\N	\N
11428	Jonathan Chen	31	meningitis	48728	0	2	\N	\N
9205	Jason Hom	30	meningitis	63923	5	4	\N	\N
9768	Andre Kumar	30	meningitis	63923	3	2	Respiratory Panel	\N
9769	Panel Consensus	30	meningitis	63923	3	\N	\N	\N
9921	Panel Average	30	meningitis	63923	3	\N	\N	\N
10783	Jonathan Chen	30	meningitis	63923	0	2	\N	\N
10784	Lisa Shieh	30	meningitis	63923	0	3	\N	\N
8598	Lisa Shieh	30	meningitis	48586	7	3	\N	\N
9206	Jason Hom	30	meningitis	48586	5	4	\N	\N
9207	Panel Average	30	meningitis	48586	5	\N	\N	\N
9208	Panel Consensus	30	meningitis	48586	5	\N	\N	\N
9770	Andre Kumar	30	meningitis	48586	3	4	CSF	\N
10785	Jonathan Chen	30	meningitis	48586	0	3	\N	\N
9209	Andre Kumar	30	meningitis	63725	5	5	Lactate	\N
9210	Jason Hom	30	meningitis	63725	5	4	\N	\N
9211	Jonathan Chen	30	meningitis	63725	5	3	Lactate	\N
9212	Lisa Shieh	30	meningitis	63725	5	3	\N	\N
9213	Panel Average	30	meningitis	63725	5	\N	\N	\N
9214	Panel Consensus	30	meningitis	63725	5	\N	\N	\N
11258	Jonathan Chen	31	meningitis	63725	5	3	Lactate	\N
8599	Lisa Shieh	30	meningitis	44198	7	3	\N	\N
9215	Jonathan Chen	30	meningitis	44198	5	3	IVF	\N
9216	Panel Consensus	30	meningitis	44198	5	\N	\N	\N
9459	Panel Average	30	meningitis	44198	4	\N	\N	\N
9771	Andre Kumar	30	meningitis	44198	3	5	Fluids	\N
9772	Jason Hom	30	meningitis	44198	3	4	\N	\N
9523	Andre Kumar	31	meningitis	44198	4	3	Fluids	\N
9524	Panel Average	31	meningitis	44198	4	\N	\N	\N
8763	Jason Hom	33	meningitis	44198	6	4	\N	\N
8872	Panel Average	33	meningitis	44198	5	\N	\N	\N
9217	Andre Kumar	33	meningitis	44198	5	2	Fluids	\N
9218	Jonathan Chen	33	meningitis	44198	5	3	IVF	\N
9219	Lisa Shieh	33	meningitis	44198	5	3	\N	\N
9220	Panel Consensus	33	meningitis	44198	5	\N	\N	\N
10099	Andre Kumar	30	meningitis	46131	2	4	STD Testing	\N
10387	Panel Average	30	meningitis	46131	1	\N	\N	\N
10786	Jason Hom	30	meningitis	46131	0	4	\N	\N
10787	Jonathan Chen	30	meningitis	46131	0	2	\N	Symptoms don't suggest neurosyphillis?
10788	Lisa Shieh	30	meningitis	46131	0	3	\N	\N
10789	Panel Consensus	30	meningitis	46131	0	\N	\N	\N
10100	Andre Kumar	30	meningitis	45751	2	5	Urinalysis	\N
10101	Jason Hom	30	meningitis	45751	2	4	\N	\N
10102	Jonathan Chen	30	meningitis	45751	2	3	UA	General workup for fever/infection, though symptoms not suggestive of UTI
10236	Panel Average	30	meningitis	45751	1	\N	\N	\N
10790	Lisa Shieh	30	meningitis	45751	0	3	\N	\N
10791	Panel Consensus	30	meningitis	45751	0	\N	\N	\N
10103	Jonathan Chen	33	meningitis	45751	2	3	UA	General workup for fever/infection, though symptoms not suggestive of UTI
10328	Andre Kumar	33	meningitis	45751	1	4	Urinalysis	\N
10402	Panel Average	33	meningitis	45751	0	\N	\N	\N
10792	Jason Hom	33	meningitis	45751	0	4	\N	\N
10793	Lisa Shieh	33	meningitis	45751	0	3	\N	\N
10794	Panel Consensus	33	meningitis	45751	0	\N	\N	\N
9221	Jason Hom	30	meningitis	45873	5	4	\N	\N
9940	Panel Average	30	meningitis	45873	2	\N	\N	\N
10104	Andre Kumar	30	meningitis	45873	2	3	Urinalysis	\N
10105	Jonathan Chen	30	meningitis	45873	2	3	UA	General workup for fever/infection, though symptoms not suggestive of UTI
10795	Lisa Shieh	30	meningitis	45873	0	3	\N	\N
10796	Panel Consensus	30	meningitis	45873	0	\N	\N	\N
9222	Jason Hom	31	meningitis	45873	5	4	\N	\N
10106	Jonathan Chen	31	meningitis	45873	2	3	UA	General workup for fever/infection, though symptoms not suggestive of UTI
10227	Panel Average	31	meningitis	45873	2	\N	\N	\N
10797	Andre Kumar	31	meningitis	45873	0	5	Urinalysis	\N
10798	Lisa Shieh	31	meningitis	45873	0	3	\N	\N
10799	Panel Consensus	31	meningitis	45873	0	\N	\N	\N
10329	Andre Kumar	30	meningitis	45782	1	4	Urine Culture	\N
10330	Panel Average	30	meningitis	45782	1	\N	\N	\N
7930	Andre Kumar	30	meningitis	43997	10	5	Antibiotics	\N
7931	Jason Hom	30	meningitis	43997	10	5	\N	\N
7932	Lisa Shieh	30	meningitis	43997	10	5	\N	\N
7933	Panel Average	30	meningitis	43997	10	\N	\N	\N
7934	Panel Consensus	30	meningitis	43997	10	\N	\N	\N
8284	Jonathan Chen	30	meningitis	43997	9	5	\N	\N
7935	Jason Hom	31	meningitis	43997	10	5	\N	\N
7936	Panel Consensus	31	meningitis	43997	10	\N	\N	\N
8285	Jonathan Chen	31	meningitis	43997	9	5	\N	\N
8409	Andre Kumar	31	meningitis	43997	8	3	Antibiotics	No points if already ordered
8443	Panel Average	31	meningitis	43997	8	\N	\N	\N
9223	Lisa Shieh	31	meningitis	43997	5	3	\N	\N
8410	Andre Kumar	33	meningitis	43997	8	2	Antibiotics	\N
8873	Panel Average	33	meningitis	43997	5	\N	\N	\N
9224	Jason Hom	33	meningitis	43997	5	5	\N	\N
9225	Jonathan Chen	33	meningitis	43997	5	4	\N	Good antibiotic, but didn't prescribe until got to the worsened" state, meaning waited over an hour before prescribing. Don't give as many points"
9226	Panel Consensus	33	meningitis	43997	5	\N	\N	\N
9773	Lisa Shieh	33	meningitis	43997	3	3	\N	\N
11242	Jonathan Chen	33	meningitis	48486	2	3	Vancomycin Level	Okay to check followup leels
11434	Jonathan Chen	30	meningitis	45972	2	3	Vancomycin Level	Okay to check followup leels
11376	Jonathan Chen	33	meningitis	45972	2	3	Vancomycin Level	Okay to check followup leels
7937	Andre Kumar	30	meningitis	48519	10	5	CSF	\N
7938	Panel Average	30	meningitis	48519	10	\N	\N	\N
11390	Jonathan Chen	33	meningitis	48519	0	2	\N	\N
11327	Jonathan Chen	33	meningitis	48529	0	2	\N	\N
11338	Jonathan Chen	30	meningitis	63735	0	2	\N	\N
11265	Jonathan Chen	30	meningitis	45766	0	2	\N	\N
9227	Jason Hom	30	meningitis	50654	5	4	\N	\N
9774	Lisa Shieh	30	meningitis	50654	3	3	\N	\N
9775	Panel Average	30	meningitis	50654	3	\N	\N	\N
10331	Andre Kumar	30	meningitis	50654	1	1	CSF	\N
10800	Jonathan Chen	30	meningitis	50654	0	2	\N	No good indication
10801	Panel Consensus	30	meningitis	50654	0	\N	\N	\N
9228	Jason Hom	33	meningitis	50654	5	4	\N	\N
9776	Lisa Shieh	33	meningitis	50654	3	3	?does not change management	\N
9777	Panel Average	33	meningitis	50654	3	\N	\N	\N
10332	Andre Kumar	33	meningitis	50654	1	4	3	\N
10802	Jonathan Chen	33	meningitis	50654	0	2	\N	No good indication
10803	Panel Consensus	33	meningitis	50654	0	\N	\N	\N
9229	Jason Hom	30	meningitis	45818	5	4	\N	\N
9778	Lisa Shieh	30	meningitis	45818	3	3	\N	\N
9779	Panel Consensus	30	meningitis	45818	3	\N	\N	\N
10107	Jonathan Chen	30	meningitis	45818	2	3	CXR	General workup for fever/infection, though symptoms not suggestive of pneumonia
10108	Panel Average	30	meningitis	45818	2	\N	\N	\N
11064	Andre Kumar	30	meningitis	45818	-2	3	Imaging	\N
9230	Jason Hom	31	meningitis	45818	5	4	\N	\N
9610	Panel Average	31	meningitis	45818	3	\N	\N	\N
9780	Lisa Shieh	31	meningitis	45818	3	3	\N	\N
9781	Panel Consensus	31	meningitis	45818	3	\N	\N	\N
10109	Andre Kumar	31	meningitis	45818	2	1	Imaging	?Check for pneumonoccocal pneumonia
10110	Jonathan Chen	31	meningitis	45818	2	3	CXR	General workup for fever/infection, though symptoms not suggestive of pneumonia
9782	Lisa Shieh	33	meningitis	45818	3	3	\N	\N
9783	Panel Consensus	33	meningitis	45818	3	\N	\N	\N
10111	Jonathan Chen	33	meningitis	45818	2	3	CXR	General workup for fever/infection, though symptoms not suggestive of pneumonia
10403	Panel Average	33	meningitis	45818	0	\N	\N	\N
10804	Jason Hom	33	meningitis	45818	0	4	\N	\N
11065	Andre Kumar	33	meningitis	45818	-2	4	Imaging	\N
9231	Jason Hom	30	meningitis	45801	5	4	\N	\N
9784	Lisa Shieh	30	meningitis	45801	3	3	\N	\N
10112	Jonathan Chen	30	meningitis	45801	2	3	CXR	General workup for fever/infection, though symptoms not suggestive of pneumonia
10113	Panel Average	30	meningitis	45801	2	\N	\N	\N
11066	Andre Kumar	30	meningitis	45801	-2	3	Imaging	\N
11345	Jonathan Chen	5000	neutropenic	56492	1	2	\N	\N
9232	Jason Hom	5002	neutropenic	44281	5	4	\N	\N
9233	Lisa Shieh	5002	neutropenic	44281	5	3	\N	\N
9525	Panel Average	5002	neutropenic	44281	4	\N	\N	\N
9526	Panel Consensus	5002	neutropenic	44281	4	\N	\N	\N
10114	Andre Kumar	5002	neutropenic	44281	2	3	Fever Medication	\N
10333	Jonathan Chen	5002	neutropenic	44281	1	2	\N	\N
11401	Jonathan Chen	5003	neutropenic	44281	1	2	\N	\N
9234	Jason Hom	5000	neutropenic	44281	5	4	\N	\N
9527	Panel Consensus	5000	neutropenic	44281	4	\N	\N	\N
9591	Panel Average	5000	neutropenic	44281	4	\N	\N	\N
9785	Andre Kumar	5000	neutropenic	44281	3	3	Fever Medication	\N
9786	Lisa Shieh	5000	neutropenic	44281	3	3	\N	\N
10334	Jonathan Chen	5000	neutropenic	44281	1	2	\N	\N
9235	Lisa Shieh	5000	neutropenic	48829	5	3	\N	\N
10237	Panel Average	5000	neutropenic	48829	1	\N	\N	\N
10805	Andre Kumar	5000	neutropenic	48829	0	5	\N	\N
10806	Jonathan Chen	5000	neutropenic	48829	0	2	\N	\N
10983	Jason Hom	5000	neutropenic	48829	-1	4	\N	\N
10984	Panel Consensus	5000	neutropenic	48829	-1	\N	\N	\N
11329	Jonathan Chen	5002	neutropenic	65641	0	4	\N	Process
9236	Andre Kumar	5002	neutropenic	45814	5	2	Admit	Assuming MASCC score is <21
9237	Panel Average	5002	neutropenic	45814	5	\N	\N	\N
7939	Jason Hom	5000	neutropenic	48775	10	4	\N	\N
9238	Lisa Shieh	5000	neutropenic	48775	5	3	after post void	\N
9239	Panel Average	5000	neutropenic	48775	5	\N	\N	\N
10807	Andre Kumar	5000	neutropenic	48775	0	1	\N	\N
10808	Jonathan Chen	5000	neutropenic	48775	0	2	\N	\N
10809	Panel Consensus	5000	neutropenic	48775	0	\N	\N	\N
7940	Jason Hom	5002	neutropenic	46157	10	5	\N	\N
7941	Panel Consensus	5002	neutropenic	46157	10	\N	\N	\N
8600	Jonathan Chen	5002	neutropenic	46157	7	4	Blood Cultures	\N
8685	Panel Average	5002	neutropenic	46157	6	\N	\N	\N
8764	Andre Kumar	5002	neutropenic	46157	6	5	Time to Positivity	More points for time to positivity cultures
9787	Lisa Shieh	5002	neutropenic	46157	3	3	\N	\N
7942	Jason Hom	5002	neutropenic	46291	10	5	\N	\N
7943	Lisa Shieh	5002	neutropenic	46291	10	3	\N	\N
7944	Panel Consensus	5002	neutropenic	46291	10	\N	\N	\N
8296	Panel Average	5002	neutropenic	46291	9	\N	\N	\N
8601	Jonathan Chen	5002	neutropenic	46291	7	4	Blood Cultures	\N
8765	Andre Kumar	5002	neutropenic	46291	6	5	Time to Positivity	\N
7945	Jason Hom	5002	neutropenic	45901	10	5	\N	\N
7946	Lisa Shieh	5002	neutropenic	45901	10	5	\N	\N
7947	Panel Consensus	5002	neutropenic	45901	10	\N	\N	\N
8326	Panel Average	5002	neutropenic	45901	8	\N	\N	\N
8602	Jonathan Chen	5002	neutropenic	45901	7	4	Blood Cultures	\N
9240	Andre Kumar	5002	neutropenic	45901	5	5	Blood cultures	\N
11438	Jonathan Chen	5003	neutropenic	45901	7	4	Blood Cultures	\N
7948	Jason Hom	5000	neutropenic	45901	10	4	\N	\N
7949	Lisa Shieh	5000	neutropenic	45901	10	3	\N	\N
7950	Panel Consensus	5000	neutropenic	45901	10	\N	\N	\N
8297	Panel Average	5000	neutropenic	45901	9	\N	\N	\N
8603	Jonathan Chen	5000	neutropenic	45901	7	4	Blood Cultures	\N
8766	Andre Kumar	5000	neutropenic	45901	6	5	Blood Cultures	\N
7951	Jason Hom	5002	neutropenic	45752	10	5	\N	\N
7952	Lisa Shieh	5002	neutropenic	45752	10	5	\N	\N
7953	Panel Consensus	5002	neutropenic	45752	10	\N	\N	\N
8327	Panel Average	5002	neutropenic	45752	8	\N	\N	\N
8604	Jonathan Chen	5002	neutropenic	45752	7	4	Blood Cultures	\N
9241	Andre Kumar	5002	neutropenic	45752	5	5	Blood Cultures	\N
11245	Jonathan Chen	5003	neutropenic	45752	7	4	Blood Cultures	\N
7954	Jason Hom	5000	neutropenic	45752	10	5	\N	\N
7955	Lisa Shieh	5000	neutropenic	45752	10	5	\N	\N
7956	Panel Consensus	5000	neutropenic	45752	10	\N	\N	\N
8298	Panel Average	5000	neutropenic	45752	9	\N	\N	\N
8605	Jonathan Chen	5000	neutropenic	45752	7	4	Blood Cultures	\N
8767	Andre Kumar	5000	neutropenic	45752	6	5	Blood Cultures	\N
7957	Jason Hom	5000	neutropenic	45760	10	5	\N	\N
8686	Panel Average	5000	neutropenic	45760	6	\N	\N	\N
8768	Andre Kumar	5000	neutropenic	45760	6	2	Blood gas	\N
8769	Panel Consensus	5000	neutropenic	45760	6	\N	\N	\N
9788	Lisa Shieh	5000	neutropenic	45760	3	3	\N	\N
10115	Jonathan Chen	5000	neutropenic	45760	2	2	Blood Gas	\N
10335	Andre Kumar	5003	neutropenic	45919	1	2	Blood Gas	\N
10336	Panel Average	5003	neutropenic	45919	1	\N	\N	\N
7958	Jason Hom	5003	neutropenic	44395	10	5	\N	\N
7959	Panel Consensus	5003	neutropenic	44395	10	\N	\N	\N
8606	Jonathan Chen	5003	neutropenic	44395	7	4	IVF	\N
9242	Panel Average	5003	neutropenic	44395	5	\N	\N	\N
9789	Lisa Shieh	5003	neutropenic	44395	3	3	\N	\N
10116	Andre Kumar	5003	neutropenic	44395	2	3	Fluids	\N
11290	Jonathan Chen	5003	neutropenic	44439	7	4	IVF	\N
7960	Jason Hom	5000	neutropenic	44290	10	5	\N	\N
7961	Panel Consensus	5000	neutropenic	44290	10	\N	\N	\N
8607	Jonathan Chen	5000	neutropenic	44290	7	4	IVF	\N
8770	Panel Average	5000	neutropenic	44290	6	\N	\N	\N
9243	Andre Kumar	5000	neutropenic	44290	5	5	Fluids	\N
9790	Lisa Shieh	5000	neutropenic	44290	3	3	\N	\N
7962	Jason Hom	5002	neutropenic	45793	10	5	\N	\N
8608	Panel Consensus	5002	neutropenic	45793	7	\N	\N	\N
8672	Panel Average	5002	neutropenic	45793	7	\N	\N	\N
9244	Andre Kumar	5002	neutropenic	45793	5	5	CBC	\N
9245	Lisa Shieh	5002	neutropenic	45793	5	3	\N	\N
9528	Jonathan Chen	5002	neutropenic	45793	4	4	CBC	\N
11462	Jonathan Chen	5003	neutropenic	45793	4	4	CBC	\N
7963	Jason Hom	5002	neutropenic	45788	10	5	\N	\N
8411	Panel Consensus	5002	neutropenic	45788	8	\N	\N	\N
8460	Panel Average	5002	neutropenic	45788	7	\N	\N	\N
8609	Lisa Shieh	5002	neutropenic	45788	7	3	\N	\N
9246	Andre Kumar	5002	neutropenic	45788	5	5	CBC	\N
9529	Jonathan Chen	5002	neutropenic	45788	4	4	CBC	\N
11402	Jonathan Chen	5003	neutropenic	45788	4	4	CBC	\N
7964	Jason Hom	5000	neutropenic	45788	10	5	\N	\N
8412	Panel Consensus	5000	neutropenic	45788	8	\N	\N	\N
8444	Panel Average	5000	neutropenic	45788	8	\N	\N	\N
8610	Lisa Shieh	5000	neutropenic	45788	7	3	\N	\N
8771	Andre Kumar	5000	neutropenic	45788	6	5	CBC	\N
9530	Jonathan Chen	5000	neutropenic	45788	4	4	CBC	\N
11355	Jonathan Chen	5002	neutropenic	45966	4	4	CBC	\N
7965	Jason Hom	5000	neutropenic	45966	10	5	\N	\N
8286	Lisa Shieh	5000	neutropenic	45966	9	3	\N	\N
8328	Panel Average	5000	neutropenic	45966	8	\N	\N	\N
8413	Panel Consensus	5000	neutropenic	45966	8	\N	\N	\N
8772	Andre Kumar	5000	neutropenic	45966	6	5	CBC	\N
9531	Jonathan Chen	5000	neutropenic	45966	4	4	CBC	\N
7966	Andre Kumar	5002	neutropenic	36210	10	5	Antibiotics	\N
7967	Jason Hom	5002	neutropenic	36210	10	5	\N	\N
7968	Jonathan Chen	5002	neutropenic	36210	10	5	Anti-Pseudomonas	\N
7969	Lisa Shieh	5002	neutropenic	36210	10	5	\N	\N
7970	Panel Average	5002	neutropenic	36210	10	\N	\N	\N
7971	Panel Consensus	5002	neutropenic	36210	10	\N	\N	\N
11475	Jonathan Chen	5003	neutropenic	36210	10	5	Anti-Pseudomonas	\N
7972	Andre Kumar	5000	neutropenic	36210	10	5	Antibiotics	\N
7973	Jason Hom	5000	neutropenic	36210	10	5	\N	\N
7974	Jonathan Chen	5000	neutropenic	36210	10	5	Anti-Pseudomonas	\N
7975	Lisa Shieh	5000	neutropenic	36210	10	5	\N	\N
7976	Panel Average	5000	neutropenic	36210	10	\N	\N	\N
7977	Panel Consensus	5000	neutropenic	36210	10	\N	\N	\N
11167	Andre Kumar	5000	neutropenic	35733	-5	3	Antibiotics	\N
11168	Panel Average	5000	neutropenic	35733	-5	\N	\N	\N
11449	Jonathan Chen	5002	neutropenic	50547	0	4	\N	Consult
11249	Jonathan Chen	5002	neutropenic	48980	0	4	\N	Consult
9247	Jason Hom	5003	neutropenic	48980	5	5	\N	\N
9248	Lisa Shieh	5003	neutropenic	48980	5	3	\N	\N
9532	Panel Average	5003	neutropenic	48980	4	\N	\N	\N
9533	Panel Consensus	5003	neutropenic	48980	4	\N	\N	\N
10117	Andre Kumar	5003	neutropenic	48980	2	2	Consult	\N
10810	Jonathan Chen	5003	neutropenic	48980	0	3	\N	\N
10118	Andre Kumar	5003	neutropenic	49207	2	2	Consult	\N
10119	Panel Average	5003	neutropenic	49207	2	\N	\N	\N
7978	Jason Hom	5002	neutropenic	49228	10	5	\N	\N
8874	Panel Average	5002	neutropenic	49228	5	\N	\N	\N
9249	Panel Consensus	5002	neutropenic	49228	5	\N	\N	\N
9791	Andre Kumar	5002	neutropenic	49228	3	1	Consult	\N
9792	Lisa Shieh	5002	neutropenic	49228	3	3	\N	\N
10811	Jonathan Chen	5002	neutropenic	49228	0	3	\N	\N
11442	Jonathan Chen	5003	neutropenic	49228	0	4	\N	Consult
11287	Jonathan Chen	5002	neutropenic	48711	0	2	\N	Wrong type of isolation
10812	Andre Kumar	5003	neutropenic	48711	0	4	Isolation	\N
10813	Panel Average	5003	neutropenic	48711	0	\N	\N	\N
11292	Jonathan Chen	5000	neutropenic	48532	0	2	\N	\N
7979	Jason Hom	5003	neutropenic	46286	10	5	\N	\N
9250	Panel Average	5003	neutropenic	46286	5	\N	\N	\N
9251	Panel Consensus	5003	neutropenic	46286	5	\N	\N	\N
9793	Lisa Shieh	5003	neutropenic	46286	3	3	\N	\N
10120	Andre Kumar	5003	neutropenic	46286	2	1	Coags	\N
10814	Jonathan Chen	5003	neutropenic	46286	0	2	\N	No reason to expect DIC at this point?
9252	Jason Hom	5003	neutropenic	48686	5	4	\N	\N
9253	Lisa Shieh	5003	neutropenic	48686	5	3	\N	\N
9534	Panel Average	5003	neutropenic	48686	4	\N	\N	\N
10121	Andre Kumar	5003	neutropenic	48686	2	3	Diet	\N
10122	Panel Consensus	5003	neutropenic	48686	2	\N	\N	\N
10815	Jonathan Chen	5003	neutropenic	48686	0	3	\N	\N
9254	Jason Hom	5000	neutropenic	48686	5	4	\N	\N
9255	Lisa Shieh	5000	neutropenic	48686	5	3	\N	\N
9535	Panel Average	5000	neutropenic	48686	4	\N	\N	\N
10123	Andre Kumar	5000	neutropenic	48686	2	1	Diet	\N
10124	Panel Consensus	5000	neutropenic	48686	2	\N	\N	\N
10816	Jonathan Chen	5000	neutropenic	48686	0	3	\N	\N
11357	Jonathan Chen	5003	neutropenic	46004	0	2	\N	\N
11378	Jonathan Chen	5003	neutropenic	45811	0	2	\N	Unnecessary?
11296	Jonathan Chen	5003	neutropenic	49054	0	3	\N	Neutropenic, not droplet isolation
7980	Jason Hom	5000	neutropenic	49054	10	5	\N	\N
9256	Lisa Shieh	5000	neutropenic	49054	5	3	\N	\N
9257	Panel Average	5000	neutropenic	49054	5	\N	\N	\N
9258	Panel Consensus	5000	neutropenic	49054	5	\N	\N	\N
10817	Andre Kumar	5000	neutropenic	49054	0	4	Isolation	\N
10818	Jonathan Chen	5000	neutropenic	49054	0	3	\N	Neutropenic, not droplet isolation
7981	Jason Hom	5002	neutropenic	45866	10	5	\N	\N
9434	Panel Average	5002	neutropenic	45866	5	\N	\N	\N
9536	Panel Consensus	5002	neutropenic	45866	4	\N	\N	\N
9794	Lisa Shieh	5002	neutropenic	45866	3	3	\N	\N
10125	Jonathan Chen	5002	neutropenic	45866	2	2	\N	Tachycardia eval?
10337	Andre Kumar	5002	neutropenic	45866	1	1	ECG + monitoring	\N
7982	Jason Hom	5003	neutropenic	45866	10	5	\N	\N
9537	Panel Consensus	5003	neutropenic	45866	4	\N	\N	\N
9611	Panel Average	5003	neutropenic	45866	3	\N	\N	\N
10126	Jonathan Chen	5003	neutropenic	45866	2	2	\N	Tachycardia eval?
10819	Andre Kumar	5003	neutropenic	45866	0	1	ECG + monitoring	\N
10820	Lisa Shieh	5003	neutropenic	45866	0	3	\N	\N
7983	Jason Hom	5000	neutropenic	45866	10	5	\N	\N
9460	Panel Average	5000	neutropenic	45866	4	\N	\N	\N
9538	Panel Consensus	5000	neutropenic	45866	4	\N	\N	\N
9795	Lisa Shieh	5000	neutropenic	45866	3	3	\N	\N
10127	Jonathan Chen	5000	neutropenic	45866	2	2	\N	Tachycardia eval?
10821	Andre Kumar	5000	neutropenic	45866	0	1	ECG + Monitoring	\N
11319	Jonathan Chen	5000	neutropenic	46160	0	4	\N	Process
11399	Jonathan Chen	5000	neutropenic	41759	0	4	\N	Presenting symptom
11374	Jonathan Chen	5002	neutropenic	45225	7	4	\N	Reduce hospitalized neutropenic time
11369	Jonathan Chen	5002	neutropenic	44252	10	5	Anti-Pseudomonas	\N
7984	Andre Kumar	5002	neutropenic	44237	10	5	Antibiotics	\N
7985	Jason Hom	5002	neutropenic	44237	10	5	\N	\N
7986	Jonathan Chen	5002	neutropenic	44237	10	5	Anti-Pseudomonas	\N
7987	Lisa Shieh	5002	neutropenic	44237	10	5	\N	\N
7988	Panel Average	5002	neutropenic	44237	10	\N	\N	\N
7989	Panel Consensus	5002	neutropenic	44237	10	\N	\N	\N
7990	Andre Kumar	5000	neutropenic	44237	10	5	Antibiotics	\N
7991	Jason Hom	5000	neutropenic	44237	10	5	\N	\N
7992	Jonathan Chen	5000	neutropenic	44237	10	5	Anti-Pseudomonas	\N
7993	Lisa Shieh	5000	neutropenic	44237	10	5	\N	\N
7994	Panel Average	5000	neutropenic	44237	10	\N	\N	\N
7995	Panel Consensus	5000	neutropenic	44237	10	\N	\N	\N
11274	Jonathan Chen	5002	neutropenic	46006	0	2	\N	\N
9259	Jason Hom	5000	neutropenic	46020	5	4	\N	\N
9941	Panel Average	5000	neutropenic	46020	2	\N	\N	\N
10128	Andre Kumar	5000	neutropenic	46020	2	4	Blood gas	\N
10129	Jonathan Chen	5000	neutropenic	46020	2	2	Blood Gas	\N
10130	Panel Consensus	5000	neutropenic	46020	2	\N	\N	\N
10822	Lisa Shieh	5000	neutropenic	46020	0	3	\N	\N
7996	Jason Hom	5002	neutropenic	62151	10	5	\N	\N
7997	Panel Consensus	5002	neutropenic	62151	10	\N	\N	\N
8673	Panel Average	5002	neutropenic	62151	7	\N	\N	\N
8773	Jonathan Chen	5002	neutropenic	62151	6	4	Lactate	\N
9260	Andre Kumar	5002	neutropenic	62151	5	4	Lactate	\N
9261	Lisa Shieh	5002	neutropenic	62151	5	3	\N	\N
7998	Jason Hom	5003	neutropenic	62151	10	5	\N	\N
7999	Panel Consensus	5003	neutropenic	62151	10	\N	\N	\N
8774	Jonathan Chen	5003	neutropenic	62151	6	4	Lactate	\N
8775	Panel Average	5003	neutropenic	62151	6	\N	\N	\N
9262	Lisa Shieh	5003	neutropenic	62151	5	3	\N	\N
9796	Andre Kumar	5003	neutropenic	62151	3	1	Lactate	\N
8000	Jason Hom	5000	neutropenic	62151	10	5	\N	\N
8001	Panel Consensus	5000	neutropenic	62151	10	\N	\N	\N
8674	Panel Average	5000	neutropenic	62151	7	\N	\N	\N
8776	Jonathan Chen	5000	neutropenic	62151	6	4	Lactate	\N
9263	Andre Kumar	5000	neutropenic	62151	5	5	Lactate	\N
9264	Lisa Shieh	5000	neutropenic	62151	5	3	\N	\N
9797	Andre Kumar	5003	neutropenic	45918	3	2	Lactate	\N
9798	Panel Average	5003	neutropenic	45918	3	\N	\N	\N
9265	Andre Kumar	5000	neutropenic	45918	5	4	Lactate	\N
9266	Panel Average	5000	neutropenic	45918	5	\N	\N	\N
9539	Jason Hom	5000	neutropenic	45903	4	4	\N	\N
9799	Lisa Shieh	5000	neutropenic	45903	3	\N	\N	\N
9942	Panel Average	5000	neutropenic	45903	2	\N	\N	\N
10131	Panel Consensus	5000	neutropenic	45903	2	\N	\N	\N
10338	Jonathan Chen	5000	neutropenic	45903	1	2	Tumor Lysis	Worth tracking?
10823	Andre Kumar	5000	neutropenic	45903	0	1	\N	\N
10824	Andre Kumar	5000	neutropenic	45894	0	1	Lipase	\N
10825	Panel Average	5000	neutropenic	45894	0	\N	\N	\N
8002	Jason Hom	5002	neutropenic	45806	10	5	\N	\N
8875	Panel Average	5002	neutropenic	45806	5	\N	\N	\N
9800	Andre Kumar	5002	neutropenic	45806	3	4	Metabolic Panel	\N
9801	Lisa Shieh	5002	neutropenic	45806	3	3	\N	\N
9802	Panel Consensus	5002	neutropenic	45806	3	\N	\N	\N
10826	Jonathan Chen	5002	neutropenic	45806	0	2	\N	\N
11436	Jonathan Chen	5003	neutropenic	45806	0	2	\N	\N
11323	Jonathan Chen	5000	neutropenic	45806	0	2	\N	\N
8003	Jason Hom	5002	neutropenic	45763	10	5	\N	\N
8004	Panel Consensus	5002	neutropenic	45763	10	\N	\N	\N
8777	Panel Average	5002	neutropenic	45763	6	\N	\N	\N
9267	Lisa Shieh	5002	neutropenic	45763	5	3	\N	\N
9803	Andre Kumar	5002	neutropenic	45763	3	3	Metabolic panel	\N
9804	Jonathan Chen	5002	neutropenic	45763	3	3	Metabolic Panel	\N
11304	Jonathan Chen	5003	neutropenic	45763	3	3	Metabolic Panel	\N
8005	Jason Hom	5000	neutropenic	45763	10	5	\N	\N
8006	Panel Consensus	5000	neutropenic	45763	10	\N	\N	\N
8687	Panel Average	5000	neutropenic	45763	6	\N	\N	\N
9268	Lisa Shieh	5000	neutropenic	45763	5	3	\N	\N
9540	Andre Kumar	5000	neutropenic	45763	4	2	Metabolic Panel	\N
9805	Jonathan Chen	5000	neutropenic	45763	3	3	Metabolic Panel	\N
8007	Jason Hom	5002	neutropenic	45771	10	5	\N	\N
8008	Panel Consensus	5002	neutropenic	45771	10	\N	\N	\N
8778	Panel Average	5002	neutropenic	45771	6	\N	\N	\N
9269	Lisa Shieh	5002	neutropenic	45771	5	3	\N	\N
9806	Andre Kumar	5002	neutropenic	45771	3	4	Metabolic Panel	\N
9807	Jonathan Chen	5002	neutropenic	45771	3	3	Metabolic Panel	\N
11400	Jonathan Chen	5003	neutropenic	45771	3	3	Metabolic Panel	\N
8009	Jason Hom	5000	neutropenic	45771	10	5	\N	\N
8010	Panel Consensus	5000	neutropenic	45771	10	\N	\N	\N
8688	Panel Average	5000	neutropenic	45771	6	\N	\N	\N
9270	Lisa Shieh	5000	neutropenic	45771	5	3	\N	\N
9541	Andre Kumar	5000	neutropenic	45771	4	2	MEtabolic Panel	\N
9808	Jonathan Chen	5000	neutropenic	45771	3	3	Metabolic Panel	\N
9271	Jason Hom	5002	neutropenic	45792	5	4	\N	\N
9612	Panel Average	5002	neutropenic	45792	3	\N	\N	\N
9809	Lisa Shieh	5002	neutropenic	45792	3	3	\N	\N
10132	Andre Kumar	5002	neutropenic	45792	2	5	MRSA	\N
10133	Panel Consensus	5002	neutropenic	45792	2	\N	\N	\N
10339	Jonathan Chen	5002	neutropenic	45792	1	2	\N	Reasonable if helps triage Vancomycin decision?
9272	Jason Hom	5003	neutropenic	45792	5	4	\N	\N
9592	Panel Average	5003	neutropenic	45792	4	\N	\N	\N
9810	Andre Kumar	5003	neutropenic	45792	3	2	MRSA	\N
9811	Lisa Shieh	5003	neutropenic	45792	3	3	\N	\N
10134	Panel Consensus	5003	neutropenic	45792	2	\N	\N	\N
10340	Jonathan Chen	5003	neutropenic	45792	1	2	\N	Reasonable if helps triage Vancomycin decision?
8011	Jason Hom	5002	neutropenic	48960	10	5	\N	\N
8012	Lisa Shieh	5002	neutropenic	48960	10	5	\N	\N
8414	Panel Consensus	5002	neutropenic	48960	8	\N	\N	\N
8445	Panel Average	5002	neutropenic	48960	8	\N	\N	\N
8779	Jonathan Chen	5002	neutropenic	48960	6	4	\N	\N
9812	Andre Kumar	5002	neutropenic	48960	3	1	Isolation	\N
8013	Jason Hom	5003	neutropenic	48960	10	5	\N	\N
8014	Lisa Shieh	5003	neutropenic	48960	10	3	\N	\N
8415	Panel Consensus	5003	neutropenic	48960	8	\N	\N	\N
8461	Panel Average	5003	neutropenic	48960	7	\N	\N	\N
8780	Jonathan Chen	5003	neutropenic	48960	6	4	\N	\N
10135	Andre Kumar	5003	neutropenic	48960	2	3	Isolation	\N
8015	Jason Hom	5000	neutropenic	48960	10	5	\N	\N
8416	Panel Consensus	5000	neutropenic	48960	8	\N	\N	\N
8611	Lisa Shieh	5000	neutropenic	48960	7	3	\N	\N
8675	Panel Average	5000	neutropenic	48960	7	\N	\N	\N
8781	Jonathan Chen	5000	neutropenic	48960	6	4	\N	\N
9813	Andre Kumar	5000	neutropenic	48960	3	4	Isolation	\N
10827	Andre Kumar	5003	neutropenic	45853	0	5	BNP	\N
10828	Panel Average	5003	neutropenic	45853	0	\N	\N	\N
11237	Jonathan Chen	5000	neutropenic	44420	0	2	\N	Symptom management
11429	Jonathan Chen	5000	neutropenic	45900	0	2	\N	Irrelevant
10136	Andre Kumar	5000	neutropenic	61823	2	3	Nursing	\N
10137	Panel Average	5000	neutropenic	61823	2	\N	\N	\N
10138	Andre Kumar	5000	neutropenic	45802	2	1	Nursing	\N
10139	Panel Average	5000	neutropenic	45802	2	\N	\N	\N
11297	Jonathan Chen	5003	neutropenic	45778	0	2	\N	\N
11294	Jonathan Chen	5002	neutropenic	50554	0	4	\N	Irrelevant
11371	Jonathan Chen	5003	neutropenic	50554	0	4	\N	Irrelevant
11326	Jonathan Chen	5003	neutropenic	45955	6	4	Lactate	\N
8016	Panel Consensus	5000	neutropenic	45955	10	\N	\N	\N
8782	Jonathan Chen	5000	neutropenic	45955	6	4	Lactate	\N
9542	Jason Hom	5000	neutropenic	45955	4	4	\N	\N
9814	Lisa Shieh	5000	neutropenic	45955	3	3	\N	\N
9815	Panel Average	5000	neutropenic	45955	3	\N	\N	\N
10140	Andre Kumar	5000	neutropenic	45955	2	3	Blood gas	\N
9816	Jonathan Chen	5000	neutropenic	46000	3	4	UA	\N
10829	Andre Kumar	5000	neutropenic	46000	0	1	Urinalysis	\N
10830	Jason Hom	5000	neutropenic	46000	0	4	\N	\N
10831	Lisa Shieh	5000	neutropenic	46000	0	3	not symptomatic?	\N
10832	Panel Average	5000	neutropenic	46000	0	\N	\N	\N
10833	Panel Consensus	5000	neutropenic	46000	0	\N	\N	\N
8017	Jason Hom	5002	neutropenic	45759	10	5	\N	\N
9461	Panel Average	5002	neutropenic	45759	4	\N	\N	\N
9543	Panel Consensus	5002	neutropenic	45759	4	\N	\N	\N
9817	Andre Kumar	5002	neutropenic	45759	3	4	Coags	\N
10834	Jonathan Chen	5002	neutropenic	45759	0	3	\N	\N
10835	Lisa Shieh	5002	neutropenic	45759	0	3	\N	\N
11336	Jonathan Chen	5003	neutropenic	45759	0	3	\N	\N
11453	Jonathan Chen	5000	neutropenic	45759	0	3	\N	\N
8018	Jason Hom	5002	neutropenic	45770	10	5	\N	\N
9462	Panel Average	5002	neutropenic	45770	4	\N	\N	\N
9544	Panel Consensus	5002	neutropenic	45770	4	\N	\N	\N
9818	Andre Kumar	5002	neutropenic	45770	3	4	Coags	\N
10836	Jonathan Chen	5002	neutropenic	45770	0	3	\N	\N
10837	Lisa Shieh	5002	neutropenic	45770	0	3	\N	\N
11279	Jonathan Chen	5003	neutropenic	45770	0	3	\N	\N
11403	Jonathan Chen	5000	neutropenic	45770	0	3	\N	\N
10341	Andre Kumar	5003	neutropenic	52757	1	2	PT/OT	\N
10342	Panel Average	5003	neutropenic	52757	1	\N	\N	\N
10141	Andre Kumar	5000	neutropenic	45890	2	5	Blood Gas	\N
10142	Jonathan Chen	5000	neutropenic	45890	2	2	Blood Gas	\N
10388	Panel Average	5000	neutropenic	45890	1	\N	\N	\N
10838	Jason Hom	5000	neutropenic	45890	0	4	\N	\N
10839	Lisa Shieh	5000	neutropenic	45890	0	3	\N	\N
10840	Panel Consensus	5000	neutropenic	45890	0	\N	\N	\N
11358	Jonathan Chen	5003	neutropenic	62023	2	3	Respiratory Virus Screen	\N
8019	Jason Hom	5000	neutropenic	62023	10	5	\N	\N
8783	Panel Average	5000	neutropenic	62023	6	\N	\N	\N
8784	Panel Consensus	5000	neutropenic	62023	6	\N	\N	\N
9273	Lisa Shieh	5000	neutropenic	62023	5	3	\N	\N
9819	Andre Kumar	5000	neutropenic	62023	3	2	Respiratory Viral Panel	\N
8796	Panel Consensus	5000	neutropenic	45782	6	\N	\N	\N
10143	Jonathan Chen	5000	neutropenic	62023	2	3	Respiratory Virus Screen	\N
8020	Jason Hom	5002	neutropenic	63923	10	5	\N	\N
8785	Panel Average	5002	neutropenic	63923	6	\N	\N	\N
8786	Panel Consensus	5002	neutropenic	63923	6	\N	\N	\N
9274	Lisa Shieh	5002	neutropenic	63923	5	3	\N	\N
9820	Andre Kumar	5002	neutropenic	63923	3	3	Respiratory Viral Panel	\N
10144	Jonathan Chen	5002	neutropenic	63923	2	3	Respiratory Virus Screen	\N
11302	Jonathan Chen	5003	neutropenic	63923	2	3	Respiratory Virus Screen	\N
8021	Jason Hom	5000	neutropenic	63923	10	5	\N	\N
8787	Panel Average	5000	neutropenic	63923	6	\N	\N	\N
8788	Panel Consensus	5000	neutropenic	63923	6	\N	\N	\N
9275	Lisa Shieh	5000	neutropenic	63923	5	3	\N	\N
9821	Andre Kumar	5000	neutropenic	63923	3	1	Respiratory Viral Panel	\N
10145	Jonathan Chen	5000	neutropenic	63923	2	3	Respiratory Virus Screen	\N
11310	Jonathan Chen	5002	neutropenic	63725	6	4	Lactate	\N
8022	Jason Hom	5003	neutropenic	63725	10	5	\N	\N
8023	Panel Consensus	5003	neutropenic	63725	10	\N	\N	\N
8789	Jonathan Chen	5003	neutropenic	63725	6	4	Lactate	\N
8790	Panel Average	5003	neutropenic	63725	6	\N	\N	\N
9276	Lisa Shieh	5003	neutropenic	63725	5	3	\N	\N
9822	Andre Kumar	5003	neutropenic	63725	3	1	Lactate	\N
8024	Jason Hom	5000	neutropenic	63725	10	5	\N	\N
8025	Panel Consensus	5000	neutropenic	63725	10	\N	\N	\N
8676	Panel Average	5000	neutropenic	63725	7	\N	\N	\N
8791	Jonathan Chen	5000	neutropenic	63725	6	4	Lactate	\N
9277	Andre Kumar	5000	neutropenic	63725	5	4	lactate	\N
9278	Lisa Shieh	5000	neutropenic	63725	5	3	\N	\N
8026	Jason Hom	5002	neutropenic	44198	10	5	\N	\N
8027	Panel Consensus	5002	neutropenic	44198	10	\N	\N	\N
8462	Panel Average	5002	neutropenic	44198	7	\N	\N	\N
8612	Jonathan Chen	5002	neutropenic	44198	7	4	IVF	\N
8613	Lisa Shieh	5002	neutropenic	44198	7	3	\N	\N
9279	Andre Kumar	5002	neutropenic	44198	5	5	Fluids	\N
8028	Jason Hom	5003	neutropenic	44198	10	5	\N	\N
8029	Panel Consensus	5003	neutropenic	44198	10	\N	\N	\N
8614	Jonathan Chen	5003	neutropenic	44198	7	4	IVF	\N
8615	Lisa Shieh	5003	neutropenic	44198	7	3	\N	\N
8689	Panel Average	5003	neutropenic	44198	6	\N	\N	\N
10146	Andre Kumar	5003	neutropenic	44198	2	3	Fluids	\N
8030	Jason Hom	5000	neutropenic	44198	10	5	\N	\N
8031	Panel Consensus	5000	neutropenic	44198	10	\N	\N	\N
8463	Panel Average	5000	neutropenic	44198	7	\N	\N	\N
8616	Jonathan Chen	5000	neutropenic	44198	7	4	IVF	\N
8617	Lisa Shieh	5000	neutropenic	44198	7	3	\N	\N
9280	Andre Kumar	5000	neutropenic	44198	5	5	Fluids	\N
11282	Jonathan Chen	5000	neutropenic	45945	1	2	\N	Anticipating transfusions, but not needed now
11331	Jonathan Chen	5003	neutropenic	45995	1	2	Tumor Lysis	\N
9281	Jason Hom	5000	neutropenic	45995	5	4	\N	\N
9823	Lisa Shieh	5000	neutropenic	45995	3	3	\N	\N
9824	Panel Consensus	5000	neutropenic	45995	3	\N	\N	\N
9922	Panel Average	5000	neutropenic	45995	3	\N	\N	\N
10343	Jonathan Chen	5000	neutropenic	45995	1	2	Tumor Lysis	\N
10841	Andre Kumar	5000	neutropenic	45995	0	1	Tumor Lysis	\N
9825	Andre Kumar	5002	neutropenic	45751	3	5	Urinalysis	\N
9826	Panel Average	5002	neutropenic	45751	3	\N	\N	\N
8618	Lisa Shieh	5000	neutropenic	45751	7	3	\N	\N
8792	Panel Consensus	5000	neutropenic	45751	6	\N	\N	\N
8852	Panel Average	5000	neutropenic	45751	6	\N	\N	\N
9282	Andre Kumar	5000	neutropenic	45751	5	2	Urinalysis	\N
9283	Jason Hom	5000	neutropenic	45751	5	4	\N	\N
9827	Jonathan Chen	5000	neutropenic	45751	3	3	UA	\N
8793	Panel Consensus	5000	neutropenic	45873	6	\N	\N	\N
9284	Andre Kumar	5000	neutropenic	45873	5	5	Urinalysis	\N
9285	Jason Hom	5000	neutropenic	45873	5	4	\N	\N
9463	Panel Average	5000	neutropenic	45873	4	\N	\N	\N
9828	Jonathan Chen	5000	neutropenic	45873	3	4	UA	\N
9829	Lisa Shieh	5000	neutropenic	45873	3	3	\N	\N
8794	Panel Consensus	5002	neutropenic	45782	6	\N	\N	\N
9286	Andre Kumar	5002	neutropenic	45782	5	5	Urine Culture	\N
9287	Jason Hom	5002	neutropenic	45782	5	4	\N	\N
9464	Panel Average	5002	neutropenic	45782	4	\N	\N	\N
9830	Jonathan Chen	5002	neutropenic	45782	3	4	UA	\N
9831	Lisa Shieh	5002	neutropenic	45782	3	3	\N	\N
8795	Panel Consensus	5003	neutropenic	45782	6	\N	\N	\N
9288	Jason Hom	5003	neutropenic	45782	5	4	\N	\N
9545	Andre Kumar	5003	neutropenic	45782	4	4	Urine Culture	\N
9546	Panel Average	5003	neutropenic	45782	4	\N	\N	\N
9832	Jonathan Chen	5003	neutropenic	45782	3	4	UA	\N
9833	Lisa Shieh	5003	neutropenic	45782	3	3	\N	\N
9289	Andre Kumar	5000	neutropenic	45782	5	5	Urine Culture	\N
9290	Jason Hom	5000	neutropenic	45782	5	4	\N	\N
9613	Panel Average	5000	neutropenic	45782	3	\N	\N	\N
9834	Jonathan Chen	5000	neutropenic	45782	3	4	UA	\N
10842	Lisa Shieh	5000	neutropenic	45782	0	3	\N	\N
9291	Jonathan Chen	5002	neutropenic	43997	5	3	\N	Case deliberately ambiguous about needing vancomycin / MRSA coverage. With elevated lactate, reasonable to assess as severe sepsis for empiric coverage
9292	Lisa Shieh	5002	neutropenic	43997	5	3	\N	\N
9943	Panel Average	5002	neutropenic	43997	2	\N	\N	\N
10147	Jason Hom	5002	neutropenic	43997	2	5	\N	\N
10148	Panel Consensus	5002	neutropenic	43997	2	\N	\N	\N
10843	Andre Kumar	5002	neutropenic	43997	0	4	Antibiotics	\N
8619	Lisa Shieh	5003	neutropenic	43997	7	3	\N	\N
9293	Jonathan Chen	5003	neutropenic	43997	5	3	\N	Case deliberately ambiguous about needing vancomycin / MRSA coverage. With elevated lactate, reasonable to assess as severe sepsis for empiric coverage
9835	Panel Average	5003	neutropenic	43997	3	\N	\N	\N
10149	Jason Hom	5003	neutropenic	43997	2	4	\N	\N
10150	Panel Consensus	5003	neutropenic	43997	2	\N	\N	\N
10844	Andre Kumar	5003	neutropenic	43997	0	5	Antibiotics	\N
9294	Jonathan Chen	5000	neutropenic	43997	5	3	\N	Case deliberately ambiguous about needing vancomycin / MRSA coverage. With elevated lactate, reasonable to assess as severe sepsis for empiric coverage
9295	Lisa Shieh	5000	neutropenic	43997	5	3	\N	\N
9944	Panel Average	5000	neutropenic	43997	2	\N	\N	\N
10151	Jason Hom	5000	neutropenic	43997	2	4	\N	\N
10152	Panel Consensus	5000	neutropenic	43997	2	\N	\N	\N
10845	Andre Kumar	5000	neutropenic	43997	0	5	Antibiotics	\N
11478	Jonathan Chen	5000	neutropenic	45972	2	3	\N	\N
9836	Andre Kumar	5002	neutropenic	63735	3	3	Respiratory Viral Panel	\N
9837	Lisa Shieh	5002	neutropenic	63735	3	3	\N	\N
10153	Jonathan Chen	5002	neutropenic	63735	2	3	Respiratory Virus Screen	\N
10154	Panel Average	5002	neutropenic	63735	2	\N	\N	\N
10846	Jason Hom	5002	neutropenic	63735	0	5	\N	\N
10847	Panel Consensus	5002	neutropenic	63735	0	\N	\N	\N
9838	Andre Kumar	5003	neutropenic	63735	3	2	Respiratory Viral Panel	\N
10155	Jonathan Chen	5003	neutropenic	63735	2	3	Respiratory Virus Screen	\N
10344	Panel Average	5003	neutropenic	63735	1	\N	\N	\N
10848	Jason Hom	5003	neutropenic	63735	0	5	\N	\N
10849	Lisa Shieh	5003	neutropenic	63735	0	3	\N	\N
10850	Panel Consensus	5003	neutropenic	63735	0	\N	\N	\N
11238	Jonathan Chen	5000	neutropenic	45766	0	2	\N	Process
8032	Jason Hom	5002	neutropenic	45818	10	5	\N	\N
8033	Panel Consensus	5002	neutropenic	45818	10	\N	\N	\N
8677	Panel Average	5002	neutropenic	45818	7	\N	\N	\N
9296	Andre Kumar	5002	neutropenic	45818	5	2	Imaging	\N
9297	Lisa Shieh	5002	neutropenic	45818	5	3	\N	\N
9839	Jonathan Chen	5002	neutropenic	45818	3	3	CXR	\N
8034	Jason Hom	5003	neutropenic	45818	10	5	\N	\N
8035	Panel Consensus	5003	neutropenic	45818	10	\N	\N	\N
8853	Panel Average	5003	neutropenic	45818	6	\N	\N	\N
9547	Andre Kumar	5003	neutropenic	45818	4	4	Imaging	No points if already done
9840	Jonathan Chen	5003	neutropenic	45818	3	3	CXR	\N
9841	Lisa Shieh	5003	neutropenic	45818	3	3	\N	\N
8036	Jason Hom	5000	neutropenic	45818	10	5	\N	\N
8037	Panel Consensus	5000	neutropenic	45818	10	\N	\N	\N
8446	Panel Average	5000	neutropenic	45818	8	\N	\N	\N
8620	Lisa Shieh	5000	neutropenic	45818	7	3	\N	\N
8797	Andre Kumar	5000	neutropenic	45818	6	4	Imaging	\N
9842	Jonathan Chen	5000	neutropenic	45818	3	3	CXR	\N
8038	Jason Hom	5002	neutropenic	45801	10	5	\N	\N
8039	Panel Consensus	5002	neutropenic	45801	10	\N	\N	\N
8464	Panel Average	5002	neutropenic	45801	7	\N	\N	\N
8621	Lisa Shieh	5002	neutropenic	45801	7	3	\N	\N
9298	Andre Kumar	5002	neutropenic	45801	5	2	Imaging	\N
9843	Jonathan Chen	5002	neutropenic	45801	3	3	CXR	\N
8040	Jason Hom	5000	neutropenic	45801	10	5	\N	\N
8041	Panel Consensus	5000	neutropenic	45801	10	\N	\N	\N
8287	Lisa Shieh	5000	neutropenic	45801	9	3	\N	\N
8329	Panel Average	5000	neutropenic	45801	8	\N	\N	\N
8798	Andre Kumar	5000	neutropenic	45801	6	4	Imaging	\N
9844	Jonathan Chen	5000	neutropenic	45801	3	3	CXR	\N
8042	Jason Hom	10	pulmonary_embolism	45977	10	5	\N	\N
8043	Panel Consensus	10	pulmonary_embolism	45977	10	\N	\N	\N
9435	Panel Average	10	pulmonary_embolism	45977	5	\N	\N	\N
9845	Lisa Shieh	10	pulmonary_embolism	45977	3	3	\N	\N
10345	Andre Kumar	10	pulmonary_embolism	45977	1	1	Weight	\N
10851	Jonathan Chen	10	pulmonary_embolism	45977	0	2	\N	\N
8044	Jason Hom	11	pulmonary_embolism	45977	10	5	\N	\N
8045	Panel Consensus	11	pulmonary_embolism	45977	10	\N	\N	\N
8854	Panel Average	11	pulmonary_embolism	45977	6	\N	\N	\N
9299	Lisa Shieh	11	pulmonary_embolism	45977	5	3	\N	\N
10156	Andre Kumar	11	pulmonary_embolism	45977	2	2	Weight	\N
10852	Jonathan Chen	11	pulmonary_embolism	45977	0	2	\N	\N
11252	Jonathan Chen	11	pulmonary_embolism	65641	0	4	\N	Process
8046	Jason Hom	11	pulmonary_embolism	45814	10	5	\N	\N
8047	Panel Consensus	11	pulmonary_embolism	45814	10	\N	\N	\N
8690	Panel Average	11	pulmonary_embolism	45814	6	\N	\N	\N
9300	Lisa Shieh	11	pulmonary_embolism	45814	5	3	\N	\N
9548	Andre Kumar	11	pulmonary_embolism	45814	4	5	Admit	\N
10853	Jonathan Chen	11	pulmonary_embolism	45814	0	2	\N	\N
9549	Andre Kumar	11	pulmonary_embolism	61982	4	5	Admit	\N
9550	Panel Average	11	pulmonary_embolism	61982	4	\N	\N	\N
11443	Jonathan Chen	10	pulmonary_embolism	46309	2	4	Nebs	\N
11473	Jonathan Chen	11	pulmonary_embolism	46309	2	4	Nebs	\N
11311	Jonathan Chen	10	pulmonary_embolism	44349	2	4	Nebs	\N
11468	Jonathan Chen	10	pulmonary_embolism	60175	2	4	Nebs	\N
8048	Jason Hom	10	pulmonary_embolism	44330	10	5	\N	\N
8622	Lisa Shieh	10	pulmonary_embolism	44330	7	3	\N	\N
8623	Panel Consensus	10	pulmonary_embolism	44330	7	\N	\N	\N
8678	Panel Average	10	pulmonary_embolism	44330	7	\N	\N	\N
9846	Andre Kumar	10	pulmonary_embolism	44330	3	3	Nebs	\N
10157	Jonathan Chen	10	pulmonary_embolism	44330	2	4	Nebs	\N
11471	Jonathan Chen	12	pulmonary_embolism	60175	2	4	Nebs	\N
11340	Jonathan Chen	11	pulmonary_embolism	44349	2	4	Nebs	\N
11432	Jonathan Chen	11	pulmonary_embolism	60175	2	4	Nebs	\N
8049	Jason Hom	11	pulmonary_embolism	44330	10	5	\N	\N
8624	Panel Consensus	11	pulmonary_embolism	44330	7	\N	\N	\N
8855	Panel Average	11	pulmonary_embolism	44330	6	\N	\N	\N
9301	Lisa Shieh	11	pulmonary_embolism	44330	5	3	\N	\N
10158	Andre Kumar	11	pulmonary_embolism	44330	2	1	Nebs	\N
10159	Jonathan Chen	11	pulmonary_embolism	44330	2	4	Nebs	\N
11427	Jonathan Chen	11	pulmonary_embolism	44595	0	2	\N	Weird antibiotic choice?
11405	Jonathan Chen	10	pulmonary_embolism	47146	0	2	\N	\N
9302	Jason Hom	10	pulmonary_embolism	44206	5	5	\N	\N
9303	Lisa Shieh	10	pulmonary_embolism	44206	5	3	\N	\N
9551	Panel Average	10	pulmonary_embolism	44206	4	\N	\N	\N
9552	Panel Consensus	10	pulmonary_embolism	44206	4	\N	\N	\N
10160	Andre Kumar	10	pulmonary_embolism	44206	2	2	ACS meds	\N
10854	Jonathan Chen	10	pulmonary_embolism	44206	0	2	\N	\N
9304	Lisa Shieh	11	pulmonary_embolism	44206	5	3	\N	\N
9553	Panel Consensus	11	pulmonary_embolism	44206	4	\N	\N	\N
9945	Panel Average	11	pulmonary_embolism	44206	2	\N	\N	\N
10161	Andre Kumar	11	pulmonary_embolism	44206	2	1	ACS Medications	\N
10855	Jason Hom	11	pulmonary_embolism	44206	0	5	\N	\N
10856	Jonathan Chen	11	pulmonary_embolism	44206	0	2	\N	\N
11472	Jonathan Chen	8	pulmonary_embolism	44206	0	2	\N	\N
10346	Andre Kumar	10	pulmonary_embolism	44315	1	2	ACS meds	\N
10347	Panel Average	10	pulmonary_embolism	44315	1	\N	\N	\N
11270	Jonathan Chen	8	pulmonary_embolism	46551	0	2	\N	\N
10857	Andre Kumar	8	pulmonary_embolism	44240	0	5	Statin	\N
10858	Panel Average	8	pulmonary_embolism	44240	0	\N	\N	\N
8050	Jason Hom	10	pulmonary_embolism	35849	10	5	\N	\N
8799	Panel Average	10	pulmonary_embolism	35849	6	\N	\N	\N
8800	Panel Consensus	10	pulmonary_embolism	35849	6	\N	\N	\N
9305	Lisa Shieh	10	pulmonary_embolism	35849	5	3	\N	\N
9847	Andre Kumar	10	pulmonary_embolism	35849	3	3	Antibiotics	\N
10859	Jonathan Chen	10	pulmonary_embolism	35849	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8801	Panel Consensus	12	pulmonary_embolism	35849	6	\N	\N	\N
9306	Jason Hom	12	pulmonary_embolism	35849	5	5	\N	\N
9614	Panel Average	12	pulmonary_embolism	35849	3	\N	\N	\N
9848	Lisa Shieh	12	pulmonary_embolism	35849	3	3	\N	\N
10162	Andre Kumar	12	pulmonary_embolism	35849	2	1	Antibiotics	\N
10860	Jonathan Chen	12	pulmonary_embolism	35849	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8051	Jason Hom	11	pulmonary_embolism	35849	10	5	\N	\N
8802	Panel Consensus	11	pulmonary_embolism	35849	6	\N	\N	\N
8876	Panel Average	11	pulmonary_embolism	35849	5	\N	\N	\N
9307	Lisa Shieh	11	pulmonary_embolism	35849	5	3	\N	\N
10348	Andre Kumar	11	pulmonary_embolism	35849	1	2	Antibiotics	\N
10861	Jonathan Chen	11	pulmonary_embolism	35849	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8052	Jason Hom	10	pulmonary_embolism	44388	10	5	\N	\N
8803	Panel Consensus	10	pulmonary_embolism	44388	6	\N	\N	\N
8877	Panel Average	10	pulmonary_embolism	44388	5	\N	\N	\N
9308	Lisa Shieh	10	pulmonary_embolism	44388	5	3	\N	\N
10349	Andre Kumar	10	pulmonary_embolism	44388	1	3	Antibiotics	\N
10862	Jonathan Chen	10	pulmonary_embolism	44388	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8053	Jason Hom	11	pulmonary_embolism	44388	10	5	\N	\N
8804	Panel Consensus	11	pulmonary_embolism	44388	6	\N	\N	\N
9436	Panel Average	11	pulmonary_embolism	44388	5	\N	\N	\N
9849	Lisa Shieh	11	pulmonary_embolism	44388	3	3	\N	\N
10350	Andre Kumar	11	pulmonary_embolism	44388	1	2	Antibiotics	\N
10863	Jonathan Chen	11	pulmonary_embolism	44388	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8054	Jason Hom	11	pulmonary_embolism	45901	10	5	\N	\N
9309	Panel Consensus	11	pulmonary_embolism	45901	5	\N	\N	\N
9437	Panel Average	11	pulmonary_embolism	45901	5	\N	\N	\N
9850	Lisa Shieh	11	pulmonary_embolism	45901	3	3	\N	\N
10163	Jonathan Chen	11	pulmonary_embolism	45901	2	\N	Blood Cultures	Not infection, but reasonable to check if not empirically treat?
10351	Andre Kumar	11	pulmonary_embolism	45901	1	2	Blood Cultures	\N
8055	Jason Hom	11	pulmonary_embolism	45752	10	5	\N	\N
9310	Panel Consensus	11	pulmonary_embolism	45752	5	\N	\N	\N
9438	Panel Average	11	pulmonary_embolism	45752	5	\N	\N	\N
9851	Lisa Shieh	11	pulmonary_embolism	45752	3	3	\N	\N
10164	Jonathan Chen	11	pulmonary_embolism	45752	2	\N	Blood Cultures	\N
10352	Andre Kumar	11	pulmonary_embolism	45752	1	2	Blood Cultures	\N
8056	Jason Hom	10	pulmonary_embolism	45760	10	5	\N	\N
8465	Panel Average	10	pulmonary_embolism	45760	7	\N	\N	\N
8625	Lisa Shieh	10	pulmonary_embolism	45760	7	3	\N	\N
8626	Panel Consensus	10	pulmonary_embolism	45760	7	\N	\N	\N
9311	Andre Kumar	10	pulmonary_embolism	45760	5	5	Blood Gas	\N
9312	Jonathan Chen	10	pulmonary_embolism	45760	5	4	Blood Gas	\N
8057	Jason Hom	12	pulmonary_embolism	45760	10	5	\N	\N
8627	Panel Consensus	12	pulmonary_embolism	45760	7	\N	\N	\N
8691	Panel Average	12	pulmonary_embolism	45760	6	\N	\N	\N
9313	Jonathan Chen	12	pulmonary_embolism	45760	5	4	Blood Gas	\N
9314	Lisa Shieh	12	pulmonary_embolism	45760	5	3	\N	\N
9554	Andre Kumar	12	pulmonary_embolism	45760	4	3	Blood Gas	\N
9555	Andre Kumar	11	pulmonary_embolism	45760	4	4	Blood Gas	\N
9556	Panel Average	11	pulmonary_embolism	45760	4	\N	\N	\N
8058	Jason Hom	10	pulmonary_embolism	45919	10	5	\N	\N
9315	Jonathan Chen	10	pulmonary_embolism	45919	5	4	Blood Gas	\N
9316	Lisa Shieh	10	pulmonary_embolism	45919	5	3	\N	\N
9317	Panel Average	10	pulmonary_embolism	45919	5	\N	\N	\N
9318	Panel Consensus	10	pulmonary_embolism	45919	5	\N	\N	\N
10864	Andre Kumar	10	pulmonary_embolism	45919	0	5	Blood Gas	\N
8059	Jason Hom	12	pulmonary_embolism	45919	10	5	\N	\N
8805	Panel Average	12	pulmonary_embolism	45919	6	\N	\N	\N
9319	Jonathan Chen	12	pulmonary_embolism	45919	5	4	Blood Gas	\N
9320	Lisa Shieh	12	pulmonary_embolism	45919	5	3	\N	\N
9321	Panel Consensus	12	pulmonary_embolism	45919	5	\N	\N	\N
9852	Andre Kumar	12	pulmonary_embolism	45919	3	3	Blood Gas	\N
9322	Jason Hom	11	pulmonary_embolism	45919	5	5	\N	\N
9323	Jonathan Chen	11	pulmonary_embolism	45919	5	4	Blood Gas	\N
9324	Lisa Shieh	11	pulmonary_embolism	45919	5	3	\N	\N
9325	Panel Consensus	11	pulmonary_embolism	45919	5	\N	\N	\N
9465	Panel Average	11	pulmonary_embolism	45919	4	\N	\N	\N
9853	Andre Kumar	11	pulmonary_embolism	45919	3	4	Blood Gas	\N
11448	Jonathan Chen	10	pulmonary_embolism	44439	0	2	IVF	\N
8060	Jason Hom	10	pulmonary_embolism	45793	10	5	\N	\N
8061	Panel Consensus	10	pulmonary_embolism	45793	10	\N	\N	\N
8856	Panel Average	10	pulmonary_embolism	45793	6	\N	\N	\N
9326	Lisa Shieh	10	pulmonary_embolism	45793	5	3	\N	\N
9854	Jonathan Chen	10	pulmonary_embolism	45793	3	2	CBC	\N
10165	Andre Kumar	10	pulmonary_embolism	45793	2	3	CBC	\N
11267	Jonathan Chen	12	pulmonary_embolism	45793	3	2	CBC	\N
8062	Jason Hom	11	pulmonary_embolism	45793	10	5	\N	\N
8063	Panel Consensus	11	pulmonary_embolism	45793	10	\N	\N	\N
8806	Panel Average	11	pulmonary_embolism	45793	6	\N	\N	\N
9327	Lisa Shieh	11	pulmonary_embolism	45793	5	3	\N	\N
9855	Andre Kumar	11	pulmonary_embolism	45793	3	2	CBC	\N
9856	Jonathan Chen	11	pulmonary_embolism	45793	3	2	CBC	\N
11305	Jonathan Chen	8	pulmonary_embolism	45793	3	2	CBC	\N
8064	Jason Hom	10	pulmonary_embolism	45788	10	5	\N	\N
8065	Panel Consensus	10	pulmonary_embolism	45788	10	\N	\N	\N
8807	Panel Average	10	pulmonary_embolism	45788	6	\N	\N	\N
9328	Lisa Shieh	10	pulmonary_embolism	45788	5	3	\N	\N
9857	Andre Kumar	10	pulmonary_embolism	45788	3	3	CBC	\N
9858	Jonathan Chen	10	pulmonary_embolism	45788	3	2	CBC	\N
8066	Jason Hom	11	pulmonary_embolism	45788	10	5	\N	\N
8067	Panel Consensus	11	pulmonary_embolism	45788	10	\N	\N	\N
8808	Panel Average	11	pulmonary_embolism	45788	6	\N	\N	\N
9329	Lisa Shieh	11	pulmonary_embolism	45788	5	3	\N	\N
9859	Andre Kumar	11	pulmonary_embolism	45788	3	2	CBC	\N
9860	Jonathan Chen	11	pulmonary_embolism	45788	3	2	CBC	\N
11255	Jonathan Chen	8	pulmonary_embolism	45788	3	2	CBC	\N
8068	Jason Hom	10	pulmonary_embolism	35733	10	5	\N	\N
8809	Panel Average	10	pulmonary_embolism	35733	6	\N	\N	\N
8810	Panel Consensus	10	pulmonary_embolism	35733	6	\N	\N	\N
9330	Lisa Shieh	10	pulmonary_embolism	35733	5	3	\N	\N
9861	Andre Kumar	10	pulmonary_embolism	35733	3	4	Antibiotics	\N
10865	Jonathan Chen	10	pulmonary_embolism	35733	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
8069	Jason Hom	11	pulmonary_embolism	35733	10	5	\N	\N
8811	Panel Average	11	pulmonary_embolism	35733	6	\N	\N	\N
8812	Panel Consensus	11	pulmonary_embolism	35733	6	\N	\N	\N
9331	Lisa Shieh	11	pulmonary_embolism	35733	5	3	\N	\N
9862	Andre Kumar	11	pulmonary_embolism	35733	3	2	Antibiotics	\N
10866	Jonathan Chen	11	pulmonary_embolism	35733	0	2	\N	Shortness of breath, but no specific pneumonia? But maybe reasonable guess when CXR shows opacity (even though it's supposed to be cancer)
11377	Jonathan Chen	11	pulmonary_embolism	45892	0	3	\N	Superceded by troponin if needed at all
9863	Lisa Shieh	10	pulmonary_embolism	49251	3	3	\N	\N
10166	Andre Kumar	10	pulmonary_embolism	49251	2	3	Consult	\N
10228	Panel Average	10	pulmonary_embolism	49251	2	\N	\N	\N
10867	Jason Hom	10	pulmonary_embolism	49251	0	5	\N	\N
10868	Jonathan Chen	10	pulmonary_embolism	49251	0	3	\N	\N
10869	Panel Consensus	10	pulmonary_embolism	49251	0	\N	\N	\N
9864	Andre Kumar	11	pulmonary_embolism	49251	3	2	Consult	\N
9865	Lisa Shieh	11	pulmonary_embolism	49251	3	3	\N	\N
10167	Panel Average	11	pulmonary_embolism	49251	2	\N	\N	\N
10870	Jason Hom	11	pulmonary_embolism	49251	0	5	\N	\N
10871	Jonathan Chen	11	pulmonary_embolism	49251	0	3	\N	\N
10872	Panel Consensus	11	pulmonary_embolism	49251	0	\N	\N	\N
8070	Jason Hom	10	pulmonary_embolism	65695	10	5	\N	\N
8857	Panel Average	10	pulmonary_embolism	65695	6	\N	\N	\N
9332	Lisa Shieh	10	pulmonary_embolism	65695	5	3	\N	\N
9333	Panel Consensus	10	pulmonary_embolism	65695	5	\N	\N	\N
10168	Andre Kumar	10	pulmonary_embolism	65695	2	3	Consult	\N
10873	Jonathan Chen	10	pulmonary_embolism	65695	0	3	\N	\N
8071	Jason Hom	11	pulmonary_embolism	65695	10	5	\N	\N
8813	Panel Average	11	pulmonary_embolism	65695	6	\N	\N	\N
9334	Lisa Shieh	11	pulmonary_embolism	65695	5	3	\N	\N
9335	Panel Consensus	11	pulmonary_embolism	65695	5	\N	\N	\N
9866	Andre Kumar	11	pulmonary_embolism	65695	3	2	Consult	\N
10874	Jonathan Chen	11	pulmonary_embolism	65695	0	3	\N	\N
10353	Andre Kumar	8	pulmonary_embolism	65695	1	5	Consult	\N
10354	Panel Average	8	pulmonary_embolism	65695	1	\N	\N	\N
11293	Jonathan Chen	10	pulmonary_embolism	61323	0	4	\N	Consult
8072	Jason Hom	12	pulmonary_embolism	61323	10	5	\N	\N
8628	Lisa Shieh	12	pulmonary_embolism	61323	7	3	\N	\N
8692	Panel Average	12	pulmonary_embolism	61323	6	\N	\N	\N
8814	Panel Consensus	12	pulmonary_embolism	61323	6	\N	\N	\N
10169	Andre Kumar	12	pulmonary_embolism	61323	2	2	Consult	\N
10875	Jonathan Chen	12	pulmonary_embolism	61323	0	3	\N	\N
11259	Jonathan Chen	11	pulmonary_embolism	61323	0	4	\N	Consult
11284	Jonathan Chen	12	pulmonary_embolism	48502	2	2	Biopsy	Consult, but maybe thinking about IR procedure. Not necessary for initial PE treatment, but maybe thinking about biopsy already
8073	Jason Hom	10	pulmonary_embolism	49207	10	5	\N	\N
9336	Panel Average	10	pulmonary_embolism	49207	5	\N	\N	\N
9337	Panel Consensus	10	pulmonary_embolism	49207	5	\N	\N	\N
9867	Lisa Shieh	10	pulmonary_embolism	49207	3	3	\N	\N
10170	Andre Kumar	10	pulmonary_embolism	49207	2	3	Consult	\N
10876	Jonathan Chen	10	pulmonary_embolism	49207	0	3	\N	\N
11456	Jonathan Chen	12	pulmonary_embolism	49207	0	4	\N	Consult
9868	Andre Kumar	11	pulmonary_embolism	49207	3	2	Consult	\N
9869	Panel Average	11	pulmonary_embolism	49207	3	\N	\N	\N
8074	Jason Hom	11	pulmonary_embolism	49228	10	5	\N	\N
9615	Panel Average	11	pulmonary_embolism	49228	3	\N	\N	\N
9870	Panel Consensus	11	pulmonary_embolism	49228	3	\N	\N	\N
10877	Andre Kumar	11	pulmonary_embolism	49228	0	5	Consult	\N
10878	Jonathan Chen	11	pulmonary_embolism	49228	0	3	\N	\N
10879	Lisa Shieh	11	pulmonary_embolism	49228	0	3	\N	\N
8075	Jason Hom	8	pulmonary_embolism	49228	10	5	\N	\N
9616	Panel Average	8	pulmonary_embolism	49228	3	\N	\N	\N
9871	Panel Consensus	8	pulmonary_embolism	49228	3	\N	\N	\N
10880	Andre Kumar	8	pulmonary_embolism	49228	0	5	Consult	\N
10881	Jonathan Chen	8	pulmonary_embolism	49228	0	3	\N	\N
10882	Lisa Shieh	8	pulmonary_embolism	49228	0	3	\N	\N
11451	Jonathan Chen	11	pulmonary_embolism	50509	0	4	\N	Consult
8076	Andre Kumar	10	pulmonary_embolism	48522	10	4	Imaging	\N
8077	Lisa Shieh	10	pulmonary_embolism	48522	10	5	\N	\N
8078	Panel Consensus	10	pulmonary_embolism	48522	10	\N	\N	\N
8417	Jonathan Chen	10	pulmonary_embolism	48522	8	4	CT Chest	\N
9338	Panel Average	10	pulmonary_embolism	48522	5	\N	\N	\N
11169	Jason Hom	10	pulmonary_embolism	48522	-5	5	\N	\N
8079	Panel Consensus	11	pulmonary_embolism	48522	10	\N	\N	\N
8418	Andre Kumar	11	pulmonary_embolism	48522	8	5	Imaging	Less points for delaying scan?
8419	Jonathan Chen	11	pulmonary_embolism	48522	8	4	CT Chest	\N
8629	Lisa Shieh	11	pulmonary_embolism	48522	7	5	late	\N
9617	Panel Average	11	pulmonary_embolism	48522	3	\N	\N	\N
11170	Jason Hom	11	pulmonary_embolism	48522	-5	5	\N	\N
8815	Jonathan Chen	11	pulmonary_embolism	49073	6	4	CT Chest	This is without contrast, so isn't really the right way to search for PE. Is more for the mass/lung
10883	Andre Kumar	11	pulmonary_embolism	49073	0	4	IMaging	won't capture PE
10884	Jason Hom	11	pulmonary_embolism	49073	0	5	\N	\N
10885	Lisa Shieh	11	pulmonary_embolism	49073	0	3	need contrast	\N
10886	Panel Average	11	pulmonary_embolism	49073	0	\N	\N	\N
10887	Panel Consensus	11	pulmonary_embolism	49073	0	\N	\N	\N
8080	Lisa Shieh	10	pulmonary_embolism	45762	10	5	\N	\N
8420	Jonathan Chen	10	pulmonary_embolism	45762	8	4	CT Chest	\N
8466	Panel Average	10	pulmonary_embolism	45762	7	\N	\N	\N
8630	Andre Kumar	10	pulmonary_embolism	45762	7	4	Imaging	\N
8631	Panel Consensus	10	pulmonary_embolism	45762	7	\N	\N	\N
9339	Jason Hom	10	pulmonary_embolism	45762	5	5	\N	\N
8081	Lisa Shieh	11	pulmonary_embolism	45762	10	5	\N	\N
8421	Andre Kumar	11	pulmonary_embolism	45762	8	4	IMaging	\N
8422	Jonathan Chen	11	pulmonary_embolism	45762	8	4	CT Chest	\N
8447	Panel Average	11	pulmonary_embolism	45762	8	\N	\N	\N
8632	Panel Consensus	11	pulmonary_embolism	45762	7	\N	\N	\N
9340	Jason Hom	11	pulmonary_embolism	45762	5	5	\N	\N
8082	Jason Hom	10	pulmonary_embolism	48676	10	5	\N	\N
8083	Lisa Shieh	10	pulmonary_embolism	48676	10	3	\N	\N
8084	Panel Consensus	10	pulmonary_embolism	48676	10	\N	\N	\N
8235	Panel Average	10	pulmonary_embolism	48676	9	\N	\N	\N
8423	Andre Kumar	10	pulmonary_embolism	48676	8	4	Imaging	\N
8424	Jonathan Chen	10	pulmonary_embolism	48676	8	4	CT Chest	\N
8085	Jason Hom	11	pulmonary_embolism	48676	10	5	\N	\N
8086	Panel Consensus	11	pulmonary_embolism	48676	10	\N	\N	\N
8330	Panel Average	11	pulmonary_embolism	48676	8	\N	\N	\N
8425	Andre Kumar	11	pulmonary_embolism	48676	8	4	Imaging	\N
8426	Jonathan Chen	11	pulmonary_embolism	48676	8	4	CT Chest	\N
8633	Lisa Shieh	11	pulmonary_embolism	48676	7	3	\N	\N
8816	Andre Kumar	10	pulmonary_embolism	48871	6	3	D-dimer	\N
8878	Panel Average	10	pulmonary_embolism	48871	5	\N	\N	\N
9341	Jason Hom	10	pulmonary_embolism	48871	5	5	\N	\N
9342	Lisa Shieh	10	pulmonary_embolism	48871	5	3	\N	\N
9343	Panel Consensus	10	pulmonary_embolism	48871	5	\N	\N	\N
10171	Jonathan Chen	10	pulmonary_embolism	48871	2	3	D-Dimer	\N
9344	Andre Kumar	11	pulmonary_embolism	48871	5	2	D-dimer	\N
9345	Panel Consensus	11	pulmonary_embolism	48871	5	\N	\N	\N
9872	Lisa Shieh	11	pulmonary_embolism	48871	3	3	\N	\N
9923	Panel Average	11	pulmonary_embolism	48871	3	\N	\N	\N
10172	Jonathan Chen	11	pulmonary_embolism	48871	2	3	D-Dimer	\N
10888	Jason Hom	11	pulmonary_embolism	48871	0	5	\N	\N
8817	Andre Kumar	10	pulmonary_embolism	48532	6	3	D-dimer	\N
8879	Panel Average	10	pulmonary_embolism	48532	5	\N	\N	\N
9346	Jason Hom	10	pulmonary_embolism	48532	5	5	\N	\N
9347	Lisa Shieh	10	pulmonary_embolism	48532	5	3	\N	\N
9348	Panel Consensus	10	pulmonary_embolism	48532	5	\N	\N	\N
10173	Jonathan Chen	10	pulmonary_embolism	48532	2	3	D-Dimer	D-Dimer okay to screen, but have enough data to go straight to CT PE
9349	Andre Kumar	11	pulmonary_embolism	48532	5	2	D-dimer	\N
9350	Panel Consensus	11	pulmonary_embolism	48532	5	\N	\N	\N
9873	Lisa Shieh	11	pulmonary_embolism	48532	3	3	\N	\N
9924	Panel Average	11	pulmonary_embolism	48532	3	\N	\N	\N
10174	Jonathan Chen	11	pulmonary_embolism	48532	2	3	D-Dimer	\N
10889	Jason Hom	11	pulmonary_embolism	48532	0	5	\N	\N
11247	Jonathan Chen	10	pulmonary_embolism	44017	5	4	Corticosteroids	Main issue is PE, but could reasonably say it's triggering a COPD exacerbation as well
9874	Lisa Shieh	10	pulmonary_embolism	45811	3	3	\N	\N
10175	Andre Kumar	10	pulmonary_embolism	45811	2	2	Diet	\N
10176	Panel Consensus	10	pulmonary_embolism	45811	2	\N	\N	\N
10229	Panel Average	10	pulmonary_embolism	45811	2	\N	\N	\N
10890	Jason Hom	10	pulmonary_embolism	45811	0	5	\N	\N
10891	Jonathan Chen	10	pulmonary_embolism	45811	0	2	\N	\N
8087	Jason Hom	12	pulmonary_embolism	45811	10	5	\N	\N
8858	Panel Average	12	pulmonary_embolism	45811	6	\N	\N	\N
9351	Lisa Shieh	12	pulmonary_embolism	45811	5	3	\N	\N
10177	Andre Kumar	12	pulmonary_embolism	45811	2	2	Diet	\N
10178	Panel Consensus	12	pulmonary_embolism	45811	2	\N	\N	\N
10892	Jonathan Chen	12	pulmonary_embolism	45811	0	2	\N	\N
9875	Andre Kumar	11	pulmonary_embolism	45811	3	1	Diet	\N
9876	Panel Average	11	pulmonary_embolism	45811	3	\N	\N	\N
8088	Jason Hom	8	pulmonary_embolism	46008	10	5	\N	\N
9466	Panel Average	8	pulmonary_embolism	46008	4	\N	\N	\N
9557	Panel Consensus	8	pulmonary_embolism	46008	4	\N	\N	\N
9877	Lisa Shieh	8	pulmonary_embolism	46008	3	3	\N	\N
10893	Andre Kumar	8	pulmonary_embolism	46008	0	3	Diet	\N
10894	Jonathan Chen	8	pulmonary_embolism	46008	0	2	\N	\N
8089	Jason Hom	10	pulmonary_embolism	49054	10	5	\N	\N
9352	Panel Consensus	10	pulmonary_embolism	49054	5	\N	\N	\N
9439	Panel Average	10	pulmonary_embolism	49054	5	\N	\N	\N
9878	Lisa Shieh	10	pulmonary_embolism	49054	3	3	\N	\N
10355	Andre Kumar	10	pulmonary_embolism	49054	1	1	Isolation	\N
10356	Jonathan Chen	10	pulmonary_embolism	49054	1	2	\N	\N
8090	Jason Hom	10	pulmonary_embolism	45866	10	5	\N	\N
8634	Lisa Shieh	10	pulmonary_embolism	45866	7	3	\N	\N
8635	Panel Average	10	pulmonary_embolism	45866	7	\N	\N	\N
8636	Panel Consensus	10	pulmonary_embolism	45866	7	\N	\N	\N
8818	Jonathan Chen	10	pulmonary_embolism	45866	6	4	\N	\N
9558	Andre Kumar	10	pulmonary_embolism	45866	4	4	ECG + Monitoring	\N
11234	Jonathan Chen	12	pulmonary_embolism	45866	6	4	\N	\N
8091	Jason Hom	11	pulmonary_embolism	45866	10	5	\N	\N
8637	Lisa Shieh	11	pulmonary_embolism	45866	7	3	\N	\N
8638	Panel Average	11	pulmonary_embolism	45866	7	\N	\N	\N
8639	Panel Consensus	11	pulmonary_embolism	45866	7	\N	\N	\N
8819	Jonathan Chen	11	pulmonary_embolism	45866	6	4	\N	\N
9559	Andre Kumar	11	pulmonary_embolism	45866	4	2	ECG + Monitoring	\N
11388	Jonathan Chen	10	pulmonary_embolism	62176	4	2	Echo	\N
11411	Jonathan Chen	11	pulmonary_embolism	62176	4	2	Echo	\N
8092	Jason Hom	10	pulmonary_embolism	61832	10	5	\N	\N
8820	Panel Average	10	pulmonary_embolism	61832	6	\N	\N	\N
8821	Panel Consensus	10	pulmonary_embolism	61832	6	\N	\N	\N
9353	Lisa Shieh	10	pulmonary_embolism	61832	5	3	\N	\N
9560	Jonathan Chen	10	pulmonary_embolism	61832	4	2	Echo	\N
9879	Andre Kumar	10	pulmonary_embolism	61832	3	4	Imaging	\N
8093	Jason Hom	11	pulmonary_embolism	61832	10	5	\N	\N
8640	Lisa Shieh	11	pulmonary_embolism	61832	7	3	\N	\N
8641	Panel Average	11	pulmonary_embolism	61832	7	\N	\N	\N
8822	Panel Consensus	11	pulmonary_embolism	61832	6	\N	\N	\N
9561	Andre Kumar	11	pulmonary_embolism	61832	4	2	Imaging	\N
9562	Jonathan Chen	11	pulmonary_embolism	61832	4	2	Echo	\N
8094	Jason Hom	8	pulmonary_embolism	61832	10	5	\N	\N
8693	Panel Average	8	pulmonary_embolism	61832	6	\N	\N	\N
8823	Panel Consensus	8	pulmonary_embolism	61832	6	\N	\N	\N
9354	Lisa Shieh	8	pulmonary_embolism	61832	5	3	\N	\N
9563	Andre Kumar	8	pulmonary_embolism	61832	4	4	Imaging	\N
9564	Jonathan Chen	8	pulmonary_embolism	61832	4	2	Echo	\N
11246	Jonathan Chen	10	pulmonary_embolism	46160	0	4	\N	Process
11266	Jonathan Chen	11	pulmonary_embolism	46160	0	4	\N	Process
8095	Andre Kumar	11	pulmonary_embolism	44250	10	5	Anticoagulation	\N
8096	Jason Hom	11	pulmonary_embolism	44250	10	5	\N	\N
7515	Jason Hom	40	atrial_fibrillation	45977	10	4	\N	\N
7516	Jason Hom	40	atrial_fibrillation	45887	10	5	\N	\N
7517	Jason Hom	40	atrial_fibrillation	45827	10	5	\N	\N
7518	Lisa Shieh	40	atrial_fibrillation	45827	10	5	\N	\N
7519	Jason Hom	40	atrial_fibrillation	45793	10	5	\N	\N
7520	Jason Hom	40	atrial_fibrillation	45788	10	5	\N	\N
7521	Jason Hom	43	atrial_fibrillation	50400	10	5	\N	\N
7522	Jason Hom	40	atrial_fibrillation	49251	10	5	\N	\N
7523	Jason Hom	43	atrial_fibrillation	49251	10	5	\N	\N
7524	Jason Hom	43	atrial_fibrillation	61323	10	5	\N	\N
10958	Lisa Shieh	11	pulmonary_embolism	62023	0	3	\N	\N
7525	Andre Kumar	40	atrial_fibrillation	-100	10	5	Cardioversion	\N
7526	Jason Hom	40	atrial_fibrillation	-100	10	5	\N	\N
7527	Jonathan Chen	40	atrial_fibrillation	-100	10	5	\N	\N
7528	Lisa Shieh	40	atrial_fibrillation	-100	10	5	\N	\N
7529	Panel Average	40	atrial_fibrillation	-100	10	\N	\N	\N
7530	Panel Consensus	40	atrial_fibrillation	-100	10	\N	\N	\N
7531	Jason Hom	43	atrial_fibrillation	-100	10	5	\N	\N
7532	Jonathan Chen	43	atrial_fibrillation	-100	10	5	\N	\N
7533	Lisa Shieh	43	atrial_fibrillation	-100	10	5	\N	\N
7534	Panel Consensus	43	atrial_fibrillation	-100	10	\N	\N	\N
7535	Jason Hom	40	atrial_fibrillation	45811	10	5	\N	\N
7536	Lisa Shieh	43	atrial_fibrillation	45811	10	5	\N	\N
7537	Jason Hom	40	atrial_fibrillation	45866	10	5	\N	\N
7538	Jonathan Chen	40	atrial_fibrillation	45866	10	5	\N	\N
7539	Lisa Shieh	40	atrial_fibrillation	45866	10	5	\N	\N
7540	Jonathan Chen	41	atrial_fibrillation	45866	10	5	\N	\N
7541	Jason Hom	41	atrial_fibrillation	61832	10	5	\N	\N
7542	Jason Hom	40	atrial_fibrillation	46160	10	5	\N	\N
7543	Lisa Shieh	40	atrial_fibrillation	46160	10	5	\N	\N
7544	Andre Kumar	41	atrial_fibrillation	44250	10	5	Anticoagulants	No positive points if combined wiht other anticoagulants
7545	Panel Average	41	atrial_fibrillation	44250	10	\N	\N	\N
8097	Jonathan Chen	11	pulmonary_embolism	44250	10	5	Anticoagulation	\N
8098	Lisa Shieh	11	pulmonary_embolism	44250	10	3	? Full dose	\N
8099	Panel Average	11	pulmonary_embolism	44250	10	\N	\N	\N
8100	Panel Consensus	11	pulmonary_embolism	44250	10	\N	\N	\N
10895	Andre Kumar	11	pulmonary_embolism	61978	0	5	Foley	\N
10896	Jason Hom	11	pulmonary_embolism	61978	0	5	\N	\N
10897	Jonathan Chen	11	pulmonary_embolism	61978	0	2	\N	Probably because think CHF exacerbation and going to lots of diuresis?
10993	Panel Average	11	pulmonary_embolism	61978	-2	\N	\N	\N
11171	Lisa Shieh	11	pulmonary_embolism	61978	-5	3	\N	\N
11172	Panel Consensus	11	pulmonary_embolism	61978	-5	\N	\N	\N
8101	Jason Hom	10	pulmonary_embolism	44004	10	5	\N	\N
9355	Lisa Shieh	10	pulmonary_embolism	44004	5	3	\N	\N
9467	Panel Average	10	pulmonary_embolism	44004	4	\N	\N	\N
10898	Jonathan Chen	10	pulmonary_embolism	44004	0	2	\N	Some pedal edema from chronic CHF? But not supposed to be volume overloaded
11212	Andre Kumar	43	atrial_fibrillation	44352	-10	5	Rhythm Control	\N
11213	Jason Hom	43	atrial_fibrillation	44352	-10	5	\N	\N
11214	Andre Kumar	40	atrial_fibrillation	50098	-10	5	Imaging	Delays care
11215	Andre Kumar	40	atrial_fibrillation	45983	-10	5	Imaging	Delays care
11216	Andre Kumar	40	atrial_fibrillation	49965	-10	5	Imaging	Delays care
11217	Andre Kumar	43	atrial_fibrillation	44389	-10	4	Rate Control	\N
11218	Panel Average	43	atrial_fibrillation	44389	-10	\N	\N	\N
11219	Lisa Shieh	40	atrial_fibrillation	35846	-10	3	\N	\N
11220	Andre Kumar	43	atrial_fibrillation	35846	-10	4	Rate Control	\N
11221	Jason Hom	43	atrial_fibrillation	35846	-10	5	\N	\N
11222	Jason Hom	43	atrial_fibrillation	44393	-10	5	\N	\N
11223	Andre Kumar	43	atrial_fibrillation	44251	-10	5	Ionotropes	\N
11224	Jason Hom	43	atrial_fibrillation	44251	-10	5	\N	\N
11225	Jason Hom	43	atrial_fibrillation	45963	-10	5	\N	\N
11226	Andre Kumar	43	atrial_fibrillation	44248	-10	5	Rate Control	\N
11227	Jason Hom	43	atrial_fibrillation	44248	-10	5	\N	\N
11228	Jason Hom	43	atrial_fibrillation	44004	-10	5	\N	\N
11229	Lisa Shieh	40	atrial_fibrillation	44327	-10	3	\N	\N
11230	Jason Hom	30	meningitis	44237	-10	4	\N	\N
10899	Panel Consensus	10	pulmonary_embolism	44004	0	\N	\N	\N
11067	Andre Kumar	10	pulmonary_embolism	44004	-2	4	Diuretics	\N
8102	Jason Hom	11	pulmonary_embolism	44004	10	5	\N	\N
9356	Lisa Shieh	11	pulmonary_embolism	44004	5	3	\N	\N
9468	Panel Average	11	pulmonary_embolism	44004	4	\N	\N	\N
10900	Jonathan Chen	11	pulmonary_embolism	44004	0	2	\N	Some pedal edema from chronic CHF? But not supposed to be volume overloaded
10901	Panel Consensus	11	pulmonary_embolism	44004	0	\N	\N	\N
11068	Andre Kumar	11	pulmonary_embolism	44004	-2	3	Diuretics	\N
10179	Jason Hom	11	pulmonary_embolism	45797	2	5	\N	\N
10357	Panel Consensus	11	pulmonary_embolism	45797	1	\N	\N	\N
10389	Panel Average	11	pulmonary_embolism	45797	1	\N	\N	\N
10902	Andre Kumar	11	pulmonary_embolism	45797	0	3	A1c	\N
10903	Jonathan Chen	11	pulmonary_embolism	45797	0	2	\N	\N
10904	Lisa Shieh	11	pulmonary_embolism	45797	0	3	\N	\N
11446	Jonathan Chen	10	pulmonary_embolism	46438	10	5	Anticoagulants	\N
8103	Andre Kumar	10	pulmonary_embolism	44359	10	5	Anticoagulants	\N
8104	Jonathan Chen	10	pulmonary_embolism	44359	10	5	Anticoagulation	\N
8105	Panel Consensus	10	pulmonary_embolism	44359	10	\N	\N	\N
8642	Lisa Shieh	10	pulmonary_embolism	44359	7	3	\N	\N
8859	Panel Average	10	pulmonary_embolism	44359	6	\N	\N	\N
10905	Jason Hom	10	pulmonary_embolism	44359	0	5	\N	\N
8106	Andre Kumar	11	pulmonary_embolism	44359	10	5	Anticoagulation	\N
8107	Jason Hom	11	pulmonary_embolism	44359	10	5	\N	\N
8108	Jonathan Chen	11	pulmonary_embolism	44359	10	5	Anticoagulation	\N
8109	Lisa Shieh	11	pulmonary_embolism	44359	10	5	\N	\N
8110	Panel Average	11	pulmonary_embolism	44359	10	\N	\N	\N
8111	Panel Consensus	11	pulmonary_embolism	44359	10	\N	\N	\N
11444	Jonathan Chen	10	pulmonary_embolism	46183	0	2	\N	Just count of part heparin protocol
8112	Jason Hom	11	pulmonary_embolism	46183	10	5	\N	\N
8113	Lisa Shieh	11	pulmonary_embolism	46183	10	3	\N	\N
8114	Panel Consensus	11	pulmonary_embolism	46183	10	\N	\N	\N
8448	Panel Average	11	pulmonary_embolism	46183	8	\N	\N	\N
9880	Andre Kumar	11	pulmonary_embolism	46183	3	2	Anticoagulation	\N
10906	Jonathan Chen	11	pulmonary_embolism	46183	0	2	\N	Just count of part heparin protocol
11322	Jonathan Chen	10	pulmonary_embolism	63714	0	2	\N	Just count of part heparin protocol
8649	Lisa Shieh	10	pulmonary_embolism	45830	7	3	\N	\N
11350	Jonathan Chen	11	pulmonary_embolism	63714	0	2	\N	Just count of part heparin protocol
9881	Andre Kumar	10	pulmonary_embolism	44211	3	3	Nebs	\N
9882	Panel Average	10	pulmonary_embolism	44211	3	\N	\N	\N
11308	Jonathan Chen	10	pulmonary_embolism	49301	5	4	Blood Gas	\N
8643	Panel Consensus	8	pulmonary_embolism	49301	7	\N	\N	\N
9357	Jason Hom	8	pulmonary_embolism	49301	5	5	\N	\N
9358	Jonathan Chen	8	pulmonary_embolism	49301	5	4	Blood Gas	\N
9618	Panel Average	8	pulmonary_embolism	49301	3	\N	\N	\N
9883	Lisa Shieh	8	pulmonary_embolism	49301	3	3	\N	\N
10180	Andre Kumar	8	pulmonary_embolism	49301	2	4	Blood Gass	\N
9884	Andre Kumar	10	pulmonary_embolism	46020	3	3	Blood gas	\N
9885	Panel Average	10	pulmonary_embolism	46020	3	\N	\N	\N
8115	Jason Hom	10	pulmonary_embolism	45838	10	5	\N	\N
8694	Panel Average	10	pulmonary_embolism	45838	6	\N	\N	\N
8824	Panel Consensus	10	pulmonary_embolism	45838	6	\N	\N	\N
9359	Jonathan Chen	10	pulmonary_embolism	45838	5	4	Troponin	\N
9360	Lisa Shieh	10	pulmonary_embolism	45838	5	3	\N	\N
9565	Andre Kumar	10	pulmonary_embolism	45838	4	2	Troponin	\N
8116	Jason Hom	10	pulmonary_embolism	62151	10	5	\N	\N
8880	Panel Average	10	pulmonary_embolism	62151	5	\N	\N	\N
9361	Jonathan Chen	10	pulmonary_embolism	62151	5	4	Blood Gas	\N
9362	Panel Consensus	10	pulmonary_embolism	62151	5	\N	\N	\N
9886	Andre Kumar	10	pulmonary_embolism	62151	3	2	Lactate	\N
9887	Lisa Shieh	10	pulmonary_embolism	62151	3	3	\N	\N
10358	Andre Kumar	11	pulmonary_embolism	44299	1	2	Antibiotics	\N
10359	Panel Average	11	pulmonary_embolism	44299	1	\N	\N	\N
11361	Jonathan Chen	10	pulmonary_embolism	62144	0	2	\N	Not sure?
9363	Lisa Shieh	11	pulmonary_embolism	61837	5	3	\N	\N
10230	Panel Average	11	pulmonary_embolism	61837	2	\N	\N	\N
10907	Andre Kumar	11	pulmonary_embolism	61837	0	5	Lipid Panel	\N
10908	Jason Hom	11	pulmonary_embolism	61837	0	5	\N	\N
10909	Jonathan Chen	11	pulmonary_embolism	61837	0	2	\N	\N
10910	Panel Consensus	11	pulmonary_embolism	61837	0	\N	\N	\N
11283	Jonathan Chen	10	pulmonary_embolism	44213	0	2	\N	Like asthma exacerbation treatment?
11239	Jonathan Chen	10	pulmonary_embolism	45806	0	2	\N	\N
11243	Jonathan Chen	12	pulmonary_embolism	45806	0	2	\N	\N
8117	Jason Hom	11	pulmonary_embolism	45806	10	5	\N	\N
8881	Panel Average	11	pulmonary_embolism	45806	5	\N	\N	\N
9364	Lisa Shieh	11	pulmonary_embolism	45806	5	3	\N	\N
9365	Panel Consensus	11	pulmonary_embolism	45806	5	\N	\N	\N
10360	Andre Kumar	11	pulmonary_embolism	45806	1	4	Metabolic Panel	\N
10911	Jonathan Chen	11	pulmonary_embolism	45806	0	2	\N	\N
11346	Jonathan Chen	8	pulmonary_embolism	45806	0	2	\N	\N
8118	Jason Hom	10	pulmonary_embolism	45763	10	5	\N	\N
8119	Panel Consensus	10	pulmonary_embolism	45763	10	\N	\N	\N
8825	Panel Average	10	pulmonary_embolism	45763	6	\N	\N	\N
9366	Lisa Shieh	10	pulmonary_embolism	45763	5	3	\N	\N
9888	Andre Kumar	10	pulmonary_embolism	45763	3	2	MEtabolic Panel	\N
9889	Jonathan Chen	10	pulmonary_embolism	45763	3	2	Metabolic Panel	\N
8120	Jason Hom	11	pulmonary_embolism	45763	10	5	\N	\N
8121	Panel Consensus	11	pulmonary_embolism	45763	10	\N	\N	\N
8882	Panel Average	11	pulmonary_embolism	45763	5	\N	\N	\N
9367	Lisa Shieh	11	pulmonary_embolism	45763	5	3	\N	\N
9890	Jonathan Chen	11	pulmonary_embolism	45763	3	2	Metabolic Panel	\N
10361	Andre Kumar	11	pulmonary_embolism	45763	1	4	Metabolic Panel	\N
8122	Jason Hom	10	pulmonary_embolism	45771	10	5	\N	\N
8123	Panel Consensus	10	pulmonary_embolism	45771	10	\N	\N	\N
8826	Panel Average	10	pulmonary_embolism	45771	6	\N	\N	\N
9368	Lisa Shieh	10	pulmonary_embolism	45771	5	3	\N	\N
9891	Andre Kumar	10	pulmonary_embolism	45771	3	2	MEtabolic Panel	\N
9892	Jonathan Chen	10	pulmonary_embolism	45771	3	2	Metabolic Panel	\N
11352	Jonathan Chen	12	pulmonary_embolism	45771	3	2	Metabolic Panel	\N
8124	Jason Hom	11	pulmonary_embolism	45771	10	5	\N	\N
8125	Panel Consensus	11	pulmonary_embolism	45771	10	\N	\N	\N
8883	Panel Average	11	pulmonary_embolism	45771	5	\N	\N	\N
9369	Lisa Shieh	11	pulmonary_embolism	45771	5	3	\N	\N
9893	Jonathan Chen	11	pulmonary_embolism	45771	3	2	Metabolic Panel	\N
10362	Andre Kumar	11	pulmonary_embolism	45771	1	4	Metabolic Panel	\N
11251	Jonathan Chen	8	pulmonary_embolism	45771	3	2	Metabolic Panel	\N
8644	Lisa Shieh	10	pulmonary_embolism	44586	7	3	\N	\N
9370	Jason Hom	10	pulmonary_embolism	44586	5	5	\N	\N
9371	Jonathan Chen	10	pulmonary_embolism	44586	5	4	Corticosteroids	\N
9372	Panel Consensus	10	pulmonary_embolism	44586	5	\N	\N	\N
10181	Andre Kumar	10	pulmonary_embolism	44586	2	3	Steroids	\N
9373	Jason Hom	11	pulmonary_embolism	44586	5	5	\N	\N
9374	Jonathan Chen	11	pulmonary_embolism	44586	5	4	Corticosteroids	\N
9375	Lisa Shieh	11	pulmonary_embolism	44586	5	3	\N	\N
9376	Panel Consensus	11	pulmonary_embolism	44586	5	\N	\N	\N
9593	Panel Average	11	pulmonary_embolism	44586	4	\N	\N	\N
10363	Andre Kumar	11	pulmonary_embolism	44586	1	4	Steroids	\N
8126	Jason Hom	11	pulmonary_embolism	45792	10	5	\N	\N
9469	Panel Average	11	pulmonary_embolism	45792	4	\N	\N	\N
9566	Panel Consensus	11	pulmonary_embolism	45792	4	\N	\N	\N
9894	Lisa Shieh	11	pulmonary_embolism	45792	3	3	\N	\N
10912	Andre Kumar	11	pulmonary_embolism	45792	0	4	MRSA	\N
10913	Jonathan Chen	11	pulmonary_embolism	45792	0	2	\N	\N
8127	Jason Hom	11	pulmonary_embolism	44228	10	5	\N	\N
9470	Panel Average	11	pulmonary_embolism	44228	4	\N	\N	\N
9567	Panel Consensus	11	pulmonary_embolism	44228	4	\N	\N	\N
9895	Lisa Shieh	11	pulmonary_embolism	44228	3	3	\N	\N
10182	Jonathan Chen	11	pulmonary_embolism	44228	2	2	Nicotine replacement	\N
10914	Andre Kumar	11	pulmonary_embolism	44228	0	4	Nicotine	\N
9896	Lisa Shieh	11	pulmonary_embolism	48628	3	3	\N	\N
10364	Panel Average	11	pulmonary_embolism	48628	1	\N	\N	\N
10915	Andre Kumar	11	pulmonary_embolism	48628	0	4	Anticoagulation	\N
10916	Jason Hom	11	pulmonary_embolism	48628	0	5	\N	\N
10917	Jonathan Chen	11	pulmonary_embolism	48628	0	2	\N	\N
10918	Panel Consensus	11	pulmonary_embolism	48628	0	\N	\N	\N
10919	Andre Kumar	11	pulmonary_embolism	46081	0	4	Anticoagulation	\N
10920	Jason Hom	11	pulmonary_embolism	46081	0	5	\N	\N
10921	Jonathan Chen	11	pulmonary_embolism	46081	0	2	\N	\N
10922	Lisa Shieh	11	pulmonary_embolism	46081	0	3	\N	\N
10923	Panel Average	11	pulmonary_embolism	46081	0	\N	\N	\N
10924	Panel Consensus	11	pulmonary_embolism	46081	0	\N	\N	\N
8128	Jonathan Chen	10	pulmonary_embolism	50235	10	5	Oxygen	\N
9377	Lisa Shieh	10	pulmonary_embolism	50235	5	3	\N	\N
10365	Panel Average	10	pulmonary_embolism	50235	1	\N	\N	\N
10925	Jason Hom	10	pulmonary_embolism	50235	0	4	\N	\N
10926	Panel Consensus	10	pulmonary_embolism	50235	0	\N	\N	\N
11069	Andre Kumar	10	pulmonary_embolism	50235	-2	1	NIPPV	\N
8129	Jason Hom	12	pulmonary_embolism	50235	10	5	\N	\N
8130	Jonathan Chen	12	pulmonary_embolism	50235	10	5	Oxygen	\N
9378	Lisa Shieh	12	pulmonary_embolism	50235	5	3	\N	\N
9568	Panel Average	12	pulmonary_embolism	50235	4	\N	\N	\N
10927	Panel Consensus	12	pulmonary_embolism	50235	0	\N	\N	\N
11095	Andre Kumar	12	pulmonary_embolism	50235	-3	1	NIPPV	\N
8131	Jason Hom	10	pulmonary_embolism	45853	10	5	\N	\N
8827	Panel Average	10	pulmonary_embolism	45853	6	\N	\N	\N
8828	Panel Consensus	10	pulmonary_embolism	45853	6	\N	\N	\N
9379	Lisa Shieh	10	pulmonary_embolism	45853	5	3	\N	\N
9897	Andre Kumar	10	pulmonary_embolism	45853	3	1	BNP	\N
9898	Jonathan Chen	10	pulmonary_embolism	45853	3	4	\N	\N
8132	Jason Hom	11	pulmonary_embolism	45853	10	5	\N	\N
8829	Panel Consensus	11	pulmonary_embolism	45853	6	\N	\N	\N
8860	Panel Average	11	pulmonary_embolism	45853	6	\N	\N	\N
9380	Lisa Shieh	11	pulmonary_embolism	45853	5	3	\N	\N
9899	Jonathan Chen	11	pulmonary_embolism	45853	3	4	\N	\N
10183	Andre Kumar	11	pulmonary_embolism	45853	2	4	BNP	\N
11359	Jonathan Chen	10	pulmonary_embolism	45750	2	3	\N	Process?
11314	Jonathan Chen	11	pulmonary_embolism	45787	0	2	\N	Process
11416	Jonathan Chen	10	pulmonary_embolism	51290	10	5	Oxygen	\N
8133	Andre Kumar	11	pulmonary_embolism	51290	10	5	Oxygen	\N
8134	Jason Hom	11	pulmonary_embolism	51290	10	5	\N	\N
8135	Jonathan Chen	11	pulmonary_embolism	51290	10	5	Oxygen	\N
8136	Panel Consensus	11	pulmonary_embolism	51290	10	\N	\N	\N
8331	Panel Average	11	pulmonary_embolism	51290	8	\N	\N	\N
9381	Lisa Shieh	11	pulmonary_embolism	51290	5	3	\N	\N
8137	Andre Kumar	10	pulmonary_embolism	45864	10	5	Oxygen	only 1 time award for oxygen
8138	Jason Hom	10	pulmonary_embolism	45864	10	5	\N	\N
8139	Jonathan Chen	10	pulmonary_embolism	45864	10	5	Oxygen	\N
8140	Lisa Shieh	10	pulmonary_embolism	45864	10	5	\N	\N
8141	Panel Average	10	pulmonary_embolism	45864	10	\N	\N	\N
8142	Panel Consensus	10	pulmonary_embolism	45864	10	\N	\N	\N
8143	Jason Hom	12	pulmonary_embolism	45864	10	5	\N	\N
8144	Jonathan Chen	12	pulmonary_embolism	45864	10	5	Oxygen	\N
8145	Lisa Shieh	12	pulmonary_embolism	45864	10	5	\N	\N
8146	Panel Consensus	12	pulmonary_embolism	45864	10	\N	\N	\N
8220	Panel Average	12	pulmonary_embolism	45864	10	\N	\N	\N
8288	Andre Kumar	12	pulmonary_embolism	45864	9	4	Oxygen	less points for delaying O2?
8147	Andre Kumar	10	pulmonary_embolism	48822	10	5	Oxygen	\N
8148	Jason Hom	10	pulmonary_embolism	48822	10	5	\N	\N
8149	Jonathan Chen	10	pulmonary_embolism	48822	10	5	Oxygen	\N
8150	Lisa Shieh	10	pulmonary_embolism	48822	10	5	\N	\N
8151	Panel Average	10	pulmonary_embolism	48822	10	\N	\N	\N
8152	Panel Consensus	10	pulmonary_embolism	48822	10	\N	\N	\N
8153	Jason Hom	12	pulmonary_embolism	48822	10	5	\N	\N
8154	Jonathan Chen	12	pulmonary_embolism	48822	10	5	Oxygen	\N
8155	Lisa Shieh	12	pulmonary_embolism	48822	10	5	\N	\N
8156	Panel Consensus	12	pulmonary_embolism	48822	10	\N	\N	\N
8221	Panel Average	12	pulmonary_embolism	48822	10	\N	\N	\N
8289	Andre Kumar	12	pulmonary_embolism	48822	9	4	Oxygen	less points for delaying O2?
8157	Andre Kumar	10	pulmonary_embolism	45900	10	5	Oxygen	\N
8158	Jason Hom	10	pulmonary_embolism	45900	10	5	\N	\N
8159	Jonathan Chen	10	pulmonary_embolism	45900	10	5	Oxygen	\N
8160	Lisa Shieh	10	pulmonary_embolism	45900	10	5	\N	\N
8161	Panel Average	10	pulmonary_embolism	45900	10	\N	\N	\N
8162	Panel Consensus	10	pulmonary_embolism	45900	10	\N	\N	\N
8163	Jason Hom	12	pulmonary_embolism	45900	10	5	\N	\N
8164	Jonathan Chen	12	pulmonary_embolism	45900	10	5	Oxygen	\N
8165	Lisa Shieh	12	pulmonary_embolism	45900	10	5	\N	\N
8166	Panel Consensus	12	pulmonary_embolism	45900	10	\N	\N	\N
8222	Panel Average	12	pulmonary_embolism	45900	10	\N	\N	\N
8290	Andre Kumar	12	pulmonary_embolism	45900	9	4	Oxygen	less points for delaying O2?
11370	Jonathan Chen	10	pulmonary_embolism	46090	0	2	\N	Heparin protocol
8291	Lisa Shieh	11	pulmonary_embolism	46090	9	3	\N	\N
9619	Panel Average	11	pulmonary_embolism	46090	3	\N	\N	\N
10184	Panel Consensus	11	pulmonary_embolism	46090	2	\N	\N	\N
10366	Andre Kumar	11	pulmonary_embolism	46090	1	3	Anticoagulation	\N
10928	Jason Hom	11	pulmonary_embolism	46090	0	5	\N	\N
10929	Jonathan Chen	11	pulmonary_embolism	46090	0	2	\N	Heparin protocol
8167	Jason Hom	10	pulmonary_embolism	45914	10	5	\N	\N
8695	Panel Average	10	pulmonary_embolism	45914	6	\N	\N	\N
8830	Panel Consensus	10	pulmonary_embolism	45914	6	\N	\N	\N
9382	Jonathan Chen	10	pulmonary_embolism	45914	5	4	Troponin	\N
9383	Lisa Shieh	10	pulmonary_embolism	45914	5	3	\N	\N
9569	Andre Kumar	10	pulmonary_embolism	45914	4	3	Troponin	\N
9570	Andre Kumar	11	pulmonary_embolism	45914	4	3	Troponin	\N
9571	Panel Average	11	pulmonary_embolism	45914	4	\N	\N	\N
8168	Jason Hom	10	pulmonary_embolism	50773	10	5	\N	\N
8645	Panel Consensus	10	pulmonary_embolism	50773	7	\N	\N	\N
8679	Panel Average	10	pulmonary_embolism	50773	7	\N	\N	\N
9384	Andre Kumar	10	pulmonary_embolism	50773	5	5	Blood gas	\N
9385	Jonathan Chen	10	pulmonary_embolism	50773	5	4	Blood Gas	\N
9386	Lisa Shieh	10	pulmonary_embolism	50773	5	3	\N	\N
8169	Jason Hom	10	pulmonary_embolism	50503	10	5	\N	\N
9387	Jonathan Chen	10	pulmonary_embolism	50503	5	4	Blood Gas	\N
9388	Lisa Shieh	10	pulmonary_embolism	50503	5	3	\N	\N
9389	Panel Average	10	pulmonary_embolism	50503	5	\N	\N	\N
9390	Panel Consensus	10	pulmonary_embolism	50503	5	\N	\N	\N
10930	Andre Kumar	10	pulmonary_embolism	50503	0	3	Blood gas	\N
8170	Jason Hom	10	pulmonary_embolism	45955	10	5	\N	\N
9391	Jonathan Chen	10	pulmonary_embolism	45955	5	4	Blood Gas	\N
9392	Lisa Shieh	10	pulmonary_embolism	45955	5	3	\N	\N
9393	Panel Average	10	pulmonary_embolism	45955	5	\N	\N	\N
9394	Panel Consensus	10	pulmonary_embolism	45955	5	\N	\N	\N
10931	Andre Kumar	10	pulmonary_embolism	45955	0	3	Blood Gas	\N
9395	Jason Hom	11	pulmonary_embolism	45955	5	5	\N	\N
9396	Jonathan Chen	11	pulmonary_embolism	45955	5	4	Blood Gas	\N
9397	Lisa Shieh	11	pulmonary_embolism	45955	5	3	\N	\N
9398	Panel Consensus	11	pulmonary_embolism	45955	5	\N	\N	\N
9441	Panel Average	11	pulmonary_embolism	45955	5	\N	\N	\N
9572	Andre Kumar	11	pulmonary_embolism	45955	4	3	Blood Gas	\N
10932	Andre Kumar	8	pulmonary_embolism	50267	0	3	Anticoagulation	\N
10933	Jason Hom	8	pulmonary_embolism	50267	0	5	\N	\N
10934	Jonathan Chen	8	pulmonary_embolism	50267	0	2	\N	\N
10935	Lisa Shieh	8	pulmonary_embolism	50267	0	3	\N	\N
10936	Panel Average	8	pulmonary_embolism	50267	0	\N	\N	\N
10937	Panel Consensus	8	pulmonary_embolism	50267	0	\N	\N	\N
8646	Lisa Shieh	10	pulmonary_embolism	44011	7	3	\N	\N
9399	Jonathan Chen	10	pulmonary_embolism	44011	5	4	Corticosteroids	Main issue is PE, but could reasonably say it's triggering a COPD exacerbation as well
9400	Panel Consensus	10	pulmonary_embolism	44011	5	\N	\N	\N
9900	Panel Average	10	pulmonary_embolism	44011	3	\N	\N	\N
10185	Andre Kumar	10	pulmonary_embolism	44011	2	3	Steroids	\N
10938	Jason Hom	10	pulmonary_embolism	44011	0	5	\N	\N
9401	Jonathan Chen	11	pulmonary_embolism	44011	5	4	Corticosteroids	Main issue is PE, but could reasonably say it's triggering a COPD exacerbation as well
9402	Lisa Shieh	11	pulmonary_embolism	44011	5	3	\N	\N
9403	Panel Consensus	11	pulmonary_embolism	44011	5	\N	\N	\N
10186	Panel Average	11	pulmonary_embolism	44011	2	\N	\N	\N
10367	Andre Kumar	11	pulmonary_embolism	44011	1	4	Steroids	\N
10939	Jason Hom	11	pulmonary_embolism	44011	0	5	\N	\N
8171	Jason Hom	11	pulmonary_embolism	62042	10	5	\N	\N
8884	Panel Average	11	pulmonary_embolism	62042	5	\N	\N	\N
9404	Panel Consensus	11	pulmonary_embolism	62042	5	\N	\N	\N
9901	Andre Kumar	11	pulmonary_embolism	62042	3	4	Procalcitonin	\N
9902	Jonathan Chen	11	pulmonary_embolism	62042	3	3	\N	May be helpful for complex differential diagnosis
9903	Lisa Shieh	11	pulmonary_embolism	62042	3	3	\N	\N
8172	Jason Hom	10	pulmonary_embolism	45759	10	5	\N	\N
8173	Panel Consensus	10	pulmonary_embolism	45759	10	\N	\N	\N
8831	Panel Average	10	pulmonary_embolism	45759	6	\N	\N	\N
9405	Lisa Shieh	10	pulmonary_embolism	45759	5	3	\N	\N
9904	Andre Kumar	10	pulmonary_embolism	45759	3	3	Coags	\N
10940	Jonathan Chen	10	pulmonary_embolism	45759	0	2	\N	\N
8174	Jason Hom	11	pulmonary_embolism	45759	10	5	\N	\N
8175	Panel Consensus	11	pulmonary_embolism	45759	10	\N	\N	\N
8861	Panel Average	11	pulmonary_embolism	45759	6	\N	\N	\N
9406	Lisa Shieh	11	pulmonary_embolism	45759	5	3	\N	\N
10187	Andre Kumar	11	pulmonary_embolism	45759	2	2	Coagulation	\N
10941	Jonathan Chen	11	pulmonary_embolism	45759	0	2	\N	\N
8176	Jason Hom	8	pulmonary_embolism	45759	10	5	\N	\N
8177	Panel Consensus	8	pulmonary_embolism	45759	10	\N	\N	\N
8647	Lisa Shieh	8	pulmonary_embolism	45759	7	3	\N	\N
8832	Panel Average	8	pulmonary_embolism	45759	6	\N	\N	\N
10368	Andre Kumar	8	pulmonary_embolism	45759	1	4	Coags	\N
10942	Jonathan Chen	8	pulmonary_embolism	45759	0	2	\N	\N
8178	Jason Hom	11	pulmonary_embolism	45776	10	5	\N	\N
9573	Panel Consensus	11	pulmonary_embolism	45776	4	\N	\N	\N
9594	Panel Average	11	pulmonary_embolism	45776	4	\N	\N	\N
10369	Andre Kumar	11	pulmonary_embolism	45776	1	2	PT/OT	\N
10943	Jonathan Chen	11	pulmonary_embolism	45776	0	2	\N	\N
10944	Lisa Shieh	11	pulmonary_embolism	45776	0	3	\N	\N
10370	Andre Kumar	8	pulmonary_embolism	45776	1	2	PT/OT	\N
10371	Panel Average	8	pulmonary_embolism	45776	1	\N	\N	\N
10945	Andre Kumar	8	pulmonary_embolism	49268	0	2	Coags	\N
10946	Jason Hom	8	pulmonary_embolism	49268	0	5	\N	\N
10947	Jonathan Chen	8	pulmonary_embolism	49268	0	2	\N	Probably a typo, looking for PTT
10948	Lisa Shieh	8	pulmonary_embolism	49268	0	3	\N	\N
10949	Panel Average	8	pulmonary_embolism	49268	0	\N	\N	\N
10950	Panel Consensus	8	pulmonary_embolism	49268	0	\N	\N	\N
11469	Jonathan Chen	10	pulmonary_embolism	45770	0	2	\N	\N
11470	Jonathan Chen	12	pulmonary_embolism	45770	0	2	\N	\N
8179	Jason Hom	11	pulmonary_embolism	45770	10	5	\N	\N
8180	Panel Consensus	11	pulmonary_embolism	45770	10	\N	\N	\N
8885	Panel Average	11	pulmonary_embolism	45770	5	\N	\N	\N
9407	Lisa Shieh	11	pulmonary_embolism	45770	5	3	\N	\N
10372	Andre Kumar	11	pulmonary_embolism	45770	1	2	Coags	\N
10951	Jonathan Chen	11	pulmonary_embolism	45770	0	2	\N	\N
8181	Jason Hom	8	pulmonary_embolism	45770	10	5	\N	\N
8182	Panel Consensus	8	pulmonary_embolism	45770	10	\N	\N	\N
8648	Lisa Shieh	8	pulmonary_embolism	45770	7	3	\N	\N
8833	Panel Average	8	pulmonary_embolism	45770	6	\N	\N	\N
10373	Andre Kumar	8	pulmonary_embolism	45770	1	2	Coags	\N
10952	Jonathan Chen	8	pulmonary_embolism	45770	0	2	\N	\N
11459	Jonathan Chen	11	pulmonary_embolism	63730	0	2	\N	Not for acute TB even if that was the diagnosis?
8183	Jason Hom	8	pulmonary_embolism	62175	10	5	\N	\N
9471	Panel Average	8	pulmonary_embolism	62175	4	\N	\N	\N
9574	Panel Consensus	8	pulmonary_embolism	62175	4	\N	\N	\N
9905	Lisa Shieh	8	pulmonary_embolism	62175	3	3	\N	\N
10188	Jonathan Chen	8	pulmonary_embolism	62175	2	2	Biopsy	Referral for biopsy?
10953	Andre Kumar	8	pulmonary_embolism	62175	0	1	Consults	\N
8184	Jason Hom	12	pulmonary_embolism	45857	10	5	\N	\N
8834	Panel Consensus	12	pulmonary_embolism	45857	6	\N	\N	\N
8862	Panel Average	12	pulmonary_embolism	45857	6	\N	\N	\N
9408	Lisa Shieh	12	pulmonary_embolism	45857	5	3	\N	\N
10189	Andre Kumar	12	pulmonary_embolism	45857	2	1	Nebs	\N
10190	Jonathan Chen	12	pulmonary_embolism	45857	2	4	Nebs	\N
8650	Panel Average	10	pulmonary_embolism	45830	7	\N	\N	\N
8651	Panel Consensus	10	pulmonary_embolism	45830	7	\N	\N	\N
9575	Andre Kumar	10	pulmonary_embolism	45830	4	2	Nebs	\N
10191	Jonathan Chen	10	pulmonary_embolism	45830	2	4	Nebs	\N
8186	Jason Hom	12	pulmonary_embolism	45830	10	5	\N	\N
8652	Lisa Shieh	12	pulmonary_embolism	45830	7	3	\N	\N
8653	Panel Consensus	12	pulmonary_embolism	45830	7	\N	\N	\N
8696	Panel Average	12	pulmonary_embolism	45830	6	\N	\N	\N
10192	Andre Kumar	12	pulmonary_embolism	45830	2	1	Nebs	\N
10193	Jonathan Chen	12	pulmonary_embolism	45830	2	4	Nebs	\N
10194	Andre Kumar	11	pulmonary_embolism	45830	2	5	Nebs	\N
10195	Panel Average	11	pulmonary_embolism	45830	2	\N	\N	\N
8187	Jonathan Chen	10	pulmonary_embolism	46030	10	5	Oxygen	\N
9409	Lisa Shieh	10	pulmonary_embolism	46030	5	3	\N	\N
10390	Panel Average	10	pulmonary_embolism	46030	1	\N	\N	\N
10954	Jason Hom	10	pulmonary_embolism	46030	0	4	\N	\N
10955	Panel Consensus	10	pulmonary_embolism	46030	0	\N	\N	\N
11096	Andre Kumar	10	pulmonary_embolism	46030	-3	1	NIPPV	may drop cardiac output
8188	Jonathan Chen	11	pulmonary_embolism	46030	10	5	Oxygen	\N
9410	Jason Hom	11	pulmonary_embolism	46030	5	5	\N	\N
9411	Lisa Shieh	11	pulmonary_embolism	46030	5	3	\N	\N
9946	Panel Average	11	pulmonary_embolism	46030	2	\N	\N	\N
10956	Panel Consensus	11	pulmonary_embolism	46030	0	\N	\N	\N
11097	Andre Kumar	11	pulmonary_embolism	46030	-3	1	NIPPV	Could induce circulatory collapse
8189	Andre Kumar	10	pulmonary_embolism	45921	10	5	Oxygen	\N
8190	Jason Hom	10	pulmonary_embolism	45921	10	5	\N	\N
8191	Jonathan Chen	10	pulmonary_embolism	45921	10	5	Oxygen	\N
8192	Lisa Shieh	10	pulmonary_embolism	45921	10	5	\N	\N
8193	Panel Average	10	pulmonary_embolism	45921	10	\N	\N	\N
8194	Panel Consensus	10	pulmonary_embolism	45921	10	\N	\N	\N
8195	Jason Hom	12	pulmonary_embolism	45921	10	5	\N	\N
8196	Jonathan Chen	12	pulmonary_embolism	45921	10	5	Oxygen	\N
8197	Lisa Shieh	12	pulmonary_embolism	45921	10	5	\N	\N
8198	Panel Consensus	12	pulmonary_embolism	45921	10	\N	\N	\N
8223	Panel Average	12	pulmonary_embolism	45921	10	\N	\N	\N
8292	Andre Kumar	12	pulmonary_embolism	45921	9	4	Oxygen	\N
11413	Jonathan Chen	11	pulmonary_embolism	45921	10	5	Oxygen	\N
9906	Jonathan Chen	11	pulmonary_embolism	46336	3	3	Respiratory Culture	\N
9907	Lisa Shieh	11	pulmonary_embolism	46336	3	3	\N	\N
10196	Andre Kumar	11	pulmonary_embolism	46336	2	2	Respiratory Culture	\N
10197	Panel Consensus	11	pulmonary_embolism	46336	2	\N	\N	\N
10231	Panel Average	11	pulmonary_embolism	46336	2	\N	\N	\N
10957	Jason Hom	11	pulmonary_embolism	46336	0	5	\N	\N
11409	Jonathan Chen	11	pulmonary_embolism	46179	3	3	Respiratory Culture	\N
8199	Jason Hom	11	pulmonary_embolism	48544	10	5	\N	\N
9412	Panel Average	11	pulmonary_embolism	48544	5	\N	\N	\N
9413	Panel Consensus	11	pulmonary_embolism	48544	5	\N	\N	\N
9908	Jonathan Chen	11	pulmonary_embolism	48544	3	3	Respiratory Culture	\N
9909	Lisa Shieh	11	pulmonary_embolism	48544	3	3	\N	\N
10198	Andre Kumar	11	pulmonary_embolism	48544	2	4	Respiratory Culture	\N
11396	Jonathan Chen	10	pulmonary_embolism	62023	3	4	Respiratory Virus Screen	\N
11394	Jonathan Chen	12	pulmonary_embolism	62023	3	4	Respiratory Virus Screen	\N
8200	Jason Hom	11	pulmonary_embolism	62023	10	5	\N	\N
9414	Panel Consensus	11	pulmonary_embolism	62023	5	\N	\N	\N
9595	Panel Average	11	pulmonary_embolism	62023	4	\N	\N	\N
9910	Jonathan Chen	11	pulmonary_embolism	62023	3	4	Respiratory Virus Screen	\N
10374	Andre Kumar	11	pulmonary_embolism	62023	1	4	Respiratory Viral Panel	\N
8201	Jason Hom	10	pulmonary_embolism	63923	10	5	\N	\N
8863	Panel Average	10	pulmonary_embolism	63923	6	\N	\N	\N
9415	Lisa Shieh	10	pulmonary_embolism	63923	5	3	\N	\N
9416	Panel Consensus	10	pulmonary_embolism	63923	5	\N	\N	\N
9911	Jonathan Chen	10	pulmonary_embolism	63923	3	4	Respiratory Virus Screen	\N
10199	Andre Kumar	10	pulmonary_embolism	63923	2	5	Respiratory Viral Panel	\N
8202	Jason Hom	11	pulmonary_embolism	63923	10	5	\N	\N
8886	Panel Average	11	pulmonary_embolism	63923	5	\N	\N	\N
9417	Lisa Shieh	11	pulmonary_embolism	63923	5	3	\N	\N
9418	Panel Consensus	11	pulmonary_embolism	63923	5	\N	\N	\N
9912	Jonathan Chen	11	pulmonary_embolism	63923	3	4	Respiratory Virus Screen	\N
10375	Andre Kumar	11	pulmonary_embolism	63923	1	4	Respiratory Viral Panel	\N
11380	Jonathan Chen	12	pulmonary_embolism	60178	10	5	Anticoagulation	\N
11406	Jonathan Chen	11	pulmonary_embolism	60178	10	5	Anticoagulation	\N
11424	Jonathan Chen	10	pulmonary_embolism	41796	0	5	\N	Presenting Symptom Diagnosis
10200	Andre Kumar	10	pulmonary_embolism	44198	2	2	Fluids	\N
10201	Panel Average	10	pulmonary_embolism	44198	2	\N	\N	\N
11418	Jonathan Chen	12	pulmonary_embolism	44198	0	2	IVF	\N
11454	Jonathan Chen	8	pulmonary_embolism	44313	0	2	\N	Nebs, but this is more for long term use
8203	Jason Hom	10	pulmonary_embolism	45870	10	5	\N	\N
8697	Panel Average	10	pulmonary_embolism	45870	6	\N	\N	\N
8835	Panel Consensus	10	pulmonary_embolism	45870	6	\N	\N	\N
9419	Jonathan Chen	10	pulmonary_embolism	45870	5	4	Troponin	\N
9420	Lisa Shieh	10	pulmonary_embolism	45870	5	3	\N	\N
9576	Andre Kumar	10	pulmonary_embolism	45870	4	4	Troponin	\N
11414	Jonathan Chen	12	pulmonary_embolism	45870	5	4	Troponin	\N
8204	Jason Hom	11	pulmonary_embolism	45870	10	5	\N	\N
8836	Panel Consensus	11	pulmonary_embolism	45870	6	\N	\N	\N
8864	Panel Average	11	pulmonary_embolism	45870	6	\N	\N	\N
9421	Jonathan Chen	11	pulmonary_embolism	45870	5	4	Troponin	\N
9422	Lisa Shieh	11	pulmonary_embolism	45870	5	3	\N	\N
10202	Andre Kumar	11	pulmonary_embolism	45870	2	3	Troponin	\N
8205	Jason Hom	8	pulmonary_embolism	45870	10	5	\N	\N
8837	Panel Consensus	8	pulmonary_embolism	45870	6	\N	\N	\N
8865	Panel Average	8	pulmonary_embolism	45870	6	\N	\N	\N
9423	Jonathan Chen	8	pulmonary_embolism	45870	5	4	Troponin	\N
9424	Lisa Shieh	8	pulmonary_embolism	45870	5	3	\N	\N
10203	Andre Kumar	8	pulmonary_embolism	45870	2	2	Troponin	\N
11313	Jonathan Chen	11	pulmonary_embolism	45945	0	2	\N	\N
11458	Jonathan Chen	11	pulmonary_embolism	65672	2	2	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
8206	Jason Hom	8	pulmonary_embolism	65672	10	5	\N	\N
9577	Panel Average	8	pulmonary_embolism	65672	4	\N	\N	\N
9578	Panel Consensus	8	pulmonary_embolism	65672	4	\N	\N	\N
10204	Andre Kumar	8	pulmonary_embolism	65672	2	2	Imaging	"IF CTA not done otherwise -2 points"
10205	Jonathan Chen	8	pulmonary_embolism	65672	2	2	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
10959	Lisa Shieh	8	pulmonary_embolism	65672	0	3	\N	\N
11417	Jonathan Chen	11	pulmonary_embolism	65656	2	2	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
11318	Jonathan Chen	11	pulmonary_embolism	65692	2	2	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
11254	Jonathan Chen	10	pulmonary_embolism	45751	0	2	\N	\N
10376	Andre Kumar	11	pulmonary_embolism	45751	1	4	Urinalysis	\N
10404	Panel Average	11	pulmonary_embolism	45751	0	\N	\N	\N
10960	Jason Hom	11	pulmonary_embolism	45751	0	5	\N	\N
10961	Jonathan Chen	11	pulmonary_embolism	45751	0	2	\N	\N
10962	Lisa Shieh	11	pulmonary_embolism	45751	0	3	\N	\N
10963	Panel Consensus	11	pulmonary_embolism	45751	0	\N	\N	\N
11382	Jonathan Chen	11	pulmonary_embolism	45911	0	2	\N	Process
8207	Jason Hom	8	pulmonary_embolism	46113	10	5	\N	\N
8887	Panel Average	8	pulmonary_embolism	46113	5	\N	\N	\N
9425	Lisa Shieh	8	pulmonary_embolism	46113	5	3	\N	\N
9426	Panel Consensus	8	pulmonary_embolism	46113	5	\N	\N	\N
10377	Andre Kumar	8	pulmonary_embolism	46113	1	1	Oxygen	\N
10964	Jonathan Chen	8	pulmonary_embolism	46113	0	2	\N	\N
10378	Andre Kumar	10	pulmonary_embolism	45766	1	2	Weight	\N
10379	Panel Average	10	pulmonary_embolism	45766	1	\N	\N	\N
8208	Jason Hom	10	pulmonary_embolism	45818	10	5	\N	\N
8209	Panel Consensus	10	pulmonary_embolism	45818	10	\N	\N	\N
8427	Jonathan Chen	10	pulmonary_embolism	45818	8	4	CXR	\N
8449	Panel Average	10	pulmonary_embolism	45818	8	\N	\N	\N
8654	Lisa Shieh	10	pulmonary_embolism	45818	7	3	\N	\N
8838	Andre Kumar	10	pulmonary_embolism	45818	6	3	Imaging	\N
8210	Jason Hom	11	pulmonary_embolism	45818	10	5	\N	\N
8211	Panel Consensus	11	pulmonary_embolism	45818	10	\N	\N	\N
8428	Jonathan Chen	11	pulmonary_embolism	45818	8	4	CXR	\N
8467	Panel Average	11	pulmonary_embolism	45818	7	\N	\N	\N
8655	Lisa Shieh	11	pulmonary_embolism	45818	7	3	\N	\N
9427	Andre Kumar	11	pulmonary_embolism	45818	5	4	Imaging	\N
8212	Jason Hom	10	pulmonary_embolism	50200	10	5	\N	\N
8213	Panel Consensus	10	pulmonary_embolism	50200	10	\N	\N	\N
8429	Jonathan Chen	10	pulmonary_embolism	50200	8	4	CXR	\N
8656	Panel Average	10	pulmonary_embolism	50200	7	\N	\N	\N
8839	Andre Kumar	10	pulmonary_embolism	50200	6	3	Imaging	\N
9428	Lisa Shieh	10	pulmonary_embolism	50200	5	3	\N	\N
8214	Jason Hom	10	pulmonary_embolism	45801	10	5	\N	\N
8215	Lisa Shieh	10	pulmonary_embolism	45801	10	5	\N	\N
8216	Panel Consensus	10	pulmonary_embolism	45801	10	\N	\N	\N
8299	Panel Average	10	pulmonary_embolism	45801	9	\N	\N	\N
8430	Jonathan Chen	10	pulmonary_embolism	45801	8	4	CXR	\N
8840	Andre Kumar	10	pulmonary_embolism	45801	6	3	Imaging	\N
8217	Jason Hom	11	pulmonary_embolism	45801	10	5	\N	\N
8218	Lisa Shieh	11	pulmonary_embolism	45801	10	3	\N	\N
8219	Panel Consensus	11	pulmonary_embolism	45801	10	\N	\N	\N
8332	Panel Average	11	pulmonary_embolism	45801	8	\N	\N	\N
8431	Jonathan Chen	11	pulmonary_embolism	45801	8	4	CXR	\N
9429	Andre Kumar	11	pulmonary_embolism	45801	5	4	Imaging	\N
11479	Post-Panel Consolidation	40	atrial_fibrillation	35968	0	0	\N	Negative points seems too severe here. Anti-arrhythmic can be option in unstable Afib if awaiting or failed DCCV. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1861334/
11480	Post-Panel Consolidation	43	atrial_fibrillation	35968	0	0	\N	Negative points seems too severe here. Anti-arrhythmic can be option in unstable Afib if awaiting or failed DCCV. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1861334/
11481	Post-Panel Consolidation	43	atrial_fibrillation	44352	0	0	\N	Negative points seems too severe here. Anti-arrhythmic can be option in unstable Afib if awaiting or failed DCCV. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1861334/
11482	Post-Panel Consolidation	40	atrial_fibrillation	45887	3	0	\N	Why different per initial vs. worse state?
11483	Post-Panel Consolidation	43	atrial_fibrillation	45887	3	0	\N	Why different per initial vs. worse state?
11484	Post-Panel Consolidation	40	atrial_fibrillation	62176	7	0	Echo	\N
11485	Post-Panel Consolidation	43	atrial_fibrillation	62176	7	0	Echo	Okay for workup, but not while unstable?
11486	Post-Panel Consolidation	40	atrial_fibrillation	45963	-4	0	TEEcho	Not while unstable
11487	Post-Panel Consolidation	43	atrial_fibrillation	45963	-4	0	TEEcho	\N
11488	Post-Panel Consolidation	41	atrial_fibrillation	61832	7	0	Echo	\N
11489	Post-Panel Consolidation	40	atrial_fibrillation	61832	7	0	Echo	Good for Afib workup, but less points if doing it while unstable?
11490	Post-Panel Consolidation	40	atrial_fibrillation	44004	0	0	\N	\N
11491	Post-Panel Consolidation	41	atrial_fibrillation	44004	0	0	\N	Positive points for furosemide here, but negative points for initial state. But also give negative points for giving IV Fluids?
11492	Post-Panel Consolidation	43	atrial_fibrillation	44004	0	0	\N	\N
11493	Post-Panel Consolidation	16	gi_bleed	45858	-5	0	CT Abdomen	Treat all CT Abd/Pelvis orders as comparable for simplicity, so why different scores? Weird cirrhosis diagnostic, but maybe people are looking for bleeding vessel?
11494	Post-Panel Consolidation	14	gi_bleed	45852	-5	0	CT Abdomen	Treat all CT Abd/Pelvis orders as comparable for simplicity, so why different scores? Weird cirrhosis diagnostic, but maybe people are looking for bleeding vessel?
11495	Post-Panel Consolidation	2	gi_bleed	49836	-5	0	CT Abdomen	Treat all CT Abd/Pelvis orders as comparable for simplicity, so why different scores? Weird cirrhosis diagnostic, but maybe people are looking for bleeding vessel?
11496	Post-Panel Consolidation	30	meningitis	45983	-3	0	CT Head	\N
11497	Post-Panel Consolidation	31	meningitis	45983	-3	0	CT Head	Gave -3 points if CT head before treatment, but what about after treatment?
11498	Post-Panel Consolidation	30	meningitis	50241	-3	0	CT Head	\N
11499	Post-Panel Consolidation	40	atrial_fibrillation	45977	0	0	\N	Standard Process
11500	Post-Panel Consolidation	41	atrial_fibrillation	45977	0	0	\N	Standard Process
11501	Post-Panel Consolidation	40	atrial_fibrillation	45919	1	0	Blood Gas	Override for consistency with others
11502	Post-Panel Consolidation	41	atrial_fibrillation	45793	6	0	CBC	Override for consistency with other choices across states
11503	Post-Panel Consolidation	40	atrial_fibrillation	50400	0	0	\N	\N
11504	Post-Panel Consolidation	43	atrial_fibrillation	50400	0	0	\N	\N
11505	Post-Panel Consolidation	40	atrial_fibrillation	49251	0	0	\N	Override, neutralize non-procedure consults
11506	Post-Panel Consolidation	41	atrial_fibrillation	49251	0	0	\N	Override, neutralize non-procedure consults
11507	Post-Panel Consolidation	43	atrial_fibrillation	49251	0	0	\N	Override, neutralize non-procedure consults
11508	Post-Panel Consolidation	40	atrial_fibrillation	45811	2	0	\N	Override, excess points for non-action
11509	Post-Panel Consolidation	43	atrial_fibrillation	45811	2	0	\N	Override, excess points for non-action
11510	Post-Panel Consolidation	40	atrial_fibrillation	46160	0	0	\N	Standard process
11511	Post-Panel Consolidation	40	atrial_fibrillation	44297	3	0	\N	Override, less point differential for initial vs. worse state
11512	Post-Panel Consolidation	40	atrial_fibrillation	44359	8	0	Anticoagulation	Override consistent points
11513	Post-Panel Consolidation	41	atrial_fibrillation	44359	8	0	Anticoagulation	Override consistent points
11514	Post-Panel Consolidation	40	atrial_fibrillation	46183	0	0	\N	Override, standard process after heparin order
11515	Post-Panel Consolidation	40	atrial_fibrillation	63714	0	0	\N	Override, standard process after heparin order
11516	Post-Panel Consolidation	43	atrial_fibrillation	61837	3	0	Lipids	\N
11517	Post-Panel Consolidation	41	atrial_fibrillation	45763	7	0	Metabolic Panel	\N
11518	Post-Panel Consolidation	40	atrial_fibrillation	45864	0	0	Oxygen	Override, no hypoxia?
11519	Post-Panel Consolidation	40	atrial_fibrillation	45900	0	0	Oxygen	Override, no hypoxia?
11520	Post-Panel Consolidation	40	atrial_fibrillation	61823	0	0	\N	Override, standard process
11521	Post-Panel Consolidation	40	atrial_fibrillation	46090	0	0	\N	Override, embedded in CBC or part of Heparin protocol
11522	Post-Panel Consolidation	40	atrial_fibrillation	45955	3	0	Lactate	Override to match lactate order
11523	Post-Panel Consolidation	43	atrial_fibrillation	45955	3	0	Lactate	Override to match lactate order
11524	Post-Panel Consolidation	43	atrial_fibrillation	49995	5	0	Cardiology	Override, treat same as Cardiology consult
11525	Post-Panel Consolidation	40	atrial_fibrillation	60178	3	0	Anticoagulation-Oral	Oral admin, is this too slow, and so should be worth less points?
11526	Post-Panel Consolidation	41	atrial_fibrillation	60178	3	0	Anticoagulation-Oral	Oral admin, is this too slow, and so should be worth less points?
11527	Post-Panel Consolidation	43	atrial_fibrillation	60178	3	0	Anticoagulation-Oral	Oral admin, is this too slow, and so should be worth less points?
11528	Post-Panel Consolidation	40	atrial_fibrillation	63725	3	0	Lactate	Override for consistency
11529	Post-Panel Consolidation	40	atrial_fibrillation	45818	3	0	\N	Override to match Portable CXR, since this can be a portable order too
11530	Post-Panel Consolidation	43	atrial_fibrillation	45818	3	0	\N	Override to match Portable CXR, since this can be a portable order too
11531	Post-Panel Consolidation	15	gi_bleed	45932	5	0	Hepatitis Panel	Override to match panel
11532	Post-Panel Consolidation	16	gi_bleed	45814	0	0	\N	Override, standard process
11533	Post-Panel Consolidation	14	gi_bleed	61982	0	0	\N	Override, standard process
11534	Post-Panel Consolidation	15	gi_bleed	61982	0	0	\N	Override, standard process
11535	Post-Panel Consolidation	15	gi_bleed	44275	8	0	IVF	Override to match panel grade
11536	Post-Panel Consolidation	14	gi_bleed	48513	2	0	\N	Override, consistencu with Indirect Bilirubin
11537	Post-Panel Consolidation	15	gi_bleed	45823	10	0	Type and Screen	Override, match panel, though this seems like too much for what will likely be part of standard tranfusion process orders
11538	Post-Panel Consolidation	14	gi_bleed	44439	8	0	IVF	Override to match panel grade
11539	Post-Panel Consolidation	15	gi_bleed	44439	8	0	IVF	Override to match panel grade
11540	Post-Panel Consolidation	15	gi_bleed	50400	0	0	\N	Neutralize consults
11541	Post-Panel Consolidation	15	gi_bleed	61323	2	0	\N	Override for consistency and avoid excess points for worse state compensation
11542	Post-Panel Consolidation	14	gi_bleed	49207	0	0	\N	Override, standard process
11543	Post-Panel Consolidation	14	gi_bleed	46160	0	0	\N	Override, standard process
11544	Post-Panel Consolidation	14	gi_bleed	63759	10	0	RBC	Override, seems typo on score?
11545	Post-Panel Consolidation	15	gi_bleed	71083	0	0	\N	Override, non-specific process / consult
11546	Post-Panel Consolidation	2	gi_bleed	45771	9	0	Metabolic Panel	\N
11547	Post-Panel Consolidation	15	gi_bleed	45832	7	0	Intubation	?Mechanical ventilation? Airway protection?
11548	Post-Panel Consolidation	14	gi_bleed	63725	2	0	Lactate	Override to match others
11549	Post-Panel Consolidation	14	gi_bleed	61993	8	0	Coagulopathy Correction	\N
11550	Post-Panel Consolidation	15	gi_bleed	61993	8	0	Coagulopathy Correction	\N
11551	Post-Panel Consolidation	16	gi_bleed	61993	8	0	Coagulopathy Correction	\N
11552	Post-Panel Consolidation	14	gi_bleed	45870	0	0	Troponin	Hemodynamic stability assessment?
11553	Post-Panel Consolidation	14	gi_bleed	50372	0	0	\N	Override, standard process
11554	Post-Panel Consolidation	30	meningitis	56492	5	0	Pain Control	Minor points for symptom control?
11555	Post-Panel Consolidation	31	meningitis	56492	5	0	Pain Control	Minor points for symptom control?
11556	Post-Panel Consolidation	33	meningitis	44281	5	0	Pain Control	Minor points for symptom control?
11557	Post-Panel Consolidation	30	meningitis	44310	5	0	Pain Control	Minor points for symptom control?
11558	Post-Panel Consolidation	31	meningitis	44310	5	0	Pain Control	Minor points for symptom control?
11559	Post-Panel Consolidation	31	meningitis	61864	5	0	HIV Test	Override, match other HIV tests
11560	Post-Panel Consolidation	30	meningitis	45966	7	0	CBC	\N
11561	Post-Panel Consolidation	31	meningitis	48880	5	0	\N	Panel of CSF tests, should get point for each? Adds up to more than value of antibiotics
11562	Post-Panel Consolidation	31	meningitis	48980	0	0	\N	Override, neutralize non-procedure consults
11563	Post-Panel Consolidation	33	meningitis	48980	0	0	\N	Override, neutralize non-procedure consults
11564	Post-Panel Consolidation	31	meningitis	49207	0	0	\N	Override, standard process
11565	Post-Panel Consolidation	31	meningitis	49083	1	0	\N	Late to be drawing culture if already got antibiotics
11566	Post-Panel Consolidation	30	meningitis	44237	0	0	\N	Mix of scores, as doesn't penetrate CNS. Leave as 0 for ambiguous, not directly harmful
11567	Post-Panel Consolidation	30	meningitis	44252	0	0	\N	Mix of scores, as doesn't penetrate CNS. Leave as 0 for ambiguous, not directly harmful
11568	Post-Panel Consolidation	31	meningitis	48577	5	0	\N	\N
11569	Post-Panel Consolidation	30	meningitis	46006	0	0	\N	Override, let be subsumed by Culture + Gram Stain order
11570	Post-Panel Consolidation	33	meningitis	46006	0	0	\N	Override, let be subsumed by Culture + Gram Stain order
11571	Post-Panel Consolidation	33	meningitis	49109	7	0	HSV CSF	\N
11572	Post-Panel Consolidation	30	meningitis	48954	0	0	\N	Standard process
11573	Post-Panel Consolidation	30	meningitis	50510	5	0	\N	Reasonable, though not standard guidelines to check
11574	Post-Panel Consolidation	30	meningitis	63811	0	0	\N	Override, let points be from respective test orders
11575	Post-Panel Consolidation	31	meningitis	63811	0	0	\N	Override, let points be from respective test orders
11576	Post-Panel Consolidation	33	meningitis	63811	0	0	\N	Override, let points be from respective test orders
11577	Post-Panel Consolidation	30	meningitis	62167	0	0	\N	Override, let points be from respective test orders
11578	Post-Panel Consolidation	33	meningitis	62167	0	0	\N	Override, let points be from respective test orders
11579	Post-Panel Consolidation	30	meningitis	45798	5	0	Pregnancy Test	\N
11580	Post-Panel Consolidation	31	meningitis	49020	5	0	\N	\N
11581	Post-Panel Consolidation	30	meningitis	45759	5	0	Coags	Override, match DIC screen
11582	Post-Panel Consolidation	30	meningitis	45770	5	0	Coags	Override, match DIC screen
11583	Post-Panel Consolidation	31	meningitis	62103	5	0	HIV Test	\N
11584	Post-Panel Consolidation	30	meningitis	48586	0	0	\N	\N
11585	Post-Panel Consolidation	30	meningitis	45801	3	0	CXR	General workup for fever/infection, though symptoms not suggestive of pneumonia
11586	Post-Panel Consolidation	5000	neutropenic	56492	4	0	Acetaminophen	\N
11587	Post-Panel Consolidation	5003	neutropenic	44281	4	0	Acetaminophen	\N
11588	Post-Panel Consolidation	5000	neutropenic	48829	0	0	\N	\N
11589	Post-Panel Consolidation	5003	neutropenic	45901	10	0	Blood Cultures	Less points if after antibiotics? May not be able to reliably distinguish if batch order
11590	Post-Panel Consolidation	5003	neutropenic	45752	10	0	Blood Cultures	Less points if after antibiotics? May not be able to reliably distinguish if batch order
11591	Post-Panel Consolidation	5003	neutropenic	44439	10	0	IVF	\N
11592	Post-Panel Consolidation	5002	neutropenic	45793	8	0	CBC	Override for consistency with panel
11593	Post-Panel Consolidation	5003	neutropenic	45793	8	0	CBC	\N
11594	Post-Panel Consolidation	5003	neutropenic	45788	8	0	CBC	\N
11595	Post-Panel Consolidation	5002	neutropenic	45966	8	0	CBC	\N
11596	Post-Panel Consolidation	5003	neutropenic	48980	0	0	\N	Neutralize non-procedure consults
11597	Post-Panel Consolidation	5002	neutropenic	49228	0	0	\N	Neutralize non-procedure consults
11598	Post-Panel Consolidation	5003	neutropenic	49054	5	0	\N	Neutropenic, not droplet isolation. Override to match panel. Could be on initial isolation pending viral screen
11599	Post-Panel Consolidation	5000	neutropenic	45806	3	0	\N	Match panel
11600	Post-Panel Consolidation	5003	neutropenic	45806	3	0	\N	Match panel
11601	Post-Panel Consolidation	5003	neutropenic	45763	10	0	Metabolic Panel	Match panel
11602	Post-Panel Consolidation	5003	neutropenic	45771	10	0	Metabolic Panel	Match panel
11603	Post-Panel Consolidation	5003	neutropenic	45955	10	0	Lactate	Match panel
11604	Post-Panel Consolidation	5000	neutropenic	45759	4	0	Coags	Match panel
11605	Post-Panel Consolidation	5003	neutropenic	45759	4	0	Coags	Match panel
11606	Post-Panel Consolidation	5000	neutropenic	45770	4	0	Coags	Match panel
11607	Post-Panel Consolidation	5003	neutropenic	45770	4	0	Coags	Match panel
11608	Post-Panel Consolidation	5003	neutropenic	62023	6	0	Respiratory Virus Screen	Match panel
11609	Post-Panel Consolidation	5003	neutropenic	63923	6	0	Respiratory Virus Screen	Match panel
11610	Post-Panel Consolidation	5002	neutropenic	63725	10	0	Lactate	Match panel
11611	Post-Panel Consolidation	5003	neutropenic	45995	3	0	\N	Match panel
11612	Post-Panel Consolidation	10	pulmonary_embolism	45977	0	0	\N	Override, standard process
11613	Post-Panel Consolidation	11	pulmonary_embolism	45977	0	0	\N	Override, standard process
11614	Post-Panel Consolidation	11	pulmonary_embolism	45814	0	0	\N	Override, standard process
11615	Post-Panel Consolidation	10	pulmonary_embolism	46309	7	0	Nebs	Match panel
11616	Post-Panel Consolidation	11	pulmonary_embolism	46309	7	0	Nebs	Match panel
11617	Post-Panel Consolidation	10	pulmonary_embolism	44349	7	0	Nebs	Match panel
11618	Post-Panel Consolidation	11	pulmonary_embolism	44349	7	0	Nebs	Match panel
11619	Post-Panel Consolidation	10	pulmonary_embolism	60175	7	0	Nebs	Match panel
11620	Post-Panel Consolidation	11	pulmonary_embolism	60175	7	0	Nebs	Match panel
11621	Post-Panel Consolidation	12	pulmonary_embolism	60175	7	0	Nebs	Match panel
11622	Post-Panel Consolidation	10	pulmonary_embolism	47146	4	0	Aspirin	Match panel
11623	Post-Panel Consolidation	8	pulmonary_embolism	44206	4	0	Aspirin	\N
11624	Post-Panel Consolidation	8	pulmonary_embolism	45793	10	0	CBC	Match panel, though seems high
11625	Post-Panel Consolidation	12	pulmonary_embolism	45793	10	0	CBC	Match panel, though seems high
11626	Post-Panel Consolidation	8	pulmonary_embolism	45788	10	0	CBC	Match panel, though seems high
11627	Post-Panel Consolidation	10	pulmonary_embolism	65695	0	0	\N	Override, neutralize non-procedural consults
11628	Post-Panel Consolidation	11	pulmonary_embolism	65695	0	0	\N	Override, neutralize non-procedural consults
11629	Post-Panel Consolidation	12	pulmonary_embolism	61323	0	0	\N	Override, neutralize non-procedural consults. Patient wouldn't qualify for ICU transfer?
11630	Post-Panel Consolidation	12	pulmonary_embolism	48502	4	0	Biopsy	Consult, but maybe thinking about IR procedure. Not necessary for initial PE treatment, but maybe thinking about biopsy already
11631	Post-Panel Consolidation	10	pulmonary_embolism	49207	0	0	\N	Override, neutralize non-procedural consults
11632	Post-Panel Consolidation	11	pulmonary_embolism	49228	0	0	\N	Override, neutralize non-procedural consults
11633	Post-Panel Consolidation	8	pulmonary_embolism	49228	0	0	\N	Override, neutralize non-procedural consults
11634	Post-Panel Consolidation	11	pulmonary_embolism	49073	7	0	CT Chest	Override, still offer points, as CT Chest order details could allow specification of PE / contrast protocol
11635	Post-Panel Consolidation	8	pulmonary_embolism	46008	2	0	NPO	Override for consistency with other NPO orders
11636	Post-Panel Consolidation	12	pulmonary_embolism	45866	7	0	\N	Match panel
11637	Post-Panel Consolidation	10	pulmonary_embolism	62176	6	0	Echo	Match panel
11638	Post-Panel Consolidation	11	pulmonary_embolism	62176	6	0	Echo	Match panel
11639	Post-Panel Consolidation	11	pulmonary_embolism	46183	0	0	\N	Override, just count primary anticoagulation order
11640	Post-Panel Consolidation	10	pulmonary_embolism	49301	7	0	Blood Gas	Match panel
11641	Post-Panel Consolidation	8	pulmonary_embolism	45806	5	0	\N	Match panel
11642	Post-Panel Consolidation	10	pulmonary_embolism	45806	5	0	\N	Match panel
11643	Post-Panel Consolidation	12	pulmonary_embolism	45806	5	0	\N	Match panel
11644	Post-Panel Consolidation	8	pulmonary_embolism	45771	10	0	Metabolic Panel	\N
11645	Post-Panel Consolidation	12	pulmonary_embolism	45771	10	0	Metabolic Panel	\N
11646	Post-Panel Consolidation	11	pulmonary_embolism	46090	0	0	\N	Override, embed to heparin order
11647	Post-Panel Consolidation	11	pulmonary_embolism	45776	0	0	\N	Override, process
11648	Post-Panel Consolidation	10	pulmonary_embolism	45770	10	0	Coags	Match panel. Monitor in prep for anticoagulation?
11649	Post-Panel Consolidation	12	pulmonary_embolism	45770	10	0	Coags	\N
11650	Post-Panel Consolidation	12	pulmonary_embolism	45857	0	0	\N	Override, process order for actual nebs medication order
11651	Post-Panel Consolidation	10	pulmonary_embolism	45830	0	0	\N	Override, process order for actual nebs medication order
11652	Post-Panel Consolidation	12	pulmonary_embolism	45830	0	0	\N	Override, process order for actual nebs medication order
11653	Post-Panel Consolidation	11	pulmonary_embolism	46179	5	0	Respiratory Culture	\N
11654	Post-Panel Consolidation	10	pulmonary_embolism	62023	5	0	Respiratory Virus Screen	\N
11655	Post-Panel Consolidation	12	pulmonary_embolism	62023	5	0	Respiratory Virus Screen	\N
11656	Post-Panel Consolidation	12	pulmonary_embolism	45870	6	0	Troponin	\N
11657	Post-Panel Consolidation	11	pulmonary_embolism	65672	4	0	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
11658	Post-Panel Consolidation	11	pulmonary_embolism	65656	4	0	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
11659	Post-Panel Consolidation	11	pulmonary_embolism	65692	4	0	DVT US	Could be good early diagnosis, but here the diagnosis of PE has likely already been made given on anticoag. So not sure what the point of adding on DVT US. They'll find DVT, but already diagnosed PE anyway.
11660	Post-Panel Consolidation	8	pulmonary_embolism	46113	0	0	\N	Process?
11661	Post-Panel Consolidation	43	atrial_fibrillation	46605	0	1	\N	Irregular rhythm, so adenosine not so relevant
11662	Post-Panel Consolidation	41	atrial_fibrillation	65641	0	1	\N	Standard Process
11663	Post-Panel Consolidation	41	atrial_fibrillation	47146	2	1	Aspirin	\N
11664	Post-Panel Consolidation	40	atrial_fibrillation	44206	2	1	Aspirin	\N
11665	Post-Panel Consolidation	41	atrial_fibrillation	44206	2	1	Aspirin	\N
11666	Post-Panel Consolidation	43	atrial_fibrillation	44206	2	1	Aspirin	\N
11667	Post-Panel Consolidation	43	atrial_fibrillation	44315	1	1	Aspirin	\N
11668	Post-Panel Consolidation	41	atrial_fibrillation	44240	2	1	\N	\N
11669	Post-Panel Consolidation	43	atrial_fibrillation	45901	1	1	\N	\N
11670	Post-Panel Consolidation	40	atrial_fibrillation	41870	0	1	\N	\N
11671	Post-Panel Consolidation	40	atrial_fibrillation	45827	8	1	\N	\N
11672	Post-Panel Consolidation	41	atrial_fibrillation	45827	8	1	\N	\N
11673	Post-Panel Consolidation	40	atrial_fibrillation	45793	6	1	CBC	\N
11674	Post-Panel Consolidation	43	atrial_fibrillation	45793	6	1	CBC	\N
11675	Post-Panel Consolidation	40	atrial_fibrillation	45788	6	1	CBC	\N
11676	Post-Panel Consolidation	41	atrial_fibrillation	45788	6	1	CBC	\N
11677	Post-Panel Consolidation	41	atrial_fibrillation	65695	0	1	\N	\N
11678	Post-Panel Consolidation	43	atrial_fibrillation	61323	6	1	\N	\N
11679	Post-Panel Consolidation	40	atrial_fibrillation	50098	-5	1	CT Head	\N
11680	Post-Panel Consolidation	40	atrial_fibrillation	45983	-5	1	CT Head	\N
11681	Post-Panel Consolidation	40	atrial_fibrillation	49965	-5	1	CT Head	\N
11682	Post-Panel Consolidation	40	atrial_fibrillation	-100	10	1	\N	\N
11683	Post-Panel Consolidation	43	atrial_fibrillation	-100	10	1	\N	\N
11684	Post-Panel Consolidation	40	atrial_fibrillation	44353	-2	1	\N	\N
11685	Post-Panel Consolidation	41	atrial_fibrillation	45824	1	1	\N	\N
11686	Post-Panel Consolidation	41	atrial_fibrillation	45811	2	1	\N	\N
11687	Post-Panel Consolidation	40	atrial_fibrillation	46674	-4	1	\N	\N
11688	Post-Panel Consolidation	43	atrial_fibrillation	46674	-4	1	\N	\N
11689	Post-Panel Consolidation	40	atrial_fibrillation	35846	-8	1	\N	\N
11690	Post-Panel Consolidation	43	atrial_fibrillation	35846	-9	1	\N	\N
11691	Post-Panel Consolidation	43	atrial_fibrillation	44393	-8	1	\N	\N
11692	Post-Panel Consolidation	43	atrial_fibrillation	44251	-8	1	\N	\N
11693	Post-Panel Consolidation	40	atrial_fibrillation	44204	-2	1	\N	\N
11694	Post-Panel Consolidation	43	atrial_fibrillation	45941	2	1	\N	\N
11695	Post-Panel Consolidation	40	atrial_fibrillation	45866	9	1	\N	\N
11696	Post-Panel Consolidation	41	atrial_fibrillation	45866	5	1	\N	Okay to have less points here, to emphasize missed opportunity initially?
11697	Post-Panel Consolidation	43	atrial_fibrillation	45866	9	1	\N	\N
11698	Post-Panel Consolidation	43	atrial_fibrillation	44248	-8	1	\N	\N
11699	Post-Panel Consolidation	43	atrial_fibrillation	44297	2	1	\N	\N
11700	Post-Panel Consolidation	40	atrial_fibrillation	46230	-2	1	\N	\N
11701	Post-Panel Consolidation	40	atrial_fibrillation	50343	0	1	\N	\N
11702	Post-Panel Consolidation	41	atrial_fibrillation	45797	3	1	\N	\N
11703	Post-Panel Consolidation	43	atrial_fibrillation	44359	8	1	Anticoagulation	\N
11704	Post-Panel Consolidation	40	atrial_fibrillation	49301	1	1	Blood Gas	\N
11705	Post-Panel Consolidation	40	atrial_fibrillation	45888	1	1	Blood Gas	\N
11706	Post-Panel Consolidation	43	atrial_fibrillation	48732	1	1	Blood Gas	\N
11707	Post-Panel Consolidation	40	atrial_fibrillation	45942	5	1	INR	\N
11708	Post-Panel Consolidation	40	atrial_fibrillation	45838	6	1	Troponin	\N
11709	Post-Panel Consolidation	40	atrial_fibrillation	62151	3	1	Lactate	\N
11710	Post-Panel Consolidation	41	atrial_fibrillation	62151	2	1	Lactate	\N
11711	Post-Panel Consolidation	41	atrial_fibrillation	46011	3	1	Lipids	\N
11712	Post-Panel Consolidation	41	atrial_fibrillation	61837	3	1	Lipids	\N
11713	Post-Panel Consolidation	40	atrial_fibrillation	45806	6	1	\N	\N
11714	Post-Panel Consolidation	41	atrial_fibrillation	45806	6	1	\N	\N
11715	Post-Panel Consolidation	40	atrial_fibrillation	45763	7	1	Metabolic Panel	\N
11716	Post-Panel Consolidation	40	atrial_fibrillation	45771	7	1	Metabolic Panel	\N
11717	Post-Panel Consolidation	41	atrial_fibrillation	45771	7	1	Metabolic Panel	\N
11718	Post-Panel Consolidation	43	atrial_fibrillation	45771	7	1	Metabolic Panel	\N
11719	Post-Panel Consolidation	40	atrial_fibrillation	44327	-8	1	\N	\N
11720	Post-Panel Consolidation	41	atrial_fibrillation	44005	4	1	\N	\N
11721	Post-Panel Consolidation	40	atrial_fibrillation	44000	5	1	\N	\N
11722	Post-Panel Consolidation	43	atrial_fibrillation	44000	4	1	\N	\N
11723	Post-Panel Consolidation	40	atrial_fibrillation	44294	2	1	\N	\N
11724	Post-Panel Consolidation	41	atrial_fibrillation	45792	0	1	\N	\N
11725	Post-Panel Consolidation	43	atrial_fibrillation	45792	-1	1	\N	\N
11726	Post-Panel Consolidation	43	atrial_fibrillation	44241	0	1	\N	Trying to relieve preload?
11727	Post-Panel Consolidation	43	atrial_fibrillation	44256	0	1	\N	Trying to relieve preload?
11728	Post-Panel Consolidation	40	atrial_fibrillation	48628	0	1	\N	\N
11729	Post-Panel Consolidation	40	atrial_fibrillation	46081	0	1	\N	\N
11730	Post-Panel Consolidation	40	atrial_fibrillation	50235	0	1	\N	Not a respiratory issue?
11731	Post-Panel Consolidation	43	atrial_fibrillation	50235	0	1	\N	Not respiratory issue, but maybe thinking manage preload with pulmonary pressure?
11732	Post-Panel Consolidation	43	atrial_fibrillation	36086	0	1	Vasopressor	Adding vasopressor on while hypotensive from negative inotrope?
11733	Post-Panel Consolidation	40	atrial_fibrillation	45853	5	1	\N	\N
11734	Post-Panel Consolidation	41	atrial_fibrillation	45853	5	1	\N	\N
11735	Post-Panel Consolidation	43	atrial_fibrillation	45853	5	1	\N	\N
11736	Post-Panel Consolidation	40	atrial_fibrillation	45787	0	1	\N	\N
11737	Post-Panel Consolidation	41	atrial_fibrillation	45787	0	1	\N	\N
11738	Post-Panel Consolidation	40	atrial_fibrillation	48822	0	1	Oxygen	\N
11739	Post-Panel Consolidation	43	atrial_fibrillation	48822	0	1	Oxygen	\N
11740	Post-Panel Consolidation	43	atrial_fibrillation	45900	0	1	Oxygen	\N
11741	Post-Panel Consolidation	43	atrial_fibrillation	43993	0	1	Vasopressor	\N
11742	Post-Panel Consolidation	40	atrial_fibrillation	45778	1	1	\N	\N
11743	Post-Panel Consolidation	43	atrial_fibrillation	45778	1	1	\N	\N
11744	Post-Panel Consolidation	40	atrial_fibrillation	45914	6	1	Troponin	\N
11745	Post-Panel Consolidation	43	atrial_fibrillation	46185	1	1	Blood Gas	\N
11746	Post-Panel Consolidation	40	atrial_fibrillation	46067	3	1	Metabolic Panel	\N
11747	Post-Panel Consolidation	43	atrial_fibrillation	46000	0	1	\N	\N
11748	Post-Panel Consolidation	40	atrial_fibrillation	45759	5	1	INR	\N
11749	Post-Panel Consolidation	41	atrial_fibrillation	45759	5	1	INR	\N
11750	Post-Panel Consolidation	43	atrial_fibrillation	45759	5	1	INR	\N
11751	Post-Panel Consolidation	40	atrial_fibrillation	45776	0	1	\N	\N
11752	Post-Panel Consolidation	41	atrial_fibrillation	45776	0	1	\N	\N
11753	Post-Panel Consolidation	40	atrial_fibrillation	45770	5	1	INR	Merge with INR just to represent checking coags
11754	Post-Panel Consolidation	43	atrial_fibrillation	45770	5	1	INR	Merge with INR just to represent checking coags
11755	Post-Panel Consolidation	40	atrial_fibrillation	44312	0	1	\N	\N
11756	Post-Panel Consolidation	40	atrial_fibrillation	44198	-2	1	\N	\N
11757	Post-Panel Consolidation	43	atrial_fibrillation	44198	-2	1	\N	\N
11758	Post-Panel Consolidation	40	atrial_fibrillation	45870	6	1	Troponin	\N
11759	Post-Panel Consolidation	41	atrial_fibrillation	45870	6	1	Troponin	\N
11760	Post-Panel Consolidation	43	atrial_fibrillation	45870	6	1	Troponin	\N
11761	Post-Panel Consolidation	40	atrial_fibrillation	62105	7	1	\N	\N
11762	Post-Panel Consolidation	41	atrial_fibrillation	62105	7	1	\N	\N
11763	Post-Panel Consolidation	40	atrial_fibrillation	45945	0	1	\N	\N
11764	Post-Panel Consolidation	43	atrial_fibrillation	45945	0	1	\N	\N
11765	Post-Panel Consolidation	40	atrial_fibrillation	65656	-1	1	DVT US	\N
11766	Post-Panel Consolidation	41	atrial_fibrillation	65656	-1	1	DVT US	\N
11767	Post-Panel Consolidation	40	atrial_fibrillation	65692	-1	1	DVT US	\N
11768	Post-Panel Consolidation	41	atrial_fibrillation	65692	-1	1	DVT US	\N
11769	Post-Panel Consolidation	41	atrial_fibrillation	45751	0	1	\N	\N
11770	Post-Panel Consolidation	40	atrial_fibrillation	46236	2	1	\N	EtOH as part of Afib eval?
11771	Post-Panel Consolidation	41	atrial_fibrillation	45818	3	1	\N	\N
11772	Post-Panel Consolidation	40	atrial_fibrillation	50200	3	1	\N	\N
11773	Post-Panel Consolidation	41	atrial_fibrillation	50200	3	1	\N	\N
11774	Post-Panel Consolidation	40	atrial_fibrillation	45801	-3	1	\N	\N
11775	Post-Panel Consolidation	43	atrial_fibrillation	45801	-3	1	\N	\N
11776	Post-Panel Consolidation	14	gi_bleed	44281	-1	1	\N	\N
11777	Post-Panel Consolidation	2	gi_bleed	48829	1	1	\N	\N
11778	Post-Panel Consolidation	14	gi_bleed	44416	0	1	\N	Acetaminophen overdose, non-specific hepatitis treatment?
11779	Post-Panel Consolidation	2	gi_bleed	65641	0	1	\N	\N
11780	Post-Panel Consolidation	14	gi_bleed	65641	0	1	\N	\N
11781	Post-Panel Consolidation	16	gi_bleed	65641	0	1	\N	\N
11782	Post-Panel Consolidation	15	gi_bleed	48744	0	1	\N	Probably want complete hepatic panel, so give points there
11783	Post-Panel Consolidation	14	gi_bleed	46136	0	1	\N	\N
11784	Post-Panel Consolidation	15	gi_bleed	46136	0	1	\N	\N
11785	Post-Panel Consolidation	2	gi_bleed	46136	0	1	\N	\N
11786	Post-Panel Consolidation	15	gi_bleed	63723	0	1	\N	\N
11787	Post-Panel Consolidation	14	gi_bleed	50962	-4	1	\N	Mistaken test. Wasted, but not directly harmful?
11788	Post-Panel Consolidation	15	gi_bleed	46245	2	1	\N	\N
11789	Post-Panel Consolidation	14	gi_bleed	45901	0	1	\N	\N
11790	Post-Panel Consolidation	14	gi_bleed	45752	0	1	\N	\N
11791	Post-Panel Consolidation	14	gi_bleed	45760	0	1	Blood Gas	\N
11792	Post-Panel Consolidation	15	gi_bleed	45919	0	1	Blood Gas	\N
11793	Post-Panel Consolidation	14	gi_bleed	45823	10	1	Type and Screen	\N
11794	Post-Panel Consolidation	14	gi_bleed	44290	8	1	IVF	\N
11795	Post-Panel Consolidation	15	gi_bleed	44290	8	1	IVF	\N
11796	Post-Panel Consolidation	15	gi_bleed	45887	0	1	\N	\N
11797	Post-Panel Consolidation	2	gi_bleed	45887	0	1	\N	\N
11798	Post-Panel Consolidation	14	gi_bleed	45793	10	1	CBC	\N
11799	Post-Panel Consolidation	15	gi_bleed	45793	10	1	CBC	\N
11800	Post-Panel Consolidation	16	gi_bleed	45793	10	1	CBC	\N
11801	Post-Panel Consolidation	2	gi_bleed	45793	10	1	CBC	\N
11802	Post-Panel Consolidation	14	gi_bleed	45788	10	1	CBC	\N
11803	Post-Panel Consolidation	15	gi_bleed	45788	10	1	CBC	\N
11804	Post-Panel Consolidation	2	gi_bleed	45788	10	1	CBC	\N
11805	Post-Panel Consolidation	15	gi_bleed	44255	0	1	\N	Not reliable to cover Gram negative enterics (e.g., E coli)
11806	Post-Panel Consolidation	15	gi_bleed	44637	5	1	Antibiotics	\N
11807	Post-Panel Consolidation	14	gi_bleed	45060	2	1	Antibiotics	\N
11808	Post-Panel Consolidation	15	gi_bleed	45060	2	1	Antibiotics	\N
11809	Post-Panel Consolidation	14	gi_bleed	35733	10	1	Antibiotics	\N
11810	Post-Panel Consolidation	15	gi_bleed	35733	10	1	Antibiotics	\N
11811	Post-Panel Consolidation	16	gi_bleed	35733	10	1	Antibiotics	\N
11812	Post-Panel Consolidation	2	gi_bleed	35733	10	1	Antibiotics	\N
11813	Post-Panel Consolidation	2	gi_bleed	44249	7	1	Antibiotics	Reasonable empiric choice for GNRs
11814	Post-Panel Consolidation	14	gi_bleed	62027	0	1	\N	\N
11815	Post-Panel Consolidation	2	gi_bleed	63720	5	1	Hepatitis Panel	\N
11816	Post-Panel Consolidation	14	gi_bleed	49481	10	1	GI EGD	\N
11817	Post-Panel Consolidation	15	gi_bleed	49481	10	1	GI EGD	\N
11818	Post-Panel Consolidation	16	gi_bleed	49481	10	1	GI EGD	\N
11819	Post-Panel Consolidation	14	gi_bleed	61323	2	1	\N	\N
11820	Post-Panel Consolidation	16	gi_bleed	61323	0	1	\N	\N
11821	Post-Panel Consolidation	14	gi_bleed	49867	0	1	\N	Not DIC, more total coagulant deficiency
11822	Post-Panel Consolidation	2	gi_bleed	50737	-5	1	\N	\N
11823	Post-Panel Consolidation	14	gi_bleed	48871	0	1	\N	\N
11824	Post-Panel Consolidation	14	gi_bleed	46286	7	1	Coags	\N
11825	Post-Panel Consolidation	16	gi_bleed	46286	7	1	Coags	\N
11826	Post-Panel Consolidation	14	gi_bleed	45811	8	1	\N	\N
11827	Post-Panel Consolidation	15	gi_bleed	45811	8	1	\N	\N
11828	Post-Panel Consolidation	14	gi_bleed	45941	0	1	\N	\N
11829	Post-Panel Consolidation	14	gi_bleed	45866	2	1	\N	\N
11830	Post-Panel Consolidation	15	gi_bleed	45866	2	1	\N	\N
11831	Post-Panel Consolidation	2	gi_bleed	61832	0	1	\N	\N
11832	Post-Panel Consolidation	15	gi_bleed	46160	0	1	\N	\N
11833	Post-Panel Consolidation	15	gi_bleed	46078	0	1	\N	\N
11834	Post-Panel Consolidation	15	gi_bleed	63759	10	1	RBC	\N
11835	Post-Panel Consolidation	14	gi_bleed	46028	4	1	\N	\N
11836	Post-Panel Consolidation	14	gi_bleed	45872	9	1	FFP	\N
11837	Post-Panel Consolidation	15	gi_bleed	45872	9	1	FFP	\N
11838	Post-Panel Consolidation	16	gi_bleed	45872	9	1	FFP	\N
11839	Post-Panel Consolidation	14	gi_bleed	44237	6	1	Antibiotics	A bit overkill, but would cover GNRs
11840	Post-Panel Consolidation	14	gi_bleed	48724	5	1	\N	\N
11841	Post-Panel Consolidation	14	gi_bleed	45948	5	1	\N	\N
11842	Post-Panel Consolidation	15	gi_bleed	45948	5	1	\N	\N
11843	Post-Panel Consolidation	15	gi_bleed	45891	10	1	CBC	\N
11844	Post-Panel Consolidation	15	gi_bleed	46051	10	1	CBC	\N
11845	Post-Panel Consolidation	15	gi_bleed	46068	0	1	\N	\N
11846	Post-Panel Consolidation	14	gi_bleed	45910	7	1	Metabolic Panel	\N
11847	Post-Panel Consolidation	2	gi_bleed	62029	0	1	\N	Covered in hepatitis panel?
11848	Post-Panel Consolidation	14	gi_bleed	65649	4	1	\N	\N
11849	Post-Panel Consolidation	15	gi_bleed	62022	7	1	Intubation	\N
11850	Post-Panel Consolidation	14	gi_bleed	45942	8	1	Coags	\N
11851	Post-Panel Consolidation	15	gi_bleed	45838	0	1	Troponin	\N
11852	Post-Panel Consolidation	14	gi_bleed	48954	10	1	IV Access	Standard process that can be hard to distinguish, but include for particular relevance in this case
11853	Post-Panel Consolidation	15	gi_bleed	44978	0	1	\N	Peri-procedure sedation???
11854	Post-Panel Consolidation	14	gi_bleed	62151	2	1	Lactate	\N
11855	Post-Panel Consolidation	15	gi_bleed	62151	2	1	Lactate	\N
11856	Post-Panel Consolidation	16	gi_bleed	62151	2	1	Lactate	\N
11857	Post-Panel Consolidation	15	gi_bleed	46289	-2	1	Lactulose	\N
11858	Post-Panel Consolidation	15	gi_bleed	44302	-2	1	Lactulose	\N
11859	Post-Panel Consolidation	15	gi_bleed	44593	-2	1	Lactulose	\N
11860	Post-Panel Consolidation	14	gi_bleed	45903	0	1	\N	Hemolytic anemia eval?
11861	Post-Panel Consolidation	14	gi_bleed	62144	0	1	\N	\N
11862	Post-Panel Consolidation	14	gi_bleed	45894	0	1	\N	\N
11863	Post-Panel Consolidation	15	gi_bleed	45806	2	1	\N	\N
11864	Post-Panel Consolidation	14	gi_bleed	63745	0	1	\N	\N
11865	Post-Panel Consolidation	15	gi_bleed	63745	0	1	\N	\N
11866	Post-Panel Consolidation	14	gi_bleed	45763	8	1	Metabolic Panel	\N
11867	Post-Panel Consolidation	15	gi_bleed	45763	8	1	Metabolic Panel	\N
11868	Post-Panel Consolidation	2	gi_bleed	45763	8	1	Metabolic Panel	\N
11869	Post-Panel Consolidation	14	gi_bleed	45771	9	1	Metabolic Panel	\N
11870	Post-Panel Consolidation	15	gi_bleed	45771	9	1	Metabolic Panel	\N
11871	Post-Panel Consolidation	15	gi_bleed	45792	0	1	\N	\N
11872	Post-Panel Consolidation	14	gi_bleed	45785	0	1	\N	\N
11873	Post-Panel Consolidation	15	gi_bleed	36086	5	1	Vasopressors	\N
11874	Post-Panel Consolidation	14	gi_bleed	51110	0	1	\N	Largely irrelevant in acute setting
11875	Post-Panel Consolidation	14	gi_bleed	46451	-2	1	\N	\N
11876	Post-Panel Consolidation	15	gi_bleed	46451	-2	1	\N	\N
11877	Post-Panel Consolidation	14	gi_bleed	43996	10	1	\N	\N
11878	Post-Panel Consolidation	15	gi_bleed	43996	10	1	\N	\N
11879	Post-Panel Consolidation	16	gi_bleed	43996	10	1	\N	\N
11880	Post-Panel Consolidation	2	gi_bleed	43996	10	1	\N	\N
11881	Post-Panel Consolidation	15	gi_bleed	46449	-2	1	\N	\N
11882	Post-Panel Consolidation	14	gi_bleed	44216	2	1	\N	\N
11883	Post-Panel Consolidation	14	gi_bleed	45868	8	1	\N	\N
11884	Post-Panel Consolidation	14	gi_bleed	48822	0	1	Oxygen	No specific hypoxia in case
11885	Post-Panel Consolidation	14	gi_bleed	45900	0	1	Oxygen	No specific hypoxia in case
11886	Post-Panel Consolidation	14	gi_bleed	44219	10	1	\N	\N
11887	Post-Panel Consolidation	15	gi_bleed	44219	10	1	\N	\N
11888	Post-Panel Consolidation	16	gi_bleed	44219	10	1	\N	\N
11889	Post-Panel Consolidation	15	gi_bleed	44236	0	1	\N	\N
11890	Post-Panel Consolidation	14	gi_bleed	44236	0	1	\N	Mistake, should be giving oral med while vomiting blood
11891	Post-Panel Consolidation	15	gi_bleed	62171	0	1	\N	Active bleeding, probably not right time for para, though SBP always to consider?
11892	Post-Panel Consolidation	14	gi_bleed	61823	10	1	IV Access	\N
11893	Post-Panel Consolidation	15	gi_bleed	61823	10	1	IV Access	\N
11894	Post-Panel Consolidation	14	gi_bleed	45802	10	1	IV Access	\N
11895	Post-Panel Consolidation	15	gi_bleed	43993	3	1	Vasopressors	\N
11896	Post-Panel Consolidation	15	gi_bleed	45778	4	1	\N	\N
11897	Post-Panel Consolidation	2	gi_bleed	45778	4	1	\N	\N
11898	Post-Panel Consolidation	14	gi_bleed	45875	0	1	Platelets	\N
11899	Post-Panel Consolidation	15	gi_bleed	45875	0	1	Platelets	\N
11900	Post-Panel Consolidation	15	gi_bleed	45955	2	1	Lactate	\N
11901	Post-Panel Consolidation	14	gi_bleed	50267	0	1	\N	\N
11902	Post-Panel Consolidation	15	gi_bleed	44292	0	1	\N	Pre-procedure sedation?
11903	Post-Panel Consolidation	14	gi_bleed	49904	-2	1	\N	\N
11904	Post-Panel Consolidation	14	gi_bleed	45759	8	1	Coags	\N
11905	Post-Panel Consolidation	15	gi_bleed	45759	8	1	Coags	\N
11906	Post-Panel Consolidation	16	gi_bleed	45759	8	1	Coags	\N
11907	Post-Panel Consolidation	2	gi_bleed	45759	8	1	Coags	\N
11908	Post-Panel Consolidation	14	gi_bleed	45770	8	1	Coags	\N
11909	Post-Panel Consolidation	15	gi_bleed	45770	8	1	Coags	\N
11910	Post-Panel Consolidation	2	gi_bleed	45770	8	1	Coags	\N
11911	Post-Panel Consolidation	2	gi_bleed	62103	0	1	\N	\N
11912	Post-Panel Consolidation	14	gi_bleed	45927	10	1	RBC	\N
11913	Post-Panel Consolidation	15	gi_bleed	45927	10	1	RBC	\N
11914	Post-Panel Consolidation	16	gi_bleed	45927	10	1	RBC	\N
11915	Post-Panel Consolidation	2	gi_bleed	45927	10	1	RBC	\N
11916	Post-Panel Consolidation	15	gi_bleed	44424	0	1	\N	\N
11917	Post-Panel Consolidation	14	gi_bleed	49173	0	1	\N	?Intoxication not really active issue
11918	Post-Panel Consolidation	14	gi_bleed	44198	8	1	IVF	\N
11919	Post-Panel Consolidation	15	gi_bleed	44198	8	1	IVF	\N
11920	Post-Panel Consolidation	15	gi_bleed	44441	0	1	\N	?Pre-intubation for airway protection?
11921	Post-Panel Consolidation	14	gi_bleed	45877	8	1	Coagulopathy Correction	\N
11922	Post-Panel Consolidation	15	gi_bleed	45877	8	1	Coagulopathy Correction	\N
11923	Post-Panel Consolidation	16	gi_bleed	45877	8	1	Coagulopathy Correction	\N
11924	Post-Panel Consolidation	14	gi_bleed	65702	8	1	Coagulopathy Correction	\N
11925	Post-Panel Consolidation	15	gi_bleed	65702	8	1	Coagulopathy Correction	\N
11926	Post-Panel Consolidation	16	gi_bleed	65702	8	1	Coagulopathy Correction	\N
11927	Post-Panel Consolidation	14	gi_bleed	65646	0	1	Transfuse Platelets	\N
11928	Post-Panel Consolidation	15	gi_bleed	65646	0	1	Transfuse Platelets	\N
11929	Post-Panel Consolidation	15	gi_bleed	45956	0	1	Transfuse Platelets	\N
11930	Post-Panel Consolidation	14	gi_bleed	45956	0	1	Transfuse Platelets	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
11997	Post-Panel Consolidation	33	meningitis	48880	5	1	\N	\N
11931	Post-Panel Consolidation	15	gi_bleed	61976	0	1	Transfuse Platelets	Not sure necessary or appropriate to transfuse platelets given observed counts not low?
11932	Post-Panel Consolidation	14	gi_bleed	61975	10	1	Transfuse RBC	\N
11933	Post-Panel Consolidation	15	gi_bleed	61975	10	1	Transfuse RBC	\N
11934	Post-Panel Consolidation	16	gi_bleed	61975	10	1	Transfuse RBC	\N
11935	Post-Panel Consolidation	14	gi_bleed	45748	10	1	Transfuse RBC	\N
11936	Post-Panel Consolidation	15	gi_bleed	45748	10	1	Transfuse RBC	\N
11937	Post-Panel Consolidation	14	gi_bleed	65640	10	1	Transfuse RBC	\N
11938	Post-Panel Consolidation	15	gi_bleed	65640	10	1	Transfuse RBC	\N
11939	Post-Panel Consolidation	16	gi_bleed	65640	10	1	Transfuse RBC	\N
11940	Post-Panel Consolidation	2	gi_bleed	65640	10	1	Transfuse RBC	\N
11941	Post-Panel Consolidation	14	gi_bleed	50581	0	1	\N	\N
11942	Post-Panel Consolidation	15	gi_bleed	50581	0	1	\N	\N
11943	Post-Panel Consolidation	14	gi_bleed	50618	10	1	Transfuse RBC	\N
11944	Post-Panel Consolidation	15	gi_bleed	50618	10	1	Transfuse RBC	\N
11945	Post-Panel Consolidation	14	gi_bleed	45945	10	1	Type and Screen	\N
11946	Post-Panel Consolidation	15	gi_bleed	45945	10	1	Type and Screen	\N
11947	Post-Panel Consolidation	14	gi_bleed	45869	6	1	US Abdomen	\N
11948	Post-Panel Consolidation	2	gi_bleed	45869	6	1	US Abdomen	\N
11949	Post-Panel Consolidation	2	gi_bleed	49408	6	1	US Abdomen	\N
11950	Post-Panel Consolidation	14	gi_bleed	46343	6	1	US Abdomen	\N
11951	Post-Panel Consolidation	2	gi_bleed	46343	6	1	US Abdomen	\N
11952	Post-Panel Consolidation	14	gi_bleed	45969	10	1	GI EGD	\N
11953	Post-Panel Consolidation	15	gi_bleed	45969	10	1	GI EGD	\N
11954	Post-Panel Consolidation	16	gi_bleed	45969	10	1	GI EGD	\N
11955	Post-Panel Consolidation	14	gi_bleed	45873	0	1	\N	\N
11956	Post-Panel Consolidation	14	gi_bleed	46348	0	1	\N	\N
11957	Post-Panel Consolidation	14	gi_bleed	44001	7	1	Coagulopathy Correction	\N
11958	Post-Panel Consolidation	15	gi_bleed	44001	7	1	Coagulopathy Correction	\N
11959	Post-Panel Consolidation	16	gi_bleed	44001	7	1	Coagulopathy Correction	\N
11960	Post-Panel Consolidation	15	gi_bleed	44404	7	1	Coagulopathy Correction	\N
11961	Post-Panel Consolidation	16	gi_bleed	44404	7	1	Coagulopathy Correction	\N
11962	Post-Panel Consolidation	14	gi_bleed	44382	-2	1	\N	\N
11963	Post-Panel Consolidation	15	gi_bleed	44382	-2	1	\N	\N
11964	Post-Panel Consolidation	14	gi_bleed	46096	0	1	\N	\N
11965	Post-Panel Consolidation	14	gi_bleed	45818	0	1	CXR	\N
11966	Post-Panel Consolidation	15	gi_bleed	45818	0	1	CXR	\N
11967	Post-Panel Consolidation	14	gi_bleed	50200	0	1	CXR	Irrelevant diagnostic?
11968	Post-Panel Consolidation	14	gi_bleed	45801	0	1	CXR	\N
11969	Post-Panel Consolidation	30	meningitis	44281	5	1	Pain Control	\N
11970	Post-Panel Consolidation	31	meningitis	44281	5	1	Pain Control	\N
11971	Post-Panel Consolidation	30	meningitis	44278	5	1	Pain Control	\N
11972	Post-Panel Consolidation	30	meningitis	48829	0	1	\N	Irrelevant diagnostics. Probably trying to order medicine
11973	Post-Panel Consolidation	30	meningitis	44615	0	1	\N	\N
11974	Post-Panel Consolidation	31	meningitis	44615	0	1	\N	\N
11975	Post-Panel Consolidation	33	meningitis	44615	0	1	\N	\N
11976	Post-Panel Consolidation	30	meningitis	48770	0	1	\N	Low yield
11977	Post-Panel Consolidation	33	meningitis	48770	0	1	\N	Low yield
11978	Post-Panel Consolidation	30	meningitis	44595	0	1	\N	\N
11979	Post-Panel Consolidation	31	meningitis	44595	0	1	\N	\N
11980	Post-Panel Consolidation	33	meningitis	44595	0	1	\N	\N
11981	Post-Panel Consolidation	30	meningitis	46093	5	1	Pregnancy Test	\N
11982	Post-Panel Consolidation	30	meningitis	45901	10	1	Blood Culture	\N
11983	Post-Panel Consolidation	31	meningitis	45901	10	1	Blood Culture	\N
11984	Post-Panel Consolidation	33	meningitis	45901	10	1	Blood Culture	\N
11985	Post-Panel Consolidation	30	meningitis	45752	10	1	Blood Culture	\N
11986	Post-Panel Consolidation	31	meningitis	45752	10	1	Blood Culture	\N
11987	Post-Panel Consolidation	33	meningitis	45752	10	1	Blood Culture	\N
11988	Post-Panel Consolidation	30	meningitis	44290	5	1	IVF	\N
11989	Post-Panel Consolidation	30	meningitis	44439	5	1	IVF	\N
11990	Post-Panel Consolidation	30	meningitis	45793	7	1	CBC	\N
11991	Post-Panel Consolidation	30	meningitis	45788	7	1	CBC	\N
11992	Post-Panel Consolidation	33	meningitis	36210	5	1	Antibiotics	\N
11993	Post-Panel Consolidation	30	meningitis	35733	10	1	Antibiotics	\N
11994	Post-Panel Consolidation	31	meningitis	35733	10	1	Antibiotics	\N
11995	Post-Panel Consolidation	33	meningitis	35733	5	1	Antibiotics	\N
11996	Post-Panel Consolidation	30	meningitis	48880	10	1	\N	\N
11998	Post-Panel Consolidation	30	meningitis	50930	0	1	\N	Wrong order. Synovial fluid not CSF
11999	Post-Panel Consolidation	30	meningitis	49079	0	1	\N	\N
12000	Post-Panel Consolidation	33	meningitis	48603	0	1	\N	Not relevant to test?
12001	Post-Panel Consolidation	33	meningitis	61973	0	1	\N	Not relevant to test?
12002	Post-Panel Consolidation	33	meningitis	48752	0	1	\N	Not relevant to test?
12003	Post-Panel Consolidation	33	meningitis	61826	0	1	\N	\N
12004	Post-Panel Consolidation	30	meningitis	61826	0	1	\N	Not relevant to test?
12005	Post-Panel Consolidation	31	meningitis	49649	0	1	\N	\N
12006	Post-Panel Consolidation	33	meningitis	49594	0	1	\N	\N
12007	Post-Panel Consolidation	30	meningitis	49594	0	1	\N	No good indication
12008	Post-Panel Consolidation	30	meningitis	49083	10	1	\N	\N
12009	Post-Panel Consolidation	33	meningitis	49083	5	1	\N	\N
12010	Post-Panel Consolidation	30	meningitis	50692	4	1	\N	\N
12011	Post-Panel Consolidation	30	meningitis	48871	0	1	\N	\N
12012	Post-Panel Consolidation	30	meningitis	44017	10	1	\N	\N
12013	Post-Panel Consolidation	31	meningitis	44017	10	1	\N	\N
12014	Post-Panel Consolidation	33	meningitis	44017	9	1	\N	\N
12015	Post-Panel Consolidation	33	meningitis	35969	-5	1	\N	\N
12016	Post-Panel Consolidation	30	meningitis	46286	5	1	Coags	\N
12017	Post-Panel Consolidation	30	meningitis	45811	2	1	\N	\N
12018	Post-Panel Consolidation	30	meningitis	49054	6	1	\N	\N
12019	Post-Panel Consolidation	31	meningitis	49054	6	1	\N	\N
12020	Post-Panel Consolidation	30	meningitis	45866	0	1	\N	\N
12021	Post-Panel Consolidation	31	meningitis	45866	0	1	\N	\N
12022	Post-Panel Consolidation	33	meningitis	63761	1	1	\N	Common meningitis cause, okay to review
12023	Post-Panel Consolidation	33	meningitis	49142	1	1	\N	Common meningitis cause, okay to review
12024	Post-Panel Consolidation	30	meningitis	46103	0	1	\N	\N
12025	Post-Panel Consolidation	30	meningitis	50685	0	1	\N	Mostly irrelevant STD testing?
12026	Post-Panel Consolidation	30	meningitis	48577	10	1	\N	\N
12027	Post-Panel Consolidation	33	meningitis	48577	10	1	\N	Doesn't match CSF cell count pattern of less points if delayed to worsened?
12028	Post-Panel Consolidation	30	meningitis	42197	0	1	\N	\N
12029	Post-Panel Consolidation	30	meningitis	49109	7	1	HSV CSF	\N
12030	Post-Panel Consolidation	30	meningitis	62011	0	1	\N	Not the right screening test for HIV
12031	Post-Panel Consolidation	30	meningitis	63767	7	1	HSV CSF	\N
12032	Post-Panel Consolidation	31	meningitis	63767	7	1	HSV CSF	\N
12033	Post-Panel Consolidation	33	meningitis	63767	7	1	HSV CSF	\N
12034	Post-Panel Consolidation	30	meningitis	44319	2	1	Pain Control	\N
12035	Post-Panel Consolidation	30	meningitis	48732	0	1	\N	Blood gases?
12036	Post-Panel Consolidation	30	meningitis	62151	5	1	Lactate	\N
12037	Post-Panel Consolidation	31	meningitis	62151	5	1	Lactate	\N
12038	Post-Panel Consolidation	33	meningitis	62151	5	1	Lactate	\N
12039	Post-Panel Consolidation	30	meningitis	45918	5	1	Lactate	\N
12040	Post-Panel Consolidation	33	meningitis	45918	5	1	Lactate	\N
12041	Post-Panel Consolidation	33	meningitis	50510	5	1	\N	\N
12042	Post-Panel Consolidation	30	meningitis	45763	5	1	Metabolic Panel	\N
12043	Post-Panel Consolidation	30	meningitis	45771	5	1	Metabolic Panel	\N
12044	Post-Panel Consolidation	31	meningitis	44199	0	1	\N	Symptomatic management
12045	Post-Panel Consolidation	31	meningitis	45792	0	1	\N	\N
12046	Post-Panel Consolidation	30	meningitis	45792	0	1	\N	\N
12047	Post-Panel Consolidation	30	meningitis	61852	0	1	\N	\N
12048	Post-Panel Consolidation	30	meningitis	61823	0	1	\N	\N
12049	Post-Panel Consolidation	31	meningitis	49334	0	1	\N	Irrelevant?
12050	Post-Panel Consolidation	30	meningitis	46090	0	1	\N	\N
12051	Post-Panel Consolidation	30	meningitis	45955	5	1	Lactate	\N
12052	Post-Panel Consolidation	33	meningitis	49134	5	1	Pregnancy Test	\N
12053	Post-Panel Consolidation	30	meningitis	62042	2	1	\N	\N
12054	Post-Panel Consolidation	30	meningitis	49020	10	1	\N	\N
12055	Post-Panel Consolidation	33	meningitis	49020	5	1	\N	\N
12056	Post-Panel Consolidation	31	meningitis	45776	0	1	\N	Process
12057	Post-Panel Consolidation	30	meningitis	62103	5	1	HIV Test	\N
12058	Post-Panel Consolidation	33	meningitis	62103	5	1	HIV Test	\N
12059	Post-Panel Consolidation	30	meningitis	48728	0	1	\N	\N
12060	Post-Panel Consolidation	31	meningitis	48728	0	1	\N	\N
12061	Post-Panel Consolidation	30	meningitis	63923	3	1	\N	\N
12062	Post-Panel Consolidation	30	meningitis	63725	5	1	Lactate	\N
12063	Post-Panel Consolidation	31	meningitis	63725	5	1	Lactate	\N
12064	Post-Panel Consolidation	30	meningitis	44198	5	1	IVF	\N
12065	Post-Panel Consolidation	33	meningitis	44198	5	1	IVF	\N
12066	Post-Panel Consolidation	30	meningitis	46131	0	1	\N	\N
12067	Post-Panel Consolidation	30	meningitis	45751	0	1	\N	\N
12068	Post-Panel Consolidation	33	meningitis	45751	0	1	\N	\N
12069	Post-Panel Consolidation	30	meningitis	45873	0	1	\N	\N
12070	Post-Panel Consolidation	31	meningitis	45873	0	1	\N	\N
12071	Post-Panel Consolidation	30	meningitis	43997	10	1	\N	\N
12072	Post-Panel Consolidation	31	meningitis	43997	10	1	\N	\N
12073	Post-Panel Consolidation	33	meningitis	43997	5	1	\N	\N
12074	Post-Panel Consolidation	33	meningitis	48486	2	1	Vancomycin Level	Okay to check followup leels
12075	Post-Panel Consolidation	30	meningitis	45972	2	1	Vancomycin Level	Okay to check followup leels
12076	Post-Panel Consolidation	33	meningitis	45972	2	1	Vancomycin Level	Okay to check followup leels
12077	Post-Panel Consolidation	33	meningitis	48519	0	1	\N	\N
12078	Post-Panel Consolidation	33	meningitis	48529	0	1	\N	\N
12079	Post-Panel Consolidation	30	meningitis	63735	0	1	\N	\N
12080	Post-Panel Consolidation	30	meningitis	45766	0	1	\N	\N
12081	Post-Panel Consolidation	30	meningitis	50654	0	1	\N	\N
12082	Post-Panel Consolidation	33	meningitis	50654	0	1	\N	\N
12083	Post-Panel Consolidation	30	meningitis	45818	3	1	CXR	\N
12084	Post-Panel Consolidation	31	meningitis	45818	3	1	CXR	\N
12085	Post-Panel Consolidation	33	meningitis	45818	3	1	CXR	\N
12086	Post-Panel Consolidation	5002	neutropenic	44281	4	1	Acetaminophen	\N
12087	Post-Panel Consolidation	5000	neutropenic	44281	4	1	Acetaminophen	\N
12088	Post-Panel Consolidation	5002	neutropenic	65641	0	1	\N	Process
12089	Post-Panel Consolidation	5000	neutropenic	48775	0	1	\N	\N
12090	Post-Panel Consolidation	5002	neutropenic	46157	10	1	Blood Cultures	\N
12091	Post-Panel Consolidation	5002	neutropenic	46291	10	1	Blood Cultures	\N
12092	Post-Panel Consolidation	5002	neutropenic	45901	10	1	Blood Cultures	\N
12093	Post-Panel Consolidation	5000	neutropenic	45901	10	1	Blood Cultures	\N
12094	Post-Panel Consolidation	5002	neutropenic	45752	10	1	Blood Cultures	\N
12095	Post-Panel Consolidation	5000	neutropenic	45752	10	1	Blood Cultures	\N
12096	Post-Panel Consolidation	5000	neutropenic	45760	6	1	Blood Gas	\N
12097	Post-Panel Consolidation	5003	neutropenic	44395	10	1	IVF	\N
12098	Post-Panel Consolidation	5000	neutropenic	44290	10	1	IVF	\N
12099	Post-Panel Consolidation	5002	neutropenic	45788	8	1	CBC	\N
12100	Post-Panel Consolidation	5000	neutropenic	45788	8	1	CBC	\N
12101	Post-Panel Consolidation	5000	neutropenic	45966	8	1	CBC	\N
12102	Post-Panel Consolidation	5002	neutropenic	36210	10	1	Anti-Pseudomonas	\N
12103	Post-Panel Consolidation	5000	neutropenic	36210	10	1	Anti-Pseudomonas	\N
12104	Post-Panel Consolidation	5003	neutropenic	36210	10	1	Anti-Pseudomonas	\N
12105	Post-Panel Consolidation	5002	neutropenic	50547	0	1	\N	Consult
12106	Post-Panel Consolidation	5002	neutropenic	48980	0	1	\N	Consult
12107	Post-Panel Consolidation	5003	neutropenic	49228	0	1	\N	Consult
12108	Post-Panel Consolidation	5002	neutropenic	48711	0	1	\N	Wrong type of isolation
12109	Post-Panel Consolidation	5000	neutropenic	48532	0	1	\N	\N
12110	Post-Panel Consolidation	5003	neutropenic	46286	5	1	Coags	\N
12111	Post-Panel Consolidation	5003	neutropenic	48686	2	1	\N	\N
12112	Post-Panel Consolidation	5000	neutropenic	48686	2	1	\N	\N
12113	Post-Panel Consolidation	5003	neutropenic	46004	0	1	\N	\N
12114	Post-Panel Consolidation	5003	neutropenic	45811	0	1	\N	Unnecessary?
12115	Post-Panel Consolidation	5000	neutropenic	49054	5	1	\N	\N
12116	Post-Panel Consolidation	5002	neutropenic	45866	4	1	\N	\N
12117	Post-Panel Consolidation	5003	neutropenic	45866	4	1	\N	\N
12118	Post-Panel Consolidation	5000	neutropenic	45866	4	1	\N	\N
12119	Post-Panel Consolidation	5000	neutropenic	46160	0	1	\N	Process
12120	Post-Panel Consolidation	5000	neutropenic	41759	0	1	\N	Presenting symptom
12121	Post-Panel Consolidation	5002	neutropenic	45225	7	1	\N	Reduce hospitalized neutropenic time
12122	Post-Panel Consolidation	5002	neutropenic	44237	10	1	Anti-Pseudomonas	\N
12123	Post-Panel Consolidation	5000	neutropenic	44237	10	1	Anti-Pseudomonas	\N
12124	Post-Panel Consolidation	5002	neutropenic	44252	10	1	Anti-Pseudomonas	\N
12125	Post-Panel Consolidation	5002	neutropenic	46006	0	1	\N	\N
12126	Post-Panel Consolidation	5000	neutropenic	46020	2	1	\N	\N
12127	Post-Panel Consolidation	5002	neutropenic	62151	10	1	Lactate	\N
12128	Post-Panel Consolidation	5003	neutropenic	62151	10	1	Lactate	\N
12129	Post-Panel Consolidation	5000	neutropenic	62151	10	1	Lactate	\N
12130	Post-Panel Consolidation	5000	neutropenic	45903	2	1	\N	\N
12131	Post-Panel Consolidation	5002	neutropenic	45806	3	1	\N	\N
12132	Post-Panel Consolidation	5002	neutropenic	45763	10	1	Metabolic Panel	\N
12133	Post-Panel Consolidation	5000	neutropenic	45763	10	1	Metabolic Panel	\N
12134	Post-Panel Consolidation	5002	neutropenic	45771	10	1	Metabolic Panel	\N
12135	Post-Panel Consolidation	5000	neutropenic	45771	10	1	Metabolic Panel	\N
12136	Post-Panel Consolidation	5002	neutropenic	45792	2	1	\N	\N
12137	Post-Panel Consolidation	5003	neutropenic	45792	2	1	\N	\N
12138	Post-Panel Consolidation	5002	neutropenic	48960	8	1	\N	\N
12139	Post-Panel Consolidation	5003	neutropenic	48960	8	1	\N	\N
12140	Post-Panel Consolidation	5000	neutropenic	48960	8	1	\N	\N
12141	Post-Panel Consolidation	5000	neutropenic	44420	0	1	\N	Symptom management
12142	Post-Panel Consolidation	5000	neutropenic	45900	0	1	\N	Irrelevant
12143	Post-Panel Consolidation	5003	neutropenic	45778	0	1	\N	\N
12144	Post-Panel Consolidation	5002	neutropenic	50554	0	1	\N	Irrelevant
12145	Post-Panel Consolidation	5003	neutropenic	50554	0	1	\N	Irrelevant
12146	Post-Panel Consolidation	5000	neutropenic	45955	10	1	Lactate	\N
12147	Post-Panel Consolidation	5000	neutropenic	46000	0	1	\N	\N
12148	Post-Panel Consolidation	5002	neutropenic	45759	4	1	Coags	\N
12149	Post-Panel Consolidation	5002	neutropenic	45770	4	1	Coags	\N
12150	Post-Panel Consolidation	5000	neutropenic	45890	0	1	\N	\N
12151	Post-Panel Consolidation	5000	neutropenic	62023	6	1	Respiratory Virus Screen	\N
12152	Post-Panel Consolidation	5002	neutropenic	63923	6	1	Respiratory Virus Screen	\N
12153	Post-Panel Consolidation	5000	neutropenic	63923	6	1	Respiratory Virus Screen	\N
12154	Post-Panel Consolidation	5003	neutropenic	63725	10	1	Lactate	\N
12155	Post-Panel Consolidation	5000	neutropenic	63725	10	1	Lactate	\N
12156	Post-Panel Consolidation	5002	neutropenic	44198	10	1	IVF	\N
12157	Post-Panel Consolidation	5003	neutropenic	44198	10	1	IVF	\N
12158	Post-Panel Consolidation	5000	neutropenic	44198	10	1	IVF	\N
12159	Post-Panel Consolidation	5000	neutropenic	45945	1	1	\N	Anticipating transfusions, but not needed now
12160	Post-Panel Consolidation	5000	neutropenic	45995	3	1	\N	\N
12161	Post-Panel Consolidation	5000	neutropenic	45751	6	1	UA + Culture	\N
12162	Post-Panel Consolidation	5000	neutropenic	45873	6	1	UA + Culture	\N
12163	Post-Panel Consolidation	5002	neutropenic	45782	6	1	UA + Culture	\N
12164	Post-Panel Consolidation	5003	neutropenic	45782	6	1	UA + Culture	\N
12165	Post-Panel Consolidation	5000	neutropenic	45782	6	1	UA + Culture	\N
12166	Post-Panel Consolidation	5002	neutropenic	43997	2	1	\N	\N
12167	Post-Panel Consolidation	5003	neutropenic	43997	2	1	\N	\N
12168	Post-Panel Consolidation	5000	neutropenic	43997	2	1	\N	\N
12169	Post-Panel Consolidation	5000	neutropenic	45972	2	1	\N	\N
12170	Post-Panel Consolidation	5002	neutropenic	63735	0	1	\N	\N
12171	Post-Panel Consolidation	5003	neutropenic	63735	0	1	\N	\N
12172	Post-Panel Consolidation	5000	neutropenic	45766	0	1	\N	Process
12173	Post-Panel Consolidation	5002	neutropenic	45818	10	1	CXR	\N
12174	Post-Panel Consolidation	5003	neutropenic	45818	10	1	CXR	\N
12175	Post-Panel Consolidation	5000	neutropenic	45818	10	1	CXR	\N
12176	Post-Panel Consolidation	5002	neutropenic	45801	10	1	CXR	\N
12177	Post-Panel Consolidation	5000	neutropenic	45801	10	1	CXR	\N
12178	Post-Panel Consolidation	11	pulmonary_embolism	65641	0	1	\N	Process
12179	Post-Panel Consolidation	10	pulmonary_embolism	44330	7	1	Nebs	\N
12180	Post-Panel Consolidation	11	pulmonary_embolism	44330	7	1	Nebs	\N
12181	Post-Panel Consolidation	11	pulmonary_embolism	44595	0	1	\N	Weird antibiotic choice?
12182	Post-Panel Consolidation	10	pulmonary_embolism	44206	4	1	Aspirin	\N
12183	Post-Panel Consolidation	11	pulmonary_embolism	44206	4	1	Aspirin	\N
12184	Post-Panel Consolidation	8	pulmonary_embolism	46551	0	1	\N	\N
12185	Post-Panel Consolidation	10	pulmonary_embolism	35849	6	1	Azithromycin	\N
12186	Post-Panel Consolidation	12	pulmonary_embolism	35849	6	1	Azithromycin	\N
12187	Post-Panel Consolidation	11	pulmonary_embolism	35849	6	1	Azithromycin	\N
12188	Post-Panel Consolidation	10	pulmonary_embolism	44388	6	1	Azithromycin	\N
12189	Post-Panel Consolidation	11	pulmonary_embolism	44388	6	1	Azithromycin	\N
12190	Post-Panel Consolidation	11	pulmonary_embolism	45901	5	1	Blood Cultures	\N
12191	Post-Panel Consolidation	11	pulmonary_embolism	45752	5	1	Blood Cultures	\N
12192	Post-Panel Consolidation	10	pulmonary_embolism	45760	7	1	Blood Gas	\N
12193	Post-Panel Consolidation	12	pulmonary_embolism	45760	7	1	Blood Gas	\N
12194	Post-Panel Consolidation	10	pulmonary_embolism	45919	5	1	Blood Gas	\N
12195	Post-Panel Consolidation	12	pulmonary_embolism	45919	5	1	Blood Gas	\N
12196	Post-Panel Consolidation	11	pulmonary_embolism	45919	5	1	Blood Gas	\N
12197	Post-Panel Consolidation	10	pulmonary_embolism	44439	0	1	IVF	\N
12198	Post-Panel Consolidation	10	pulmonary_embolism	45793	10	1	CBC	\N
12199	Post-Panel Consolidation	11	pulmonary_embolism	45793	10	1	CBC	\N
12200	Post-Panel Consolidation	10	pulmonary_embolism	45788	10	1	CBC	\N
12201	Post-Panel Consolidation	11	pulmonary_embolism	45788	10	1	CBC	\N
12202	Post-Panel Consolidation	10	pulmonary_embolism	35733	6	1	\N	\N
12203	Post-Panel Consolidation	11	pulmonary_embolism	35733	6	1	\N	\N
12204	Post-Panel Consolidation	11	pulmonary_embolism	45892	0	1	\N	Superceded by troponin if needed at all
12205	Post-Panel Consolidation	10	pulmonary_embolism	49251	0	1	\N	\N
12206	Post-Panel Consolidation	11	pulmonary_embolism	49251	0	1	\N	\N
12207	Post-Panel Consolidation	10	pulmonary_embolism	61323	0	1	\N	Consult
12208	Post-Panel Consolidation	11	pulmonary_embolism	61323	0	1	\N	Consult
12209	Post-Panel Consolidation	12	pulmonary_embolism	49207	0	1	\N	Consult
12210	Post-Panel Consolidation	11	pulmonary_embolism	50509	0	1	\N	\N
12211	Post-Panel Consolidation	10	pulmonary_embolism	48522	10	1	CT Chest	\N
12212	Post-Panel Consolidation	11	pulmonary_embolism	48522	10	1	CT Chest	\N
12213	Post-Panel Consolidation	10	pulmonary_embolism	45762	7	1	CT Chest	\N
12214	Post-Panel Consolidation	11	pulmonary_embolism	45762	7	1	CT Chest	\N
12215	Post-Panel Consolidation	10	pulmonary_embolism	48676	10	1	CT Chest	\N
12216	Post-Panel Consolidation	11	pulmonary_embolism	48676	10	1	CT Chest	\N
12217	Post-Panel Consolidation	10	pulmonary_embolism	48871	5	1	D-Dimer	\N
12218	Post-Panel Consolidation	11	pulmonary_embolism	48871	5	1	D-Dimer	\N
12219	Post-Panel Consolidation	10	pulmonary_embolism	48532	5	1	D-Dimer	\N
12220	Post-Panel Consolidation	11	pulmonary_embolism	48532	5	1	D-Dimer	\N
12221	Post-Panel Consolidation	10	pulmonary_embolism	44017	5	1	Corticosteroids	Main issue is PE, but could reasonably say it's triggering a COPD exacerbation as well
12222	Post-Panel Consolidation	10	pulmonary_embolism	45811	2	1	NPO	\N
12223	Post-Panel Consolidation	12	pulmonary_embolism	45811	2	1	NPO	\N
12224	Post-Panel Consolidation	10	pulmonary_embolism	49054	5	1	\N	\N
12225	Post-Panel Consolidation	10	pulmonary_embolism	45866	7	1	\N	\N
12226	Post-Panel Consolidation	11	pulmonary_embolism	45866	7	1	\N	\N
12227	Post-Panel Consolidation	10	pulmonary_embolism	61832	6	1	Echo	\N
12228	Post-Panel Consolidation	11	pulmonary_embolism	61832	6	1	Echo	\N
12229	Post-Panel Consolidation	8	pulmonary_embolism	61832	6	1	Echo	\N
12230	Post-Panel Consolidation	10	pulmonary_embolism	46160	0	1	\N	Process
12231	Post-Panel Consolidation	11	pulmonary_embolism	46160	0	1	\N	Process
12232	Post-Panel Consolidation	11	pulmonary_embolism	44250	10	1	Anticoagulation	\N
12233	Post-Panel Consolidation	11	pulmonary_embolism	61978	-5	1	\N	\N
12234	Post-Panel Consolidation	10	pulmonary_embolism	44004	0	1	\N	\N
12235	Post-Panel Consolidation	11	pulmonary_embolism	44004	0	1	\N	\N
12236	Post-Panel Consolidation	11	pulmonary_embolism	45797	1	1	\N	\N
12237	Post-Panel Consolidation	10	pulmonary_embolism	46438	10	1	Anticoagulation	\N
12238	Post-Panel Consolidation	10	pulmonary_embolism	44359	10	1	Anticoagulation	\N
12239	Post-Panel Consolidation	11	pulmonary_embolism	44359	10	1	Anticoagulation	\N
12240	Post-Panel Consolidation	10	pulmonary_embolism	46183	0	1	\N	Just count of part heparin protocol
12241	Post-Panel Consolidation	10	pulmonary_embolism	63714	0	1	\N	Just count of part heparin protocol
12242	Post-Panel Consolidation	11	pulmonary_embolism	63714	0	1	\N	Just count of part heparin protocol
12243	Post-Panel Consolidation	8	pulmonary_embolism	49301	7	1	Blood Gas	\N
12244	Post-Panel Consolidation	10	pulmonary_embolism	45838	6	1	Troponin	\N
12245	Post-Panel Consolidation	10	pulmonary_embolism	62151	5	1	Lactate	\N
12246	Post-Panel Consolidation	10	pulmonary_embolism	62144	0	1	\N	Not sure?
12247	Post-Panel Consolidation	11	pulmonary_embolism	61837	0	1	\N	\N
12248	Post-Panel Consolidation	10	pulmonary_embolism	44213	0	1	\N	Like asthma exacerbation treatment?
12249	Post-Panel Consolidation	11	pulmonary_embolism	45806	5	1	\N	Not sure why so much points?
12250	Post-Panel Consolidation	10	pulmonary_embolism	45763	10	1	Metabolic Panel	\N
12251	Post-Panel Consolidation	11	pulmonary_embolism	45763	10	1	Metabolic Panel	\N
12252	Post-Panel Consolidation	10	pulmonary_embolism	45771	10	1	Metabolic Panel	\N
12253	Post-Panel Consolidation	11	pulmonary_embolism	45771	10	1	Metabolic Panel	\N
12254	Post-Panel Consolidation	10	pulmonary_embolism	44586	5	1	Corticosteroids	\N
12255	Post-Panel Consolidation	11	pulmonary_embolism	44586	5	1	Corticosteroids	\N
12256	Post-Panel Consolidation	11	pulmonary_embolism	45792	4	1	\N	\N
12257	Post-Panel Consolidation	11	pulmonary_embolism	44228	4	1	\N	\N
12258	Post-Panel Consolidation	11	pulmonary_embolism	48628	0	1	\N	\N
12259	Post-Panel Consolidation	11	pulmonary_embolism	46081	0	1	\N	\N
12260	Post-Panel Consolidation	10	pulmonary_embolism	50235	0	1	NIPPV	\N
12261	Post-Panel Consolidation	12	pulmonary_embolism	50235	0	1	NIPPV	\N
12262	Post-Panel Consolidation	10	pulmonary_embolism	45853	6	1	\N	\N
12263	Post-Panel Consolidation	11	pulmonary_embolism	45853	6	1	\N	\N
12264	Post-Panel Consolidation	10	pulmonary_embolism	45750	2	1	\N	Process?
12265	Post-Panel Consolidation	11	pulmonary_embolism	45787	0	1	\N	Process
12266	Post-Panel Consolidation	11	pulmonary_embolism	51290	10	1	Oxygen	\N
12267	Post-Panel Consolidation	10	pulmonary_embolism	51290	10	1	Oxygen	\N
12268	Post-Panel Consolidation	10	pulmonary_embolism	45864	10	1	Oxygen	\N
12269	Post-Panel Consolidation	12	pulmonary_embolism	45864	10	1	Oxygen	\N
12270	Post-Panel Consolidation	10	pulmonary_embolism	48822	10	1	Oxygen	\N
12271	Post-Panel Consolidation	12	pulmonary_embolism	48822	10	1	Oxygen	\N
12272	Post-Panel Consolidation	10	pulmonary_embolism	45900	10	1	Oxygen	\N
12273	Post-Panel Consolidation	12	pulmonary_embolism	45900	10	1	Oxygen	\N
12274	Post-Panel Consolidation	10	pulmonary_embolism	46090	0	1	\N	Heparin protocol
12275	Post-Panel Consolidation	10	pulmonary_embolism	45914	6	1	Troponin	\N
12276	Post-Panel Consolidation	10	pulmonary_embolism	50773	7	1	Blood Gas	\N
12277	Post-Panel Consolidation	10	pulmonary_embolism	50503	5	1	Blood Gas	\N
12278	Post-Panel Consolidation	10	pulmonary_embolism	45955	5	1	Blood Gas	\N
12279	Post-Panel Consolidation	11	pulmonary_embolism	45955	5	1	Blood Gas	\N
12280	Post-Panel Consolidation	8	pulmonary_embolism	50267	0	1	\N	\N
12281	Post-Panel Consolidation	10	pulmonary_embolism	44011	5	1	Corticosteroids	\N
12282	Post-Panel Consolidation	11	pulmonary_embolism	44011	5	1	Corticosteroids	\N
12283	Post-Panel Consolidation	11	pulmonary_embolism	62042	5	1	\N	\N
12284	Post-Panel Consolidation	10	pulmonary_embolism	45759	10	1	Coags	\N
12285	Post-Panel Consolidation	11	pulmonary_embolism	45759	10	1	Coags	\N
12286	Post-Panel Consolidation	8	pulmonary_embolism	45759	10	1	Coags	\N
12287	Post-Panel Consolidation	8	pulmonary_embolism	49268	0	1	\N	\N
12288	Post-Panel Consolidation	11	pulmonary_embolism	45770	10	1	Coags	\N
12289	Post-Panel Consolidation	8	pulmonary_embolism	45770	10	1	Coags	\N
12290	Post-Panel Consolidation	11	pulmonary_embolism	63730	0	1	\N	Not for acute TB even if that was the diagnosis?
12291	Post-Panel Consolidation	8	pulmonary_embolism	62175	4	1	\N	For biopsy?
12292	Post-Panel Consolidation	10	pulmonary_embolism	46030	0	1	NIPPV	\N
12293	Post-Panel Consolidation	11	pulmonary_embolism	46030	0	1	NIPPV	\N
12294	Post-Panel Consolidation	10	pulmonary_embolism	45921	10	1	Oxygen	\N
12295	Post-Panel Consolidation	12	pulmonary_embolism	45921	10	1	Oxygen	\N
12296	Post-Panel Consolidation	11	pulmonary_embolism	45921	10	1	Oxygen	\N
12297	Post-Panel Consolidation	11	pulmonary_embolism	46336	0	1	\N	Override, process order
12298	Post-Panel Consolidation	11	pulmonary_embolism	48544	5	1	Respiratory Culture	\N
12299	Post-Panel Consolidation	11	pulmonary_embolism	62023	5	1	Respiratory Virus Screen	\N
12300	Post-Panel Consolidation	10	pulmonary_embolism	63923	5	1	Respiratory Virus Screen	\N
12301	Post-Panel Consolidation	11	pulmonary_embolism	63923	5	1	Respiratory Virus Screen	\N
12302	Post-Panel Consolidation	11	pulmonary_embolism	60178	10	1	Anticoagulation	\N
12303	Post-Panel Consolidation	12	pulmonary_embolism	60178	10	1	Anticoagulation	\N
12304	Post-Panel Consolidation	10	pulmonary_embolism	41796	0	1	\N	Presenting Symptom Diagnosis
12305	Post-Panel Consolidation	12	pulmonary_embolism	44198	0	1	IVF	\N
12306	Post-Panel Consolidation	8	pulmonary_embolism	44313	0	1	\N	Nebs, but this is more for long term use
12307	Post-Panel Consolidation	10	pulmonary_embolism	45870	6	1	Troponin	\N
12308	Post-Panel Consolidation	11	pulmonary_embolism	45870	6	1	Troponin	\N
12309	Post-Panel Consolidation	8	pulmonary_embolism	45870	6	1	Troponin	\N
12310	Post-Panel Consolidation	11	pulmonary_embolism	45945	0	1	\N	\N
12311	Post-Panel Consolidation	8	pulmonary_embolism	65672	4	1	DVT US	\N
12312	Post-Panel Consolidation	11	pulmonary_embolism	45751	0	1	\N	\N
12313	Post-Panel Consolidation	10	pulmonary_embolism	45751	0	1	\N	\N
12314	Post-Panel Consolidation	11	pulmonary_embolism	45911	0	1	\N	Process
12315	Post-Panel Consolidation	10	pulmonary_embolism	45818	10	1	CXR	\N
12316	Post-Panel Consolidation	11	pulmonary_embolism	45818	10	1	CXR	\N
12317	Post-Panel Consolidation	10	pulmonary_embolism	50200	10	1	CXR	\N
12318	Post-Panel Consolidation	10	pulmonary_embolism	45801	10	1	CXR	\N
12319	Post-Panel Consolidation	11	pulmonary_embolism	45801	10	1	CXR	\N
\.


--
-- Name: sim_grading_key_sim_grading_key_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_grading_key_sim_grading_key_id_seq', 12319, true);


--
-- PostgreSQL database dump complete
--

