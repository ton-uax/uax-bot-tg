# from core.config.celery import app as celery_app
# from core.apps.broadcast import models as broadcast_models
# from core.apps.account import models as account_models
# from core.package.helpbot import services as helpbot_services
#
# from django.utils import timezone
#
#
# @celery_app.task
# def check_broadcast_query():
#     query = broadcast_models.BroadcastQuery.objects.filter(action="queue_for_sending", status=False)
#
#     if query.exists():
#         for msg in query:
#             users = account_models.TelegramAccount.objects.filter(blocked_bot=False)
#             helpbot_services.broadcast(users, msg.text, msg.keyboard)
#             msg.status = True
#             msg.save()
