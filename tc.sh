#!/bin/sh

cd $(dirname "$0")

pipenv run pypy -m trade_companion "$@"
