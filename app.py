import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

response_type = { 'ContentType':'application/json' }

from elasticsearch import Elasticsearch, helpers
es = Elasticsearch()

def init():
    index_name = 'transactions'
    with open('index_settings.json') as settings_file:
        index_settings = json.load(settings_file)

    es.indices.create(index=index_name, body=index_settings, ignore=400)

init();

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

@app.route('/categories', methods = ['GET'])
@cross_origin()
def categories():
    index_name = 'categories'
    query = {
        "query": {
            "match_all": {}
        }
    }
    try:
        res = es.search(index=index_name, body=query)
        print(res)
        return {'categories' : res['hits']['hits']}, 200, \
            response_type
    except Exception as e:
        return json.dumps({'message' : str(e)}), 500, response_type

@app.route('/accounts', methods = ['GET'])
@cross_origin()
def accounts():
    index_name = 'accounts'
    query = {
        "query": {
            "match_all": {}
        }
    }
    try:
        res = es.search(index=index_name, body=query)
        print(res)
        return {'accounts' : res['hits']['hits']}, 200, \
            response_type
    except Exception as e:
        return json.dumps({'message' : str(e)}), 500, response_type

@app.route('/transactions', methods = ['GET', 'POST', 'DELETE'])
@cross_origin()
def transactions():
    index_name = 'transactions'
    if request.method == 'GET':
        try:
            ts = request.args.get('ts')
            id = request.args.get('id')
            if ts is not None:
                if id is None:
                    raise Exception('Missing id.')
                ts = int(ts)

            size = request.args.get('size')
            if size is not None:
                size = int(size)
            else:
                size = 25
            
        except Exception as e:
            return json.dumps({'message' : str(e)}), 400, response_type

        query = {
            "size": size,
            "query": {
                "match_all": {}
            },
            "sort": [
                {"date": "desc"},
                {"_id": "desc"}
            ]
        }

        if ts is not None:
            query['search_after'] = [ts, id]
        try:
            res = es.search(index=index_name, body=query)
            print(res)
            return {'transactions' : res['hits']['hits']}, 200, \
                response_type
        except Exception as e:
            return json.dumps({'message' : str(e)}), 500, response_type  
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        try:
            validate(data)
        except Exception as e:
            return json.dumps({'message' : str(e)}), 400, response_type  

        if 'id' in data:
            id = data['id']
            del data['id']
            try:
                res = es.index(index=index_name, doc_type='_doc', body=data, 
                    refresh="true", id=id)
            except Exception as e:
                return json.dumps({'message' : str(e)}), 500, response_type  
        else:
            try:
                res = es.index(index=index_name, doc_type='_doc', body=data, 
                    refresh="true")
            except Exception as e:
                return json.dumps({'message' : str(e)}), 500, response_type  

        return json.dumps({'message' : 'success'}), 200, response_type  
    if request.method == 'DELETE':
        ids = request.args.get('ids')
        ids = ids.split(",")
        actions = [
            {
                "_index" : index_name,
                "_id" : id,
                "_op_type" : "delete"
            }        
            for id in ids    
        ]

        try:
            helpers.bulk(es, actions, refresh="true")
            return json.dumps({'message' : 'success'}), 200, response_type  
        except Exception as e:
            return json.dumps({'message' : str(e)}), 500, response_type
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')
