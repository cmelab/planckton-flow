#!/bin/bash

python3 src/project.py status --detailed $@ | tee status.txt
