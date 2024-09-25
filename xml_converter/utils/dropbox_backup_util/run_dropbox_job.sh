#!/bin/bash
source ../../../venv/bin/activate &&
python3.6 /opt/notemaster/xml_converter/utils/dropbox_backup_util/dropbox_backup.py &&
deactivate
