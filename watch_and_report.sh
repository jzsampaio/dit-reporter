#!/bin/bash

# e.g.: ./watch_and_report 2019-01-01 2019-01-07

python daily-report.py . $@

while inotifywait -e close_write -e create -e delete -r .; do
    clear
    python daily-report.py . $@
done
