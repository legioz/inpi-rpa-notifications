# **INPI** RPA Notifications

Automation of **INPI** protocol update notifications.
**INPI** requires the user who requested a service to access the [website](http://revistas.inpi.gov.br/rpi/) weekly to download the magazine and check the status of the protocol.

## Requirements

| Tech | Version |
| --- | --- |
| [Python](https://www.python.org/) | 3.9.5 |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.78.0 |
| [Docker](https://docs.docker.com/) | 20.10.16 |
| [Docker-Compose](https://docs.docker.com/compose/) | 2.5.0 |
| [Deta.sh](https://docs.deta.sh/docs/home/) | 1.1.0 |
| [Bootstrap](https://getbootstrap.com/docs/5.2/getting-started/introduction/) | 5.2 |


## Running locally in development

Using Docker Compose:

```sh
docker-compose build
docker-compose up -d
```

Using VENV:

```sh
python -m venv venv
source venv/bin/activate
uvicorn main:app --reload
```

Project will be running on http://localhost:8000

### .ENV file

```sh
PROJECT_KEY=""
PROJECT_ID=""
```
