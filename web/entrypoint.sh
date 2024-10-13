#!/bin/bash

gunicorn -b 0.0.0.0:5000 wsgi:app

flask db init
flask db migrate -m "new-migration"
flask db upgrade