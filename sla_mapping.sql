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
-- Name: sla_mapping; Type: TABLE; Schema: public; Owner: ckan_default; Tablespace:
--

CREATE TABLE sla_mapping (
    id text NOT NULL,
    sla_id text NOT NULL,
    user_id text NOT NULL
);


ALTER TABLE public.sla_mapping OWNER TO ckan_default;

--
-- Name: sla_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default; Tablespace:
--

ALTER TABLE ONLY sla_mapping
    ADD CONSTRAINT sla_mapping_pkey PRIMARY KEY (id);


--
-- Name: sla_mapping_sla_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY sla_mapping
    ADD CONSTRAINT sla_mapping_sla_id_fkey FOREIGN KEY (sla_id) REFERENCES sla(id);


--
-- Name: sla_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY sla_mapping
    ADD CONSTRAINT sla_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id);


--
-- PostgreSQL database dump complete
--

