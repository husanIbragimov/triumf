FROM python:3.9

ADD home/jamoc/sites/api.triumf-express.uz/triumf/requirements.txt home/jamoc/sites/api.triumf-express.uz/triumf/requirements.txt

RUN set -ex \
    && apk add --no-cache --virtual .build-deps postgresql-dev build-base \
    && python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r home/jamoc/sites/api.triumf-express.uz/triumf/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps

ADD django-polls /app
WORKDIR /home/jamoc/sites/api.triumf-express.uz/triumf

ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

EXPOSE 8050

CMD ["triumf", "--bind", ":8050", "--workers", "5", "config.wsgi"]


 