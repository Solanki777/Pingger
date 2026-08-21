1. CMD no. 1 :

    1. docker start pingger-redis

    if it says " pingger-redis "
    go for 

    2.docker run --name pingger-redis -p 6379:6379 -d redis

    once the container has been created 

    3. docker start pingger-redis

2. CMD no . 2
    1. activate the environment : venv\Scripts\activate
    2. python manage.py runserver

3. CMD no.3
    1. celery -A config worker --loglevel=INFO --pool=solo

    wait until you see connected to redis : // localhost : ... and celery@...

4. CMD no.4
    1. celery -A config beat --loglevel=INFO