#!/usr/bin/env bash
. aws_env

aws s3 sync jekyll_deploy s3://${S3_BUCKET_NAME} --delete

echo
echo "S3 endpoint: ${S3_ENDPOINT_NAME}"
