#! /bin/bash

INFERENCE_PID_FILE="inference.pid"
STREAM_PID_FILE="stream.pid"

if [ -f "$INFERENCE_PID_FILE" ]; then
    INFER_PID=$(cat $INFERENCE_PID_FILE)
    echo "Killing inferance process with PID: $INFER_PID"
    kill -s SIGTERM "$INFER_PID"
    rm "$INFERENCE_PID_FILE"
else
    echo "No inference.pid file found"
fi


if [ -f "$STREAM_PID_FILE" ]; then
    STREAM_PID=$(cat $STREAM_PID_FILE)
    echo "Killing stream process with PID: $STREAM_PID"
    kill -s SIGTERM "$STREAM_PID"
    rm "$STREAM_PID_FILE"
else
    echo "No stream.pid file found"
fi
