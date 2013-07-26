#!/bin/bash
{% for e,v in STARTUP_ENV.items %}
export {{e}}={{v}}
{% endfor %}
