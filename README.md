# MiniTwit
Origin: https://github.com/pallets/flask/tree/master/examples/minitwit

## Setup
### Install dependencies
```
pip install --editable .[dev]
```

### Initialize database
```
createdb minitwit
psql minitwit < server/schema.sql
```

### Set environments variables
```
cp .env.example .env
```

## Run Server
```
honcho start
```

## Test
```
python setup.py test
```

## Lint
```
flake8 server
```

## Run with Docker
### Setup
```
docker-compose build
docker-compose run --rm -e FLASK_APP=server web flask initdb
```

### Run
```
docker-compose up
```

## Frontend
### Setup
```
npm install
```

### Start development
```
npm start
```
