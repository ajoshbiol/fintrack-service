# fintrack-service

REST service for Fintrack project

## Getting Started

### Prerequisites

Python 3 and pip. Using virtualenv is recommended.
Elasticsearch `7.5.1` service running locally for now.

```
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.1
```

### Installing

Create you virtual environment.

```
virtualenv --python=python3 venv
```

Install Python dependencies.

```
pip install -r requirements.txt
```

## Running the tests

No tests yet.

## Deployment

Manual at the moment.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Josh Biol**

