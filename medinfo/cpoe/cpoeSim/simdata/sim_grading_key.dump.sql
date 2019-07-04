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
-- Data for Name: sim_grading_key; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sim_grading_key (sim_grading_key_id, sim_grader_id, sim_state_id, clinical_item_id, score, confidence, group_name, comment) FROM stdin;
\.


--
-- Name: sim_grading_key_sim_grading_key_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sim_grading_key_sim_grading_key_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

