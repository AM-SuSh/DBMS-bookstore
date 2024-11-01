#!/bin/sh
export PATHONPATH=`pwd`
coverage run -m unittest discover run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data
coverage combine
coverage report
coverage html
