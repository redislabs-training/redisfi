from uuid import uuid4

import requests
from flask import Blueprint, current_app, request, render_template, Response

from redisfi.web.research.api import facets

research = Blueprint('research', __name__)

DEFAULT_YEAR_START = 2020
DEFAULT_YEAR_END = 2022
TRENDING_SEARCHES = ["exposure to Russian operations",
                     "hackers attempting to steal customer data",
                     "industry wide plant closures",
                     "High wafer lead times and shortages",
                     "Criminal charges brought",
                     "armed conflict",
                     "Wage pressures",
                     "Britain leaves European Union",
                     "India manufacturing exposure",
                     "concerns over protests",
                     "unintended reputational damage",
                     "weakening demand and consumer confidence"]

_log_guid = lambda: str(uuid4())

@research.route('/')
def overview():
    return render_template('research/overview.html', trending_searches=TRENDING_SEARCHES)

@research.route('/healthcheck')
def healthcheck():
    url = current_app.config.get('VSS_URL') + '/healthcheck'
    status = int(requests.get(url).text)

    if status == 0:
        return Response(status=503)
    elif status == 1:
        return Response(status=200)
    else:
        return Response(status=418) # i'm a little teapot short and stout...

@research.route('/ft')
def full_text():
    query = request.args.get('query')
    url = current_app.config.get('VSS_URL')
    log_guid = _log_guid()
    resp = requests.get(url, params={'filter':query, 'log_guid':log_guid})
    resp_data = resp.json()
    return render_template('research/results-ft.html', **resp_data, query=query, log_guid=log_guid)

@research.route('/vss')
def vss(query=None, _filter=None):
    query = query or request.args.get('query')
    log_guid = _log_guid()
    if type(query) == list:
        query = query[0]
    
    _filter = _filter or request.args.get('filter')
    if _filter is None:
        _filter = f'@FILED_DATE_YEAR:[{DEFAULT_YEAR_START},{DEFAULT_YEAR_END}]'
    elif type(_filter) == list:
        _filter = _filter[0]
     
    params = {'term':query, 'filter':_filter, 'log_guid':log_guid}
    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params=params)
    resp_data = resp.json()
    resp_data['results'] = filter(lambda result: result['COMPANY_NAME'] != 'N/A', resp_data['results'])
    return render_template('research/results-vss.html', **resp_data, facets=facets(query, _filter, serialize=False), query=query, filter=_filter, log_guid=log_guid)

@research.route('/faceted-search', methods=['POST'])
def faceted_search():
    data = request.form.to_dict(flat=False)
    print(data)
    _filter = ''
    if 'companies' in data:
        _filter += f'@COMPANY_NAME:{{{"|".join(data["companies"])}}} '
    if not data.get('10-K') or not data.get('10-Q'):
        if data.get('10-K'): # this is somehow backwards in redisearch - don't ask me why
            _filter += '@FILING_TYPE:10-Q '
        else:
            _filter += '@FILING_TYPE:10-K '
    
    year_start, year_end = data.get('yearStart')[0], data.get('yearEnd')[0]
    
    _filter += f'@FILED_DATE_YEAR:[{year_start or DEFAULT_YEAR_START},{year_end or DEFAULT_YEAR_END}] '
    
    return vss(data['query'][0], _filter.strip())


