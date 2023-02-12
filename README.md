
# Run locally

## Build docker

 docker build \
  --build-arg BUILD_FROM="homeassistant/amd64-base:latest" \
  -t local/my-test-addon \
  .


## Run docker

docker run \
  --rm \
  -v /tmp/my_test_data:/data \
  -p 1883 \
  local/my-test-addon