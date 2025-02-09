from django.db.models.signals import post_save
from django.dispatch import receiver
from app.web_app.models import Notification, User
from app.telegram.management.commands.run import bot
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Notification)
def send_notification_to_users(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Новое уведомление добавлено: {instance.text}")

        users = User.objects.filter(chat_id__isnull=False)

        for user in users:
            try:
                async_to_sync(bot.send_message)(user.chat_id, f"📢 Новое уведомление от админа:\n\n{instance.text}")
                logger.info(f"Уведомление отправлено пользователю {user.full_name} ({user.chat_id})")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления пользователю {user.full_name}: {e}")
