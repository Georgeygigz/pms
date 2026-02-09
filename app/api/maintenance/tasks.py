from celery import shared_task


@shared_task
def send_work_order_notification(work_order_id):
    print(f"Notification: work order created {work_order_id}")