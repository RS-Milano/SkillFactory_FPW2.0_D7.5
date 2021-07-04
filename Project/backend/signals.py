# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from .models import Post, AuthorCategory, Category, PostCategory
# import datetime

# @receiver(post_save, sender = Post)
# def new_post_notify(sender, instance, created, **kwargs):
#     if created:
#         email_list = []
#         for i in Post.objects.get(id = instance.id).category.all():
#             for j in AuthorCategory.objects.filter(category = i):
#                 email_list.append(j.author.user.email)
        
#         send_mail(
#             subject = f"New post {instance.title}",
#             message = f'{instance.title} | {instance.author} | {instance.create_data} | {instance.preview()}' + f'\nhttp://127.0.0.1:8000/news/{instance.id}',
#             from_email='test.for.sm@yandex.ru',
#             recipient_list = email_list
#         )

#         # all_category = ["sport", "politics", "education", "culture"]
#         all_category = ["sport"]
#         for i in all_category:
#             email_list = []
#             posts_id = []
#             posts_list = ""


#             for j in AuthorCategory.objects.filter(category = Category.objects.get(category = i)):
#                 if j.author.user.email not in email_list:
#                     email_list.append(j.author.user.email)
            
#             for n in PostCategory.objects.filter(category = Category.objects.get(category = i)):
#                 if n.post.create_data.timestamp() > (datetime.datetime.now().timestamp() - 604800):
#                     posts_id.append(n.post.id)
            
#             for my_post in posts_id:
#                 posts_list += f'\nhttp://127.0.0.1:8000/news/{my_post}'

#             print(email_list)
#             print(posts_id)
#             print(posts_list)
#             if posts_list:
#                 send_mail(
#                     subject = f"Тew posts this week",
#                     message = posts_list,
#                     from_email='test.for.sm@yandex.ru',
#                     recipient_list = email_list
#                 )