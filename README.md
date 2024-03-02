## running dev

Start database (requires installed docker) and drop it after closing

```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -p 5432:5432 --rm postgres
```

Run up (in debug mode)

```bash
pipenv run flask --app opennote run --debug
```
