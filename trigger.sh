#!/bin/bash
while inotifywait -e close_write *.py */*.py >/dev/null 2>/dev/null; do
  echo 'update-resume' | python firepit.py
done
