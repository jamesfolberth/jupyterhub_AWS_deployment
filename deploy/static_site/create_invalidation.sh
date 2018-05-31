#!/usr/bin/env bash

. aws_env

# Invalidate the edge caches.
# You get 1000 free invalidation paths per month, where a path could be
# /path/to/object.png or /*, which nukes a bunch of objects.
aws cloudfront create-invalidation --distribution-id  $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
