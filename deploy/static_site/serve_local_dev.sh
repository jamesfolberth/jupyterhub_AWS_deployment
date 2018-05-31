#!/usr/bin/env bash
cd source
bundle exec jekyll serve --destination ../jekyll-output --unpublished --drafts --future
cd ..
