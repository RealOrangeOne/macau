# Macau

A simple and efficient URL shortener.

## Features

- Responsive, accessible admin interface with dark mode.
- High-performance. Easily handles thousands of redirects per second
- Permanent / non-permanent redirects
- Supports protecting redirects with basic auth
- Supports multiple user login, with group permissions management
- Easily create redirect by prefixing the URL eg (`macau.example.com/https://github.com/realorangeone/macau`)

## Usage

The easiest deployment is using Docker:

```yml
services:
  macau:
    image: ghcr.io/realorangeone/macau:latest
    restart: unless-stopped
    volumes:
        - ./data:/data
    environment:
        DATABASE_URL=sqlite:////data/db.sqlite3
        SECRET_KEY=changeme
```

Once deployed, connect to the container and run `./manage.py createsuperuser`. You can then log in at `/-/admin/`

## Configuration

Configuration is done through environment variables.

- `DATABASE_URL` (required): Database connection URL. SQLite (`sqlite:///<path>`) and PostgreSQL (`postgres://user:password@localhost/db`)
- `SECRET_KEY` (required): Set to a secret value. [Generate](https://realorangeone.github.io/django-secret-key-generator/).
- `ALLOWED_HOSTS`: A list of hostnames to restrict which URLs the application will serve. By default this is unrestricted.
- `ROOT_REDIRECT_URL`: The URL to redirect `/` to. By default, the root URL will 404.

The web server used is `granian` which has its own [environment variables](https://github.com/emmett-framework/granian/#options).
