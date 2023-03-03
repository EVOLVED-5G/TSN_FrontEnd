#!/usr/bin/env bash

port=$(cat Dockerfile | grep "EXPOSE ")
port=${port//EXPOSE }

echo "Starting TSF AF. Running on host network, port $port"
docker run -d --network=host  --name TSN_AF --restart unless-stopped tsn_af
