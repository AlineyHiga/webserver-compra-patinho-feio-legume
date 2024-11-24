#!/bin/bash

#build the project
echo "Building the project"
python3 -m pip install -r requirements.txt

eco "Make migration"
python3 manage.py makemigrations --noinput
python3 manage

echo "collect Static"
python3 manage.py collectstatic --noinput --clear