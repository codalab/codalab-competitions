import os, json

with open("./apps/web/fixtures/initialize_site.json") as file:
    site_data = json.loads(file.read())

site_data[0]['fields']['domain'] = os.environ['CODALAB_SITE_DOMAIN']
site_data[0]['fields']['name'] = 'CODALAB_SITE_DOMAIN'


with open("./apps/web/fixtures/initialize_site.json", 'w') as file:
    file.write(json.dumps(site_data))



