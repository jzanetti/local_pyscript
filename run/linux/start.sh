#!/bin/bash

# Go to the working dir
cd ../../examples/calculator

# Start the server
python -m http.server 8080 &

# wait 5 sec to ensure the server is up
sleep 5

# open the web browser
open http://localhost:8080