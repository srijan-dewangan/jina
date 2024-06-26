set -ex

docker build --build-arg PIP_TAG="[devel]" -f Dockerfiles/pip.Dockerfile -t jinaai/jina:test-pip .
docker build -f tests/jinahub/hub_mwu/Dockerfile tests/jinahub/hub_mwu -t hubpod:test
docker build -f tests/jinahub/Dockerfile tests/jinahub/ -t jinaai/test_hubapp_hubpods

if [ "${PWD##*/}" != "jina" ]
  then
    echo "test_integration.sh should only be run from the jina base directory"
    exit 1
fi

CONTAINER_ID=$(docker run -v /var/run/docker.sock:/var/run/docker.sock --network=host -d jinaai/test_hubapp_hubpods)

sleep 10

RESPONSE=$(curl --request POST -d '{"data": ["text:hey, dude"]}' -H 'Content-Type: application/json' 'localhost:45678/index')

echo "Response is: ${RESPONSE}"

TEXT_RESPONSE=$(echo $RESPONSE | jq -e ".data.docs[] | .text")

echo "Text Response is: ${TEXT_RESPONSE}"

# remove the new pods
docker ps -a | awk '{ print $1,$2 }' | grep hubpod:test | awk '{print $1 }' | xargs -I {} docker rm -f {}
docker rm -f $CONTAINER_ID

EXPECTED_TEXT='"text:hey, dude"'

if [ "$EXPECTED_TEXT" = "$TEXT_RESPONSE" ]; then
        echo "Success"
else
        echo "Fail"
        exit 1
fi