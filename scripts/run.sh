#! /bin/bash

git reset --hard origin/master
pip install -r requirements.txt
python src/anathema.py
