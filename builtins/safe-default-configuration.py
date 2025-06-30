# Sanitizer API - Build configuration dictionary from text file.

import json
import argparse
import sys

def dedupe(alist):
  result = []
  for item in alist:
    if not item in result:
      result.append(item)
  return result

def remove_from(alist, reference):
  return [item for item in dedupe(alist) if not item in reference]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=argparse.FileType('r'), required=True)
    parser.add_argument("--out", type=argparse.FileType('w'), required=True)
    args = parser.parse_args()

    try:
      lines = args.input.read()
    except BaseException as err:
      parser.error("Cannot read from --input file.")

    result = { "elements": [], "attributes": [], "comments": False, "dataAttributes": False }
    current = []
    for line in lines.split("\n"):
      if "//" in line:
        line = line[:line.find("//")]
      line = line.strip()
      if not line:
        pass
      elif line.startswith("- xml "):
        current.append({"name": line[6:], "namespace": "http://www.w3.org/XML/1998/namespace"})
      elif line.startswith("- "):
        current.append(line[2:])
      elif line.startswith("[") and line.endswith("Global]"):
        current = result["attributes"]
      else:
        if line.startswith("math "):
          elem = {"name": line[5:],
                  "namespace": "http://www.w3.org/1998/Math/MathML"}
        elif line.startswith("svg "):
          elem = {"name": line[4:], "namespace": "http://www.w3.org/2000/svg"}
        else:
          elem = {"name": line, "namespace": "http://www.w3.org/1999/xhtml"}
        elem["attributes"] = []
        result["elements"].append(elem)
        current = elem["attributes"]

    # De-dupe the global element + attribute allow lists.
    result["elements"] = dedupe(result["elements"])
    result["attributes"] = dedupe(result["attributes"])

    # Remove globally allowed attributes from per-element allow lists.
    for element in result["elements"]:
      if "attributes" in element:
        element["attributes"] = remove_from(element["attributes"],
                                            result["attributes"])

    # Remove empty per-element allow lists.
    for element in result["elements"]:
      if "attributes" in element and not element["attributes"]:
        element.pop("attributes")

    # Replace element dictionaries with string (if the default handling would
    # create the same dictionary again).
    for index, element in enumerate(result["elements"]):
      if (element["namespace"] == "http://www.w3.org/1999/xhtml" and
          not "attributes" in element and not "removeAttributes" in element):
        result["elements"][index] = element["name"]

    try:
      json.dump(result, args.out, indent=2)
    except BaseException as err:
      parser.error("Cannot write to --out file.")
    return 0

if __name__ == "__main__":
    main()
