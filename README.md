## Requirements
- python 3.7
- pipenv
- docker

## TODO for production ready
In case of productions configuration (like dp user and password) should at least land into environment variables. Alternatively there can be a configuration file.
If we want higher level of security we might want to look for more sophisticated tools - like using AWS secret (if our infrastructure is on AWS).

For higher security we also would like to compile code and don't keep original source code on the server.

## running in development
Before first run install dependencies
```bash
pipenv install
```

Start database (requires installed docker) and drop it after closing

```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -p 5432:5432 --rm postgres
```

Run with debug mode

```bash
pipenv run flask --app opennote run --debug
```
