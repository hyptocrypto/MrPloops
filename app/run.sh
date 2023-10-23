#! /bin/bash
python inference.py >/dev/null 2>&1 & 
python stream_server.py >/dev/null 2>&1 &
