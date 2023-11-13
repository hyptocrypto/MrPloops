#! /bin/bash

ffmpeg -i rtsp://192.168.1.56:8554/cam -vf fps=5 -q:v 2 -f image2pipe -vcodec rawvideo -pix_fmt rgb24 - | ../venv/bin/python test.py
