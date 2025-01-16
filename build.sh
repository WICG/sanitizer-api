#!/bin/sh
# Generate safe-default-configuration.json
python3 builtins/safe-default-configuration.py --input builtins/safe-default-configuration.txt --out builtins/safe-default-configuration.json
# Generate safe-baseline-configuration-materialized.json
python3 builtins/safe-baseline-configuration.py --input builtins/safe-baseline-configuration.json --event-handlers builtins/event-handler-content-attributes.txt --out builtins/safe-baseline-configuration-materialized.json

