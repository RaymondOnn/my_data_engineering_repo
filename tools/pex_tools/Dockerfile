ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION:-3.10}-slim

WORKDIR /build
ENV VIRTUAL_ENV=./venv
RUN python -m venv ${VIRTUAL_ENV} && ${VIRTUAL_ENV}/bin/pip3 install pex


ENV PATH= "${VIRTUAL_ENV}/bin:$PATH"
RUN pex pex requests -c pex -o /usr/local/bin/pex && rm -rf pex

