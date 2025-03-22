FROM python:3.12 AS base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/medlog/"
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Builder stage to install dependencies
# This stage is separate so if the requirements.txt file hasn't changed, it will be cached
FROM base AS builder

RUN apt-get update \
    && apt-get install -y \
    curl gcc libc-dev musl-dev libpq-dev

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

COPY ./requirements.txt /medlog/
WORKDIR /medlog
RUN /root/.local/bin/uv venv /opt/venv && \
    /root/.local/bin/uv pip install --no-cache -r requirements.txt

# Final stage to create the runnable image with minimal size
FROM python:3.12-slim-bookworm AS final

COPY --from=builder /opt/venv /opt/venv

COPY run-backend.sh .
RUN chmod +x /run-backend.sh

RUN apt-get update \
    && apt-get install -y \
    libglib2.0-dev libpango-1.0-0 libpangoft2-1.0-0 gettext \
    && apt-get update

COPY ./medlog /medlog

RUN useradd -ms /bin/bash app
WORKDIR /medlog

RUN chown -R app:app /medlog
RUN chmod 755 /medlog

USER app

EXPOSE 8000

# Activate the virtualenv in the container
# See here for more information:
# https://pythonspeed.com/articles/multi-stage-docker-python/
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/run-backend.sh"]
