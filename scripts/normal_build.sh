#!/usr/bin/env bash
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"

while getopts "n:" opt; do
  case $opt in
    n) number=$OPTARG ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

NUMBER_PHILOSOPHEN=${number:-3}

if [ "$NUMBER_PHILOSOPHEN" -lt 3 ]; then
    echo "The number is less than 3. Setting it to 3 by default."
    NUMBER_PHILOSOPHEN=3
fi


for i in $(seq 1 ${NUMBER_PHILOSOPHEN});
do
    echo "stopping philosoph $i..."
    docker stop ph$i 
done

for i in $(seq 1 ${NUMBER_PHILOSOPHEN});
do
    echo "removing philosoph $i..."
    docker rm ph$i 
done

echo "Checking if network vs-net exists..."
docker network inspect vs-net >/dev/null 2>&1 || docker network create vs-net
echo "Network vs-net is ready."

echo "Building philosopher..."
docker build --quiet ${BASE_DIR}philosoph -t philosoph
echo -e "\n\n"


for i in $(seq 1 ${NUMBER_PHILOSOPHEN});
do
    echo "Starting philosoph $i..."
    docker run -d --net=vs-net \
    -e NAME="ph$i"  \
    --name ph$i philosoph
done

sleep 2s

for i in $(seq 1 ${NUMBER_PHILOSOPHEN});
do
    docker logs ph$i
done

exec bash