#!/usr/bin/env bash
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"

while getopts "n:" opt; do
  case $opt in
    n) number=$OPTARG ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

NUMBER_PHILOSOPHERS=${number:-3}

if [ "$NUMBER_PHILOSOPHERS" -lt 3 ]; then
    echo "The number is less than 3. Setting it to 3 by default."
    NUMBER_PHILOSOPHERS=3
fi

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "stopping and removing philosoph $i and fork $i..."
    docker stop -s SIGKILL ph$i 
    docker rm ph$i 
    docker stop -s SIGKILL f$i 
    docker rm f$i 

done

echo "Checking if network vs-net exists..."
docker network inspect vs-net >/dev/null 2>&1 || docker network create vs-net
echo "Network vs-net is ready."


echo "Building philosopher..."
docker build  ${BASE_DIR}philosoph -t philosoph
echo -e "\n\n"

echo "Building fork..."
docker build  ${BASE_DIR}fork -t fork
echo -e "\n\n"

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "Starting fork $i..."
    docker run -d --net=vs-net \
    -e ID="$i"  \
    --name f$i fork
done

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "Starting philosoph $i..."
    docker run -d --net=vs-net \
    -e ID="$i"  \
    -e NUMBER_PHILOSOPHERS=$NUMBER_PHILOSOPHERS  \
    --name ph$i philosoph
done

sleep 2s

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    docker logs -f ph$i &
done
