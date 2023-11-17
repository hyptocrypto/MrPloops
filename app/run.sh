#! /bin/bash
../venv/bin/python inference.py >/dev/null 2>&1 & 
../venv/bin/python stream_server.py >/dev/null 2>&1 &
