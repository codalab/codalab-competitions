{% for e,v in STARTUP_ENV.items %}
set {{e}}={{v}}
{% endfor %}
