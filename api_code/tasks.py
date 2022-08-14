from celery import Celery
from phoneai_api import settings

app = Celery('tasks', backend=None)
app.conf.broker_url = settings.REDIS_BROKER


@app.task
def process_menu_audio(vm_data):

    pass


@app.task
def process_cdr_audio(cdr_data):

    pass
