#!/usr/bin/env bash
export DOCKER_SCOUT=disable
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"

while getopts "n:" opt; do
  case $opt in
    n) number=$OPTARG ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

NUMBER_PHILOSOPHERS=${number:-5}
BASE_FORK_IP="20.0.1"
FORK_IP="10.8.1.6"
PRS_IP="10.8.1.6"
BASE_PORT=42040

if [ "$NUMBER_PHILOSOPHERS" -lt 2 ]; then
    echo "The number is less than 2. Setting it to 3 by default."
    NUMBER_PHILOSOPHERS=2
fi

function build_container() {
  local dir=$1
  local tag=$2

  echo "Building $tag..."
  if docker build --quiet "${BASE_DIR}${dir}" -t "$tag"; then
    echo "Successfully built: $tag"
  else
    echo "Failed to build: $tag" >&2
  fi
  echo ""
}
build_container "philosoph" "philosoph"

function run_container_phil() {
  local name=$1
  local id=$2

  echo "Starting $name..."
  if docker run -d --net=vs-net --name "$name" -e PRS_IP=$PRS_IP -e ID=$id -e BASE_IP=$BASE_FORK_IP -e FORKS_IP=$FORK_IP -e BASE_PORT=$BASE_PORT -e NUMBER_PHILOSOPHERS=$NUMBER_PHILOSOPHERS "philosoph"; then
    echo "$name started successfully."
  fi
  echo ""
}

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "Starting philosopher $i..."
    run_container_phil "ph$i" "$i"
done

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    docker logs -f ph$i &
done


bash