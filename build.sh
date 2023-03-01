#!/usr/bin/env bash

echo "Checking for 'jq' availability..."
jq --version
if [ $? -ne 0 ]; then
	echo "'jq' command is not available. Please install and re-run this script."
	echo "See 'https://stedolan.github.io/jq/download/' for more information."
	exit
fi

port=$(jq .FrontEnd.Port config.json)

echo ""
echo "Generating Dockerfile (FrontEnd Port in config.json is $port)..."

cp Dockerfile.Template Dockerfile
sed -i "s/{{PORT}}/$port/" Dockerfile

echo ""
echo "Building docker image..."

docker build -t tsn_af .

echo "Done"
