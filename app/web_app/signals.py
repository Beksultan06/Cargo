from django.db.models.signals import post_save
from django.dispatch import receiver
from app.web_app.models import Notification, User
from app.telegram.management.commands.run import bot
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Notification)
def send_notification_to_users(sender, instance, created, **kwargs):
    if created:

        users = User.objects.filter(chat_id__isnull=False)

        for user in users:
            try:
                async_to_sync(bot.send_message)(user.chat_id, f"📢 Новое уведомление от админа:\n\n{instance.text}")
            except Exception as e:
                pass
