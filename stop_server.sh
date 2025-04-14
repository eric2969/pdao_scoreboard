#!/bin/bash

echo "🔍 Searching for Gunicorn processes..."

# 找出所有 gunicorn 相關的 PID
PIDS=$(ps aux | grep 'gunicorn' | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
  echo "No Gunicorn processes found."
  exit 0
fi

echo "Killing the following Gunicorn PIDs: $PIDS"
for pid in $PIDS; do
  kill -9 $pid && echo "Killed PID $pid"
done

echo "All Gunicorn processes have been terminated."
