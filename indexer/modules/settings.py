import json

settings = {}
with open('settings.json', 'r') as settings_file:
    settings = json.load(settings_file)
