#! /bin/bash

INFERENCE_PID_FILE="inference.pid"
STREAM_PID_FILE="stream.pid"

terminate_process() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
            echo "Killing process with PID: $pid"
            kill -s SIGTERM "$pid"
        else
            echo "Process with PID $pid not found or invalid"
        fi
        rm "$pid_file"
    else
        echo "No $pid_file found"
    fi
}


terminate_process $INFERENCE_PID_FILE
terminate_process $STREAM_PID_FILE
