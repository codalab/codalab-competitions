#!/bin/bash
{% if BUNDLE_SERVICE_CODE_PATH|length > 0 %}
export PYTHONPATH={{BUNDLE_SERVICE_CODE_PATH}}:{{PROJECT_DIR}}:$PYTHONPATH
{% else %}
export PYTHONPATH={{PROJECT_DIR}}:$PYTHONPATH
{% endif %}
{% for e,v in STARTUP_ENV.items %}
export {{e}}={{v}}
{% endfor %}
