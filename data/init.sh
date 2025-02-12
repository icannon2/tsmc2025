#!/bin/sh
if [ ! -f "datasource.duckdb" ]; then
    echo creating datasource.duckdb from datasource.csv
    cat init.sql | duckdb datasource.duckdb 
fi