import sys
import json
import textwrap

class NameList:
  def __init__(self, file):
    self.namespace = None
    self.names = []
    for line in file:
      if line.startswith("# namespace:"):
        self.namespace = line[len(" namespace:") + 1:].strip()
      elif not line or line.startswith("#"):
        pass  # Drop empties and comments.
      else:
        self.names.append(line.strip())

  def __iter__(self):
    return self.names.__iter__()

def load():
  lists = dict()
  for kind in ["attributes", "elements"]:
    for spec in ["html", "svg", "mathml"]:
      for what in ["known", "baseline", "default"]:
        list_file = (kind, spec, what)
        with open("%s-%s-%s.txt" % list_file, "r") as f:
          lists["%s-%s-%s" % list_file] = NameList(f)
  for spec in ["xlink", "xml", "xmlns"]:
    list_file = ("attributes", spec, "known")
    with open("%s-%s-%s.txt" % list_file, "r") as f:
      lists["%s-%s-%s" % list_file] = NameList(f)
  lists["default_stub"] = json.load(open("defaults-stub.json", "r"))
  return lists

def join_lists(*lists):
  result = []
  NAMESPACE_MAP = {
      "": "", "http://www.w3.org/1999/xhtml": "",
      "http://www.w3.org/2000/svg": "svg:", "http://www.w3.org/1998/Math/MathML": "mathml:",
      "http://www.w3.org/1999/xlink": "xlink:", "http://www.w3.org/XML/1998/namespace": "xml:",
      "http://www.w3.org/2000/xmlns/": "xmlns",
  }
  for l in lists:
    for name in l:
      result.append(NAMESPACE_MAP[l.namespace] + name)
  return sorted(result)

def write_lists(filename, *lists):
  with open(filename, "w") as out:
    out.write(textwrap.fill(", ".join(join_lists(*lists))))

def main(argv):
  lists = load()

  defaults = lists["default_stub"].copy()
  defaults["allowElements"] = lists["elements-html-default"]
  defaults["allowAttributes"] = dict([(attr, ["*"]) for attr in lists["attributes-html-default"]])

  with open("../out/default-configuration.json", "w") as config_out:
    json.dump(defaults, config_out, indent=True, sort_keys=True,
              ensure_ascii=True, default=lambda obj: obj.names)

  write_lists("../out/baseline-element-allow-list.txt",
    lists["elements-html-baseline"], lists["elements-svg-baseline"], lists["elements-mathml-baseline"])
  write_lists("../out/baseline-attribute-allow-list.txt",
    lists["attributes-html-baseline"], lists["attributes-svg-baseline"], lists["attributes-mathml-baseline"])

#  write_lists("../out/known-elements-list.txt",
#    lists["elements-html-known"], lists["elements-svg-known"], lists["elements-mathml-known"])
#  write_lists("../out/default-element-allow-list.txt",
#    lists["elements-html-default"], lists["elements-svg-default"], lists["elements-mathml-default"])

if __name__ == '__main__':
  main(sys.argv)
