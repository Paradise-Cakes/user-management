set -e
cd ./lambdas
AWS_ACCESS_KEY_ID="fakekey" \
AWS_SECRET_ACCESS_KEY="fakesecret" \
AWS_SESSION_TOKEN="fake" \
AWS_DEFAULT_REGION="test" \
poetry install
poetry run pytest ../integration_tests -vvv --cov

