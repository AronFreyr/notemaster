#!/bin/sh
current_directory=$(dirname "$0")
source $current_directory/../../../venv/bin/activate
python $current_directory/dropbox_backup.py