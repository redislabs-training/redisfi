import requests
from flask import Blueprint, current_app, request, render_template

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
    url = current_app.config.get('VSS_URL')
    resp = requests.get(url, params={'term':query})
    resp_data = resp.json()
    return render_template('research/results.html', **resp_data)



