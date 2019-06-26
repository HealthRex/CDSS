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
-- Data for Name: sim_grading_key; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_grading_key (index, clinical_item_id, "case", clinical_item_name, name, score, confidence, state_dependent, group_dependent, sim_state_id) FROM stdin;
0	35733	meningitis	Ceftriaxone (Intravenous)	Meningitis Adequately Treated	10	3	f	f	31
1	44281	meningitis	Acetaminophen (Oral)	Meningitis Adequately Treated	4	2	f	f	31
2	43997	meningitis	Vancomycin (Intravenous)	Meningitis Adequately Treated	10	1	t	t	31
3	44017	meningitis	Dexamethasone (Intravenous)	Meningitis Adequately Treated	10	2	f	f	31
4	45811	meningitis	DIET NPO	Meningitis Adequately Treated	3	3	t	t	31
5	35733	meningitis	Ceftriaxone (Intravenous)	Mening Active	10	3	f	f	30
6	44281	meningitis	Acetaminophen (Oral)	Mening Active	4	2	f	f	30
7	43997	meningitis	Vancomycin (Intravenous)	Mening Active	10	1	t	t	30
8	44017	meningitis	Dexamethasone (Intravenous)	Mening Active	10	2	f	f	30
9	45811	meningitis	DIET NPO	Mening Active	3	3	t	t	30
10	44281	meningitis	Acetaminophen (Oral)	Meningits Worsens	4	2	f	f	33
11	43997	meningitis	Vancomycin (Intravenous)	Meningits Worsens	10	1	t	t	33
12	44017	meningitis	Dexamethasone (Intravenous)	Meningits Worsens	10	2	f	f	33
13	45811	meningitis	DIET NPO	Meningits Worsens	3	3	t	t	33
\.


--
-- PostgreSQL database dump complete
--

