#!/usr/bin/env sh

current_directory=$(dirname "$0")
project_root=$(realpath "$current_directory/../../../")

if [ -f "$project_root/venv/bin/activate" ]; then
    source "$project_root/venv/bin/activate"
elif [ -f "$project_root/venv/Scripts/activate" ]; then
    source "$project_root/venv/Scripts/activate"
else
    echo "No virtual environment activation script found." >&2
    exit 1
fi

python $project_root/manage.py test taskmaster.tests.django_tests