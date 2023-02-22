#!/usr/bin/env bash

echo Starting TSF AF. Running on host network, port 8899
docker run -d --network=host  --name TSN_AF --restart unless-stopped tsn_af
