#!/usr/bin/env python
from ckanapi import RemoteCKAN
import json

settings = json.load(open('datahub-credentials.json', 'r'))

client = RemoteCKAN(settings['ckan_host'], settings['api_key'])

package_ids = client.action.package_list()

sparql = []
for package_id in package_ids:
    package = client.action.package_show(id=package_id)

    resources = package.get('resources')
    sparql_endpoints = [
        resource['url'] for resource in resources
        if resource['format'] == 'api/sparql' or resource['description'] == 'SPARQL endpoint'
    ]
    if sparql_endpoints:
            sparql.append((file, ', '.join(sparql_endpoints)))
            continue

with open('results_sparql.txt', 'w') as list_file:
    for package, urls in sparql:
        line = u'%s: %s\n' % (package, urls)
        list_file.write(line.encode('utf-8'))
