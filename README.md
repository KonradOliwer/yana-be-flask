# Yet another notes app
___
This is learning project. So take everything with grain of salt and don't emulate things without a thought.

This is [python](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/) + [SQLAlchemy](https://www.sqlalchemy.org/) implementation of backend
This version is currently not supported by frontend. Use tag [v0.1.0](https://github.com/KonradOliwer/yana-be-flask/tree/v0.1.0) to see compatible version.
For more details about project read frontend [README.md](https://github.com/KonradOliwer/yana-fe-react/)

## Using app
### Requirements
- [python 3.7](https://www.python.org/)
- [pipenv](https://pypi.org/project/pipenv/)
- [docker](https://www.docker.com/)

### TODO for production ready
In case of productions configuration (like dp user and password) should at least land into environment variables. Alternatively there can be a configuration file.
If we want higher level of security we might want to look for more sophisticated tools - like using AWS secret (if our infrastructure is on AWS).
For higher security we also would like to compile code and don't keep original source code on the server.

### Running the app
Install dependencies
```bash
pipenv install
```

Start db (this will drop DB on finishing process)
```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -p 5432:5432 --rm postgres
```

Run with debug mode
```bash
pipenv run flask run --debug  -p 8000
```

### Running tests
```bash
pipenv run pytest
```

## Development notes
### Migrations
For automatic generation of next migration use
```bash
pipenv run flask db migrate -m "<migration_name>"
```
Make sure to review migration code before commiting.

### Note about running in IDEA
Change script and  working directory to root directory'
