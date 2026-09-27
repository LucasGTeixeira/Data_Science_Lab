# Docker Guide

> A "when do I reach for this?" reference. Every section starts with the
> situation that calls for it, then the commands.

Docker packages an app with everything it needs to run — OS libraries, Python,
system tools — into one portable unit. It solves "works on my machine": the
same image runs identically on your laptop, a teammate's, and a server. This
lab is Docker-first (see the repo README for the Jupyter container), and this
guide is the general-purpose reference.

## Core concepts

Analogy that covers most of it:

- **Dockerfile** = recipe (build steps).
- **Image** = frozen meal made from the recipe (read-only template).
- **Container** = one serving, heated up (running instance of an image).
- **Volume** = the data that survives when the container is thrown away.
- **Network** = lets containers reach each other.
- **Registry** = the store images come from (Docker Hub).

```
Dockerfile -> image -> container
image      = read-only template
container  = running instance of an image
volume     = persistent storage
network    = lets containers talk
registry   = image store (Docker Hub)
```

The mental shift from VMs: containers share the host kernel, start in
milliseconds, and are **disposable**. Anything not written to a volume is gone
when the container is removed — that's a feature, not a bug.

## Install check

> **When:** new machine, or a command fails with "cannot connect to the Docker
> daemon".

```bash
docker --version
docker info                       # daemon status
docker run hello-world            # smoke test
```

## Images

> **When:** `pull` to grab an existing environment (postgres, python); `build`
> to make your own from a Dockerfile. Images are what you version and share.

```bash
docker images                     # list local images
docker pull nginx                 # download
docker pull nginx:1.27            # specific tag
docker build -t myapp .           # build from ./Dockerfile
docker build -t myapp:v1 .        # with tag
docker tag myapp:v1 user/myapp:v1 # rename/retag
docker push user/myapp:v1         # upload
docker rmi nginx                  # delete image
docker image prune                # remove dangling images
```

Use readable, pinned tags (`nginx:1.27`, `myapp:v1`) — `latest` is a moving
target and will bite you at the worst time.

## Containers

> **When:** actually running something. `run` creates a new container from an
> image; `start` restarts an existing stopped one. `-d` for background
> services, `-it` when you need a shell, `--rm` for throwaway containers.

```bash
docker run nginx                  # run (foreground, Ctrl+C stops it)
docker run -d nginx               # detached (background)
docker run -it ubuntu bash        # interactive shell
docker run --name web -p 8080:80 -d nginx   # name + port map
docker run -v $(pwd):/app -w /app python:3 python app.py  # mount + workdir
docker run --rm alpine echo hi     # auto-delete on exit
docker run -e KEY=value myapp      # env var
docker run --env-file .env myapp   # env from file

docker ps                         # running containers
docker ps -a                      # all (incl. stopped)
docker stop web                   # graceful stop (SIGTERM, then kill)
docker start web                  # start stopped
docker restart web
docker rm web                     # delete stopped
docker rm -f web                  # force delete running
docker logs web                   # logs
docker logs -f web                # follow logs (like tail -f)
docker exec -it web bash          # shell into running container
docker cp web:/path/file .        # copy out
docker inspect web                # full JSON details
docker stats                      # live resource usage
```

Two gotchas that waste the most time:

- `-p 8080:80` is `host:container`, not the reverse. The app listens on 80
  inside; you reach it on 8080 outside.
- A file written inside a container is gone when it's removed unless it lives
  on a volume or bind mount.

## Dockerfile

> **When:** you have code that should run the same everywhere, or you want to
> hand someone an app/notebook that starts with one command.

```dockerfile
FROM python:3.12-slim        # base image
WORKDIR /app                 # set working dir
COPY requirements.txt .      # copy file in
RUN pip install -r requirements.txt   # build step
COPY . .                     # copy rest
ENV PORT=8000                # env var
EXPOSE 8000                  # document port
CMD ["python", "app.py"]     # default command
```

Build: `docker build -t myapp .`

Order matters: copy `requirements.txt` and `RUN pip install` **before**
`COPY . .`. Docker caches each step, so later code changes only re-run the last
layers instead of reinstalling dependencies every build.

`.dockerignore` (speeds build, shrinks image):

```
.git
__pycache__
*.pyc
.env
node_modules
```

## Volumes (persistence)

> **When:** data must survive container removal — database files, processed
> datasets, anything you'd hate to lose. Bind mounts when you want to edit
> files on the host and have the container see changes live.

```bash
docker volume create data
docker volume ls
docker volume rm data
docker run -v data:/var/lib/mysql mysql   # named volume
docker run -v $(pwd)/data:/data alpine    # bind mount
docker run --mount type=bind,src=$(pwd),dst=/app myapp  # explicit mount
```

Named volume = Docker-managed (keep data). Bind mount = host path (edit live).
Rule of thumb: bind mounts while developing, named volumes for anything Docker
should own and preserve.

## Networks

> **When:** two or more containers need to talk (app → database, notebook →
> Spark). By default containers are isolated.

```bash
docker network create mynet
docker network ls
docker network inspect mynet
docker run --network mynet --name db postgres
docker run --network mynet myapp         # reach db by name "db"
```

Containers on the same network resolve each other by name. Compose creates a
network per project automatically, so you rarely build one by hand.

## Docker Compose

> **When:** more than one container, or you're tired of typing long `run`
> commands. Compose turns the whole stack (services, volumes, ports) into one
> versioned file — and `docker compose up` starts it all.

`docker-compose.yml`:

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
    depends_on:
      - db
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

```bash
docker compose up -d              # build + start all
docker compose up --build         # rebuild then start
docker compose ps                 # status
docker compose logs -f web        # logs for one service
docker compose exec web bash      # shell into service
docker compose down               # stop + remove
docker compose down -v            # also remove volumes (wipes data)
```

## Housekeeping

> **When:** Docker is eating your disk (`docker system df` tells you). Prune
> removes unused things — read the flags, the aggressive one removes data.

```bash
docker system df                  # disk usage
docker system prune               # remove unused (images, nets, cache)
docker system prune -a --volumes  # aggressive: remove EVERYTHING unused
docker container prune
docker volume prune
```

## Debugging

> **When:** a container won't start, exits immediately, or the app misbehaves.
> Order that solves most cases: `logs` (what happened) → `exec` (look inside)
> → `inspect` (configuration).

```bash
docker run -it --entrypoint sh myapp   # override entrypoint to get a shell
docker inspect --format '{{.State.Status}}' web
docker logs --tail 50 web
docker events                     # live daemon events
```

A container that exits instantly usually crashed at startup; `docker logs
<name>` shows the traceback. If there are no logs, run it with `-it
--entrypoint sh` and poke around.

## Golden rules

- Pin image tags (`python:3.12-slim`, not `latest`) for reproducible builds.
- Use multi-stage builds to shrink production images.
- Keep secrets out of images — pass via env/`--env-file`, never `COPY .env`.
- One process per container.
- Named volumes for data you must keep; `down -v` deletes volumes.
