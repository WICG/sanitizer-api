# Sanitizer API - Build configuration dictionary from text file.

import json
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=argparse.FileType('r'), required=True)
    parser.add_argument("--event-handlers", type=argparse.FileType('r'),
                        required=True)
    parser.add_argument("--out", type=argparse.FileType('w'), required=True)
    args = parser.parse_args()

    try:
      config = json.load(args.input)
    except BaseException as err:
      parser.error("Cannot read from --input file.")

    try:
      events = args.event_handlers.read()
    except BaseException as err:
      parser.error("Cannot read from --event-handlers file.")

    for event in events.split("\n"):
      if not event:
        continue
      if event.startswith("//"):
        continue
      config["removeAttributes"].append(event)

    try:
      json.dump(config, args.out, indent=2)
    except BaseException as err:
      parser.error("Cannot write to --out file.")
    return 0

if __name__ == "__main__":
    main()
