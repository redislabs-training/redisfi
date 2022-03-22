import requests
from flask import Blueprint, current_app, request, render_template

from redisfi.web.research.api import facets

research = Blueprint('research', __name__)

@research.route('/')
def overview():
    return render_template('research/overview.html')

@research.route('/ft')
def full_text():
    query = request.args.get('query')
    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params={'filter':query})
    resp_data = resp.json()
    return render_template('research/results.html', **resp_data)

@research.route('/vss')
def vss():
    query = request.args.get('query')
    _filter = request.args.get('filter')
    if _filter is not None:
        params = {'term':query, 'filter':_filter}
    else:
        params = {'term':query}

    print(params)

    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params=params)
    resp_data = resp.json()
    return render_template('research/results.html', **resp_data, facets=facets(query, serialize=False), query=query)



