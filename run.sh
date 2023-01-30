#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    port="8888"
else
    port=$1
fi

echo Starting TSF AF on port $port
docker run -d -p $port:5000  --name TSN_AF --restart unless-stopped tsn_af
