from celery import shared_task
from django.core.mail import send_mail
from .models import AuthorCategory, Post, Author, Category, RegisterForm, PostCategory
import datetime

@shared_task
def new_post_notify(post):
    email_list = []

    for i in post.category.all():
        for j in AuthorCategory.objects.filter(category = i):
            email_list.append(j.author.user.email)

    send_mail(
        subject = f"New post {post.title}",
        message = f'{post.title} | {post.author} | {post.create_data} | {post.preview()}' + f'\nhttp://127.0.0.1:8000/news/{post.id}',
        from_email='test.for.sm@yandex.ru',
        recipient_list = email_list
    )

@shared_task
def weekly_mail():

        all_category = ["sport", "politics", "education", "culture"]
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