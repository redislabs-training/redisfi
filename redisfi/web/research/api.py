from json import dumps

import requests
from flask import Blueprint, request, current_app

research_api = Blueprint('research_api', __name__)

@research_api.route('/facets')
def facets(query=None, serialize=True):
    query = query or request.args.get('query')
    url = current_app.config.get('VSS_URL')
    resp = requests.get(f'{url}/facets', params={'term':query})
    facets: dict = resp.json()
    inverted = [(item.title(), facets[item]) for item in sorted(facets, key=facets.get, reverse=True) if item != 'N/A']
    
    if serialize:
        return dumps(inverted)
    else:
        return inverted
