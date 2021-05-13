# Copyright (C) 2021 Alex Verrico (https://alexverrico.com/). All Rights Reserved.

import requests

baseurl = "http://localhost:80"

r = requests.post('{}/api/plugin/display_eta'.format(baseurl), json={'command': 'current_eta'})
print('JSON response to current_eta POST is: {}'.format(r.json()))

r = requests.get('{}/api/plugin/display_eta'.format(baseurl), {'command': 'current_eta'})
print('JSON response to current_eta GET is: {}'.format(r.json()))

r = requests.post('{}/api/plugin/display_eta'.format(baseurl), json={'command': 'update_eta'})
print('JSON response to update_eta POST is: {}'.format(r.json()))

r = requests.get('{}/api/plugin/display_eta'.format(baseurl), {'command': 'update_eta'})
print('JSON response to update_eta GET is: {}'.format(r.json()))
