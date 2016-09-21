#!/usr/bin/env python
from ckanapi import RemoteCKAN
import json

settings = json.load(open('datahub-credentials.json', 'r'))

client = RemoteCKAN(settings['ckan_host'], settings['api_key'])

package_ids = client.action.package_list()

sparql = []
with open('results_sparql.txt', 'w') as list_file:
    for package_id in package_ids:
        package = client.action.package_show(id=package_id)
        for resource in package.get('resources'):
            if resource['format'] == 'api/sparql' or resource['description'] == 'SPARQL endpoint':
                list_file.write(resource['url'].encode('utf-8'))
