#!/bin/bash

#disable the "errexit" option, even if a command within the script fails,
#the script will continue executing the subsequent commands instead of immediately terminating.
set +e

#change the pipeline behaviour
set -o pipeline

global_status=0

echo -e "#### RUNNING black ####\n"
black --check --diff .
status=$?

if [[ status -eq 0 ]]
then 
    echo -e "No problems detected by black\n"
else
    echo -e "Problems detected by black, please run black and commit the result\n"
    global_status=1
fi

echo -e "#### Running ruff ####\n"
ruff check --show-source .
status=$?
if [[ $status -eq 0 ]]
then
    echo -e "No problem detected by ruff\n"
else
    echo -e "Problems detected by ruff, please fix them\n"
    global_status=1
fi

echo -e "#### Linting completed ####\n"
if [[ $global_status -eq 1 ]]
then
    echo -e "Linting failed\n"
    exit 1
else
    echo -e "Linting passed\n"
    exit 0
fi