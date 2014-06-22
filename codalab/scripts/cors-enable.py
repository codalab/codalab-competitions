import sys
import yaml
from os.path import dirname, abspath
# Add codalabtools to the module search path
#sys.path.append(dirname(dirname(dirname(abspath(__file__))))) #depends on where you place this script
sys.path.append(dirname(dirname(abspath(__file__))))
from codalabtools.azure_extensions import (Cors,CorsRule,set_storage_service_cors_properties)

account_name = "codalabue"
account_key = "LbPY7RcFTX/rTnRdlhLXz1/crpLnmQX14ioDM8tvzdVt4AQIJIeSovsVJIceWS0X7mFWkUgfzU0nbf1QDLP6Qg=="
cors_rule = CorsRule()
cors_rule.allowed_origins = '*' # this is fine for dev setup
cors_rule.allowed_methods = 'PUT'
cors_rule.exposed_headers = '*'
cors_rule.allowed_headers = '*'
cors_rule.max_age_in_seconds = 1800
cors_rules = Cors()
cors_rules.cors_rule.append(cors_rule)
set_storage_service_cors_properties(account_name, account_key, cors_rules)