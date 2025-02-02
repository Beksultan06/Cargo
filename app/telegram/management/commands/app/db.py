from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

async def get_user_by_chat_id(chat_id):
    return await sync_to_async(lambda: User.objects.filter(chat_id=chat_id).first())()

async def update_chat_id(user, chat_id):
    if user.chat_id != chat_id:
        user.chat_id = chat_id
        await sync_to_async(user.save)()

async def get_user_by_chat_id(chat_id):
    """Асинхронно получает пользователя по chat_id"""
    return await sync_to_async(lambda: User.objects.select_related("pickup_point").filter(chat_id=chat_id).first())()