from celery.signals import worker_ready

from app.tasks.sampling import init_dft_sample_map


@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    init_dft_sample_map.delay()
