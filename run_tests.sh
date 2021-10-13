#!/bin/bash

EVENNIA_EXEC=$PWD/.venv/bin/evennia 

$EVENNIA_EXEC test --settings settings.py $1