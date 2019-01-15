FROM python:3.6-alpine as builder

RUN apk --update add --no-cache git build-base libffi-dev openssl-dev

ARG whl=/tmp/wheelhouse
WORKDIR /tmp
COPY . .
RUN pip wheel --wheel-dir=${whl} .

FROM python:3.6-alpine
ARG whl=/tmp/wheelhouse

COPY --from=builder ${whl} ${whl}
RUN pip install --find-links ${whl} ${whl}/zeta-*.whl
RUN rm -r ${whl}

# this is for click
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
CMD ["zeta-bot"]