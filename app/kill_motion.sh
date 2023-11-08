#! /bin/bash

MOTION_PID_FILE="motion.pid"

if [ -f "$MOTION_PID_FILE" ]; then
    MOTION_PID=$(cat $MOTION_PID_FILE)
    echo "Killing inferance process with PID: $MOTION_PID"
    kill -s SIGTERM "$MOTION_PID"
    rm "$MOTION_PID_FILE"
else
    echo "No motion.pid file found"
fi
