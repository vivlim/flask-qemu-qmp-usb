#!/bin/bash
pipenv install
FLASK_APP=app.py pipenv run flask run