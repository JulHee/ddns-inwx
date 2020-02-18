# ddns-inwx

A dyndns server to continually update subdomain nameserver records for
inwx domains via basic HTTP requests and querystrings.

## Setup
Copy config.example.yaml to config.yaml and edit login information
as needed.

This service should be run behind a reverse proxy for ssl support.

### Running behind a reverse proxy (recommend)

```
docker-compose -f docker-compose.proxy.yml up -d
```

Configure your reverse proxy to use uwsgi protocol

#### Nginx (Example)

You need to add your ssl configuration into the server block.

```
upstream docker-ddns-inwx {
  server 127.0.0.1:5050;
}

server {
  listen 80;
  server_name test-a.domain.tld;
  access_log /var/log/test-a.domain.tld/access_log;
  location / {
    uwsgi_pass docker-ddns-inwx;
    include uwsgi_params;
    proxy_redirect     off;
    proxy_set_header   Host $host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Host $server_name;
  }
}
```

### Running as a single service

```
docker-compose up -d
```

The server should be reachable under `http://127.0.0.1:5050`

### Setting up subdomains

Start the server, e.g. with docker-compose:
```
$ docker-compose build
$ docker-compose up -d
```

Generate an API secret for each subdomain, e.g.:

```
$ docker exec -it ddns-inwx_flask_1 flask dns add test-a.domain.tld
```


You can now update the record with curl in the following way:
```
$ curl localhost:5050/update\?myip=127.0.0.1\&myipv6=::1\&key=F8LBaSpLvIOrb83i08PI9g
```
