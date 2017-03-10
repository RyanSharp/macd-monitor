from celery.schedules import crontab


BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_IMPORTS = ["utils.tasks"]
 
CELERY_RESULT_BACKEND = "amqp"
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_RESULT_EXPIRES = None
 
CELERY_DEFAULT_QUEUE = "default"
CELERY_QUEUES = {
    "default": {
        "binding_key": "task.#",
    },
    "stock": {
        "binding_key": "stock.#",
    },
}
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
CELERY_DEFAULT_ROUTING_KEY = "task.default"
CELERY_ROUTES = {
    "utils.tasks.run_update_for_ticker": {
        "queue": "stock",
        "routing_key": "stock.ticker_update"
    },
    "utils.tasks.queue_stock_matrix_update": {
        "queue": "stock",
        "routing_key": "stock.system_trigger"
    },
}
CELERYBEAT_SCHEDULE = {
    "stock-matrix-update": {
        "task": "utils.tasks.queue_stock_matrix_update",
        "schedule": crontab(minute="*/10")
    }
}
