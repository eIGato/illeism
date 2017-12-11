#!/usr/bin/env bash
virtualenv -p python3 .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c '\
import nltk;\
nltk.download("punkt");\
nltk.download("wordnet");\
nltk.download("averaged_perceptron_tagger")'
