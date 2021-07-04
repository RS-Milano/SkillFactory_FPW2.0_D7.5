import logging, datetime

from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail
from ...models import AuthorCategory, PostCategory, Category

 
logger = logging.getLogger(__name__)

all_category = ["sport", "politics", "education", "culture"]
 
# наша задача по выводу текста на экран
def my_job():
    for i in all_category:
        email_list = []
        posts_id = []
        posts_list = ""

        for j in AuthorCategory.objects.filter(category = Category.objects.get(category = i)):
            if j.author.user.email not in email_list:
                email_list.append(j.author.user.email)
            
            for n in PostCategory.objects.filter(category = Category.objects.get(category = i)):
                if n.post.create_data.timestamp() > (datetime.datetime.now().timestamp() - 604800):
                    posts_id.append(n.post.id)
            
            for my_post in posts_id:
                posts_list += f'\nhttp://127.0.0.1:8000/news/{my_post}'

            print(email_list)
            print(posts_id)
            print(posts_list)
            if posts_list:
                send_mail(
                    subject = f"Тew posts this week",
                    message = posts_list,
                    from_email='test.for.sm@yandex.ru',
                    recipient_list = email_list
                )
 
# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")