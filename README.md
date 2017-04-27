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
