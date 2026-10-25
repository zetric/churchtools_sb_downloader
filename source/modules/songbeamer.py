import logging
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import zipfile

logger = logging.getLogger(__name__)

class songbeamer:

  def sb_render_template(self, agenda, target_path):

    # Load jinja2 environment
    env = Environment(
        loader=PackageLoader("app"),
        autoescape=select_autoescape()
    )

    template = env.get_template("songbeamer_collection.sb")

    # Change special characters to fit songbeamer format
    def to_pascal_cp1252(s):
      result = []
      for b in s.encode("cp1252"):
          if 32 <= b <= 126 and chr(b) not in ("#",):
              result.append(chr(b))
          else:
              result.append(f"'#{b}'")
      return "".join(result)

    def convert_json(obj, key_marker=None):
      """
      Recursively convert JSON-like structures. If `key_marker` is provided,
      only string values whose parent key contains `key_marker` will be
      transformed with `to_pascal_cp1252`. Otherwise string values are
      returned unchanged.
      """
      if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
          # propagate marker if current key contains it
          marker = key_marker
          if key_marker is None and isinstance(k, str) and "title" in k:
            marker = "title"
          if key_marker is None and isinstance(k, str) and "fileName" in k:
            marker = "fileName"
          new[k] = convert_json(v, key_marker=marker)
        return new
      elif isinstance(obj, list):
        return [convert_json(item, key_marker=key_marker) for item in obj]
      elif isinstance(obj, str):
        if key_marker is not None:
          return to_pascal_cp1252(obj)
        return obj
      else:
        return obj

    agenda_formated = convert_json(agenda)

    logger.debug(os.listdir("./"))

    # Write rendered SB collection  to file
    with open(f"{target_path}/Schedule.col", 'w') as file:
      file.write(template.render(agenda=agenda_formated))

  def zip_file(self, path, fileName):

    with zipfile.ZipFile(fileName, 'w', zipfile.ZIP_DEFLATED) as zipf:
      # ziph is zipfile handle
      for root, dirs, files in os.walk(path):
          for file in files:
              zipf.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), os.path.dirname(path)))