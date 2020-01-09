import json
from flask import Flask
from flask import request
app = Flask(__name__)

response_type = { 'ContentType':'application/json' }

from elasticsearch import Elasticsearch
es = Elasticsearch()

index_name = 'transactions'
with open('index_settings.json') as settings_file:
    index_settings = json.load(settings_file)

es.indices.create(index=index_name, body=index_settings, ignore=400)

def validate(data):
    """Function to validate transaction data"""
    if 'value' not in data or \
        'category' not in data or \
        'classification' not in data or \
        'account' not in data:
        raise Exception('Missing required field.')
    classifications = ['Personal', 'Essential', 'Savings', 'Income']
    if data['classification'] not in classifications:
        raise Exception('Invalid classification.')

@app.route('/', methods = ['POST'])
def transactions():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        try:
            validate(data)
        except Exception as e:
            return json.dumps({'message' : str(e)}), 400, response_type  

        try:
            res = es.index(index=index_name, doc_type='_doc', body=data)
        except Exception as e:
            return json.dumps({'message' : str(e)}), 500, response_type  

        return json.dumps({'message' : 'success'}), 200, response_type  
    else:
        return 'Not allowed!'
    

if __name__ == '__main__':
    app.run()
