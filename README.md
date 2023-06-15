# UAX Telegram Bot + API

Everything should run as a charm, if you follow the steps:

- Have Docker daemon running
- Create `api/core/config/settings/.env` according to `.env.sample`
- Paste missing variable values (ask product owner)
- Do the same with `bot/config/settings/.env`

Now you're ready to run:

```shell
cd docker
docker-compose build
docker-compose up
```

