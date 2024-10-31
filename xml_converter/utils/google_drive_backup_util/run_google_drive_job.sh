#!/bin/sh
current_directory=$(dirname "$0")
source $current_directory/../../../venv/bin/activate
python $current_directory/google_drive_backup.py