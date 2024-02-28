## running dev

Start clean database (requires installed docker)

```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -p 5432:5432 --rm postgres
```

open pipenv shell

```bash
pipenv shell
```

Start app

```bash
flask --app opennote run --debug
```
