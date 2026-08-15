from celery import shared_task


@shared_task
def hello_pingger():

    print("Hello from Celery!")

    return "Celery is working!"