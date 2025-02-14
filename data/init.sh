#!/bin/sh
if [ ! -f "datasource.duckdb" ]; then
    echo creating datasource.duckdb from datasource.csv
    curl https://rate.bot.com.tw/xrt/flcsv/0/day -o ExchangeRate.csv
    cat init.sql | duckdb datasource.duckdb 
fi