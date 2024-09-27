#!/bin/bash
current_directory=$(dirname "$0")
source $current_directory/../../../venv/bin/activate &&
python3.6 $current_directory/dropbox_backup.py &&
deactivate