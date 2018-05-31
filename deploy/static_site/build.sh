#!/usr/bin/env bash
cd source
bundle exec jekyll build --source . --destination ../jekyll-output
cd ..
