import logging
from jinja2 import Environment, PackageLoader, select_autoescape

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

    def convert_json(obj):
      if isinstance(obj, dict):
          return {k: convert_json(v) for k, v in obj.items()}
      elif isinstance(obj, list):
          return [convert_json(item) for item in obj]
      elif isinstance(obj, str):
          return to_pascal_cp1252(obj)
      else:
          return obj

    agenda_formated = convert_json(agenda)


    print(template.render(agenda=agenda_formated))
    
    # Write rendered SB collection  to file
    with open(f"{target_path}/Schedule.col", 'w') as file:
      file.write(template.render(agenda=agenda_formated))
