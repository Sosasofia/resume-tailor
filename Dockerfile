FROM python:3.12-slim

RUN useradd \
    --create-home \
    --shell /bin/bash \
    dev

RUN mkdir -p /workspace && \
    chown -R dev:dev /workspace

WORKDIR /workspace

USER dev

CMD ["bash"]
