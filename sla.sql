--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: sla; Type: TABLE; Schema: public; Owner: ckan_default; Tablespace: 
--

CREATE TABLE sla (
    id text NOT NULL,
    name text,
    level integer,
    rate_rq_s integer,
    speed_bytes_s integer,
    priority integer
);


ALTER TABLE public.sla OWNER TO ckan_default;

--
-- Data for Name: sla; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY sla (id, name, level, rate_rq_s, speed_bytes_s, priority) FROM stdin;
\.


--
-- Name: sla_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default; Tablespace: 
--

ALTER TABLE ONLY sla
    ADD CONSTRAINT sla_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

