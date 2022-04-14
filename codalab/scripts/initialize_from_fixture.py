import os, json

with open("apps/web/fixtures/initialize_site.json",'r') as initial_site_json:
    json_data = json.loads(initial_site_json.read())
    json_data[0]['fields']['domain'] = os.environ.get('CODALAB_SITE_DOMAIN', 'localhost')
    json_data[0]['fields']['name'] = os.environ.get('CODALAB_SITE_DOMAIN', 'localhost')

with open("apps/web/fixtures/initialize_site.json",'w') as post_site_json:
    post_site_json.write(json.dumps(json_data))
    
