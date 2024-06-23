#!/bin/sh
gunicorn restaurant.wsgi --log-file -
