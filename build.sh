#!/usr/bin/env bash
set -o errexit

# Força uso do Python 3.12
export PYTHON_VERSION=3.12.7

pip install --upgrade pip
pip install -r requirements.txt
