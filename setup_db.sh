#!/bin/bash

sudo -u postgres psql -d ckan_default -f sla.sql
sudo -u postgres psql -d ckan_default -f sla_mapping.sql