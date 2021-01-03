#!/bin/bash

alias psql="psql -h ${PGHOST} -U ${PGUSER}"

psql -t -c "SELECT TRUE FROM dbg_dump_tables()"
