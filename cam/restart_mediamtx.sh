#! /bin/bash

LOG_FILE="/home/pi/restart.log"

while true; do
	sleep 600
	sudo systemctl restart mediamtx
        echo "$(date): Restarted Mediamtx" >> "$LOG_FILE"
done
