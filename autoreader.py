# Copyright 2025, werpyock
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__version__ = (1, 1, 0)
# meta developer: @wmodules

from .. import loader, utils
from telethon.tl.types import User, Chat, Channel

@loader.tds
class AutoReaderMod(loader.Module):
    """Авточиталка сообщений в указанных в конфиге чатов."""

    strings = {"name": "AutoReaderMod"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "CHATS", {}, lambda: "Словарь чатов для авточиталки (ID: название)."
        )

    async def client_ready(self, client, db):
        self.client = client

    def get_display_name(self, entity):
        if hasattr(entity, 'title'):
            return entity.title
        if hasattr(entity, 'first_name') or hasattr(entity, 'last_name'):
            return f"{entity.first_name or ''} {entity.last_name or ''}".strip()
        return str(entity)

    @loader.command()
    async def autoread(self, message):
        """Добавляет указанный чат в список авточиталки."""
        args = utils.get_args_raw(message)
        try:
            chat = await self.client.get_entity(args) if args else await message.get_chat()
        except ValueError:
            await message.edit("❌ Не удалось найти указанный чат.")
            return

        chat_id = chat.id
        chat_title = self.get_display_name(chat)

        if chat_id in self.config["CHATS"]:
            await message.edit(f"ℹ️ Чат '{chat_title}' уже находится в списке авточиталки.")
            return

        self.config["CHATS"][chat_id] = chat_title
        self.save_config()
        await message.edit(f"✅ Чат '{chat_title}' добавлен в авточиталку.")

    @loader.command()
    async def unautoread(self, message):
        """Удаляет указанный чат из списка авточиталки."""
        args = utils.get_args_raw(message)
        try:
            chat = await self.client.get_entity(args) if args else await message.get_chat()
        except ValueError:
            await message.edit("❌ Не удалось найти указанный чат.")
            return

        chat_id = chat.id
        chat_title = self.get_display_name(chat)

        if chat_id not in self.config["CHATS"]:
            await message.edit(f"❌ Чат '{chat_title}' отсутствует в списке авточиталки.")
            return

        del self.config["CHATS"][chat_id]
        self.save_config()
        await message.edit(f"✅ Чат '{chat_title}' удален из авточиталки.")

    @loader.command()
    async def autoreadlist(self, message):
        """Показывает список чатов в авточиталке."""
        if not self.config["CHATS"]:
            await message.edit("ℹ️ Список чатов для авточиталки пуст.")
            return

        chats_info = [f"{title} (ID: {id})" for id, title in self.config["CHATS"].items()]
        await message.edit("📋 Список чатов в авточиталке:\n" + "\n".join(chats_info))

    @loader.watcher()
    async def watcher(self, message):
        chat_id = utils.get_chat_id(message)
        if chat_id in self.config["CHATS"]:
            try:
                await message.mark_read()
            except Exception as e:
                logger.error(f"Ошибка при отметке сообщения как прочитанного: {e}")
