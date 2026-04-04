FROM postgres:15-alpine

RUN apk add --no-cache bash

COPY init-scripts/postgres/ /docker-entrypoint-initdb.d/

RUN find /docker-entrypoint-initdb.d -type f -name "*.sh" -exec sed -i 's/\r$//' {} \; \
    && find /docker-entrypoint-initdb.d -type f -name "*.sh" -exec chmod +x {} \;