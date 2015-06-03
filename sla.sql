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
    name text NOT NULL,
    level integer NOT NULL,
    rate_rq_s integer NOT NULL,
    speed_bytes_s integer NOT NULL,
    timeout_s integer NOT NULL,
    CONSTRAINT sla_rate_rq_s_check CHECK ((rate_rq_s >= 0)),
    CONSTRAINT sla_speed_bytes_s_check CHECK ((speed_bytes_s >= 0)),
    CONSTRAINT sla_timeout_s_check CHECK ((timeout_s >= 0))
);


ALTER TABLE public.sla OWNER TO ckan_default;

--
-- Name: sla_level_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default; Tablespace: 
--

ALTER TABLE ONLY sla
    ADD CONSTRAINT sla_level_key UNIQUE (level);


--
-- Name: sla_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default; Tablespace: 
--

ALTER TABLE ONLY sla
    ADD CONSTRAINT sla_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

