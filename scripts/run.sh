#! /bin/bash

git checkout master |:
git pull
pip install -r requirements.txt
whoami
python src/anathema.py
