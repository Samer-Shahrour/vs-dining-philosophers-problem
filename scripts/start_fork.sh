#!/usr/bin/env bash
export DOCKER_SCOUT=disable
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"

# Parsing command line arguments
while getopts "n:" opt; do
  case $opt in
    n) number=$OPTARG ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

# Set default values
NUMBER_PHILOSOPHERS=${number:-5}
BASE_FORK_IP="20.0.1"
BASE_PORT=42040

# Ensure number of philosophers is at least 2
if [ "$NUMBER_PHILOSOPHERS" -lt 2 ]; then
    echo "The number is less than 2. Setting it to 2 by default."
    NUMBER_PHILOSOPHERS=2
fi

# Function to build Docker container
function build_container() {
  local dir=$1
  local tag=$2

  echo "Building $tag..."
  if docker build --quiet "${BASE_DIR}${dir}" -t "$tag"; then
    echo "Successfully built: $tag"
  else
    echo "Failed to build: $tag" >&2
    exit 1
  fi
  echo ""
}

# Cleanup existing Docker network if it exists
docker network rm vs-net 2>/dev/null || true
docker network create --driver bridge --subnet=20.0.0.0/22 vs-net
echo "Network vs-net is ready."

# Build the "fork" container
build_container "fork" "fork"

# Function to run Docker container
function run_fork() {
  local name=$1
  local image=$2
  local ip=$3
  local port=$4
  local options=${5:-""}

  echo "Starting $name..."
  echo "Fork $name -> IP: $ip, Port: $port"
  if docker run -p $port:$port -d --net=vs-net --ip $ip --name "$name" $options -e PORT=$port -e IP=$ip "$image"; then
    echo "$name started successfully."
  else
    echo "Failed to start $name."
  fi
  echo ""
}

# Start the forks
for i in $(seq 0 $((NUMBER_PHILOSOPHERS-1))); do
    echo "Starting fork $i..."
    run_fork "f$i" "fork" "${BASE_FORK_IP}.$((i+2))" $((BASE_PORT+i)) "-e ID=$i -e IP=${BASE_FORK_IP}.$((i+1))"
done

# Optional: Run `docker logs` for each fork (uncomment if needed)
# for i in $(seq 0 $((NUMBER_PHILOSOPHERS-1))); do
#     echo "Fetching logs for fork $i..."
#     docker logs -f "f$i" &
# done

# Wait for the logs to finish in the background
wait
