# Django application on Google Cloud Platform.

<!-- START doctoc -->
<!-- END doctoc -->

## Introduction

django microservices python 3.9
[![Restaurant Tests](https://github.com/delitamakanda/restaurant/actions/workflows/restaurant_tests.yml/badge.svg?branch=main&event=push)](https://github.com/delitamakanda/restaurant/actions/workflows/restaurant_tests.yml)

## Restaurant application

django restaurant multi tenant application

```bash
python3 manage.py runserver
```

## logging

```bash
>>> import structlog
>>> logger = structlog.getLogger()
>>> logger.info('hello world', key='value', more=[1,2,3]
... )
2023-06-25 21:15:19 [info     ] hello world                    key=value more=[1, 2, 3]
>>>
```

## Links

- [ Python on Google Cloud](https://cloud.google.com/python)
- [Running Django on the App Engine standard environment](https://cloud.google.com/python/django/appengine)
- [Running Django on the App Engine flexible environment](https://cloud.google.com/python/django/flexible-environment)
- [Running Django on the Cloud Run environment ](https://cloud.google.com/python/django/run)
