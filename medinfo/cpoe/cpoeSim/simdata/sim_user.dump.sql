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
-- Data for Name: sim_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY sim_user (sim_user_id, name) FROM stdin;
0	Default User
1	Jonathan Chen
9	User1
2	User2
10	User3
11	User4
12	User5
13	User6
\.


--
-- Name: sim_user_sim_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('sim_user_sim_user_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

