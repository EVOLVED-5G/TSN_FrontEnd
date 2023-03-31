#!/usr/bin/env bash

port=$(cat Dockerfile | grep "EXPOSE ")
port=${port//EXPOSE }

echo "Starting TSF FrontEnd. Running on host network, port $port"
docker run -d --network=host  --name TSN_FrontEnd --restart unless-stopped tsn_frontend
