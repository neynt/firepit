#!/bin/bash
while inotifywait -e close_write **/*.py >/dev/null 2>/dev/null; do
  echo 'status' | python firepit.py
done
