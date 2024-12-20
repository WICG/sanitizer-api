# Sanitizer API - Build configuration dictionary from text file.

import json
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=argparse.FileType('r'), required=True)
    parser.add_argument("--out", type=argparse.FileType('w'), required=True)
    args = parser.parse_args()

    try:
      lines = args.input.read()
    except BaseException as err:
      parser.error("Cannot read from --input file.")

    result = { "elements": [], "attributes": [] }
    current = []
    for line in lines.split("\n"):
      if not line:
        pass
      elif line.startswith("//"):
        pass
      elif line.startswith("- "):
        current.append({ "name": line[2:], "namespace": None })
      elif line == "[HTML Global]":
        current = result["attributes"]
      else:
        elem = { "name": line, "namespace": "http://www.w3.org/1999/xhtml",
                 "attributes": [] }
        result["elements"].append(elem)
        current = elem["attributes"]

    try:
      json.dump(result, args.out, indent=2)
    except BaseException as err:
      parser.error("Cannot write to --out file.")
    return 0

if __name__ == "__main__":
    main()
