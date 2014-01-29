#!/bin/bash
export PYTHONPATH={{BUNDLE_SERVICE_CODE_PATH}}:{{PROJECT_DIR}}:$PYTHONPATH
{% for e,v in STARTUP_ENV.items %}
export {{e}}={{v}}
{% endfor %}
