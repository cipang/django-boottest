web: gunicorn boottest.wsgi --log-file -
worker: python3 boottest/manage.py rqworker high default low
