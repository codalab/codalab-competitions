#!/bin/bash
export PYTHONPATH={{PROJECT_DIR}}:$PYTHONPATH
{% for e,v in STARTUP_ENV.items %}
export {{e}}={{v}}
{% endfor %}
