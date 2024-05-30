# Restaurant application

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
