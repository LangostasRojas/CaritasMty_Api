#!/bin/bash
pkill -f "python3 -m gunicorn.app.wsgiapp -b 0.0.0.0:10206"
