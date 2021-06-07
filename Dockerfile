#Builder
FROM python:3.8-alpine as builder
ENV PYROOT /pyroot
ENV PATH=$PYROOT/bin:$PATH \
    PYTHONUSERBASE=$PYROOT

WORKDIR /app
RUN apk update && apk add --no-cache musl-dev openssl-dev gcc \
    py3-configobj supervisor libffi-dev

COPY code ./

RUN set -ex && pip install --upgrade pipenv && \
    PIP_USER=1 PIP_IGNORE_INSTALLED=1 \
    pipenv install --system --deploy


#Runner
FROM python:3.8-alpine
ENV USERNAME ciscosec

ENV PYROOT /pyroot
ENV PATH=$PYROOT/bin:$PATH \
    PYTHONUSERBASE=$PYROOT

RUN addgroup --system --gid=9999 $USERNAME && \
    adduser -S -u 9999 \
    -h $PYROOT \
    -G $USERNAME $USERNAME

COPY --from=builder --chown=$USERNAME:$USERNAME $PYROOT/lib/ $PYROOT/lib/
COPY --from=builder --chown=$USERNAME:$USERNAME $PYROOT/bin/ $PYROOT/bin/
COPY --from=builder --chown=$USERNAME:$USERNAME \
    /usr/local/lib/python3.8/site-packages/certifi \
    /$PYROOT/lib/python3.8/site-packages/certifi
COPY --from=builder --chown=$USERNAME:$USERNAME /app /app
COPY --chown=$USERNAME:$USERNAME scripts /

RUN apk update && apk add --no-cache supervisor uwsgi-http syslog-ng \
     uwsgi-python3 uwsgi-syslog git uwsgi-http

RUN mv /uwsgi.ini /etc/uwsgi && \
    addgroup $USERNAME uwsgi && addgroup uwsgi $USERNAME && \
	chmod +x /*.sh && \
	chown -R $USERNAME:$USERNAME /var/log && \
    chown -R $USERNAME:$USERNAME /run && \
    chown -R $USERNAME:$USERNAME /usr/sbin/uwsgi && \
    chown -R $USERNAME:$USERNAME /etc/uwsgi

USER $USERNAME
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]