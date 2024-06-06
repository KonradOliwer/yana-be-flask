# Yet another notes app
___
This is learning project. So take everything with grain of salt and don't emulate things without a thought.

This is [python](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/) + [SQLAlchemy](https://www.sqlalchemy.org/) implementation of backend
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

Building database from scratch is good thing for development but for production we should have some kind of migration system. 
We could use [Alembic](https://alembic.sqlalchemy.org/en/latest/) for that.

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
pipenv run flask --app opennote run --debug  -p 8000
```

### Running tests
```bash
pipenv run pytest
```
