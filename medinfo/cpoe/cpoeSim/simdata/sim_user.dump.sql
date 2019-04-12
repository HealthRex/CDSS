--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.11
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
-- Data for Name: sim_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_user (sim_user_id, name) FROM stdin;
0	Default User
1	Jonathan Chen
9	User1
2	User2
10	User3
11	User4
12	User5
13	User6
14	
\.


--
-- Name: sim_user_sim_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_user_sim_user_id_seq', 14, true);


--
-- PostgreSQL database dump complete
--

