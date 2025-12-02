# Macau

A simple and efficient URL shortener.

## Features

- Responsive, accessible admin interface with dark mode.
- High-performance. Easily handles thousands of redirects per second
- Permanent / non-permanent redirects
- Protect redirects with basic auth
- Multiple user login, with group permissions management
- Easily create redirect by prefixing the URL eg (`macau.example.com/https://github.com/realorangeone/macau`)
- No analytics or tracking of click counts or IP addresses
- Import / export via multiple formats (CSV, JSON etc)

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

- `DATABASE_URL` (required): Database connection URL. SQLite (`sqlite:///<path>`) and PostgreSQL (`postgres://user:password@localhost/db`) are supported.
- `SECRET_KEY` (required): Set to a secret value. [Generate](https://realorangeone.github.io/django-secret-key-generator/).
- `ALLOWED_HOSTS`: A list of hostnames to restrict which URLs the application will serve. By default this is unrestricted.
- `ROOT_REDIRECT_URL`: The URL to redirect `/` to, or `"admin"` to redirect to the admin interface. By default, the root URL will 404.
- `TZ`: Timezone to use (eg `Europe/London`)

The web server used is `granian` which has its own [environment variables](https://github.com/emmett-framework/granian/#options).

## Another?

Yes, I made _another_ URL shortener. URL shorteners are fairly easy to build, and this means I can add all the features I want. If you like these features too, or want an easy path to contribute or suggest them, this might be the project for you.
