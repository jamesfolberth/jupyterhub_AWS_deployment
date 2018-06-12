#!/usr/bin/env bash

if [[ ! -d tensorflow_models ]]; then
    echo "Cloning tensorflow models repo"
    git clone https://github.com/tensorflow/models.git tensorflow_models
fi


if [[ ! -d FastText ]]; then
    mkdir FastText
fi

if [[ ! -f FastText/wiki-news-300d-100k.vec ]]; then
    echo "ERROR: Download John's FastText.zip and put the .vec file in ./FastText/wiki-news-300d-100k.vec."
    exit 1;
fi

