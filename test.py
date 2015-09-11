from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

loader = FileSystemLoader("templates")
env = Environment(line_statement_prefix='%',
      variable_start_string="{{",
      variable_end_string="}}",
      loader=loader)
t = env.get_template("base.html")


tmpl = env.from_string("""\
<ul>
{% for item in seq %}
    <li>{{item}}</li>
{% endfor %}
</ul>
{{cat}}


""")

print(t.render())