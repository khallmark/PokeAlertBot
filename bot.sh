#!/bin/bash

until "python main.py"; do
    echo "Server 'python main.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done