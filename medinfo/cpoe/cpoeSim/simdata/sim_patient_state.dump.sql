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
-- Data for Name: sim_patient_state; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_patient_state (sim_patient_state_id, sim_patient_id, sim_state_id, relative_time_start, relative_time_end) FROM stdin;
9	9	3	-7200	\N
13	6	6	-14400	\N
7	7	7	-7200	\N
15	13	3	-7200	\N
16	14	6	-14400	\N
17	15	7	-7200	\N
20	18	7	-7200	\N
21	19	3	-7200	\N
22	20	6	-14400	\N
23	5	13	-7200	0
24	5	14	0	\N
42	23	13	-7200	0
44	24	3	-7200	\N
45	25	6	-14400	\N
8	8	9	-36000	0
18	16	9	-36000	0
19	17	9	-36000	0
41	22	9	-36000	0
49	16	21	0	\N
50	17	21	0	\N
51	22	21	0	\N
47	8	21	0	1440
53	8	18	1440	\N
43	23	14	0	0
54	23	17	0	0
55	23	15	0	1620
56	23	14	1620	1620
57	23	14	1620	4800
58	23	16	4800	4860
59	23	2	4860	\N
63	28	9	-36000	0
65	29	3	-7200	\N
66	30	6	-14400	\N
67	31	13	-7200	0
64	28	21	0	2580
69	28	18	2580	\N
68	31	14	0	0
70	31	17	0	0
71	31	15	0	1680
72	31	14	1680	1860
73	31	16	1860	2940
74	31	2	2940	\N
75	32	3	-7200	\N
76	33	9	-36000	0
78	34	6	-14400	\N
79	35	13	-7200	0
77	33	21	0	1980
81	33	18	1980	5580
82	33	20	5580	\N
80	35	14	0	300
83	35	14	300	480
84	35	17	480	480
85	35	15	480	480
86	35	17	480	480
87	35	15	480	1560
88	35	14	1560	1560
89	35	14	1560	1560
90	35	16	1560	3720
91	35	2	3720	\N
92	36	9	-36000	0
94	37	3	-7200	\N
95	38	6	-14400	\N
96	39	13	-7200	0
93	36	21	0	2220
98	36	18	2220	5820
99	36	20	5820	\N
97	39	14	0	0
100	39	17	0	0
101	39	15	0	1680
102	39	17	1680	1680
103	39	15	1680	1860
104	39	14	1860	1860
105	39	14	1860	2280
106	39	16	2280	2520
107	39	2	2520	\N
121	50	5000	0	\N
120	48	30	0	\N
178	61	10	0	\N
600	49	40	0	\N
\.


--
-- Name: sim_patient_state_sim_patient_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_patient_state_sim_patient_state_id_seq', 186, true);


--
-- PostgreSQL database dump complete
--

