import requests
from flask import Blueprint, current_app, request, render_template

from redisfi.web.research.api import facets
from redisfi.web.research.utils import escape_special_characters

research = Blueprint('research', __name__)

DEFAULT_YEAR_START = 2020
DEFAULT_YEAR_END = 2022

@research.route('/')
def overview():
    return render_template('research/overview.html')

@research.route('/ft')
def full_text():
    query = request.args.get('query')
    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params={'filter':query})
    resp_data = resp.json()
    return render_template('research/results-ft.html', **resp_data, query=query)

@research.route('/vss')
def vss(query=None, _filter=None):
    query = query or request.args.get('query')
    if type(query) == list:
        query = query[0]
    
    _filter = _filter or request.args.get('filter')
    if _filter is None:
        _filter = f'@FILED_DATE_YEAR:[{DEFAULT_YEAR_START},{DEFAULT_YEAR_END}]'
    elif type(_filter) == list:
        _filter = _filter[0]
     
    params = {'term':query, 'filter':_filter}
    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params=params)
    resp_data = resp.json()
    resp_data['results'] = filter(lambda result: result['COMPANY_NAME'] != 'N/A', resp_data['results'])
    return render_template('research/results-vss.html', **resp_data, facets=facets(query, _filter, serialize=False), query=query, filter=_filter)

@research.route('/faceted-search', methods=['POST'])
def faceted_search():
    data = request.form.to_dict(flat=False)

    _filter = ''
    if 'companies' in data:
        _filter += f'@COMPANY_NAME:({"|".join([escape_special_characters(company) for company in data["companies"]])}) '
    
    year_start, year_end = data.get('yearStart')[0], data.get('yearEnd')[0]
    
    _filter += f'@FILED_DATE_YEAR:[{year_start or DEFAULT_YEAR_START},{year_end or DEFAULT_YEAR_END}] '
    
    return vss(data['query'][0], _filter.strip())


