# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

from pyrogram import Client
from AloneX import config, logger


class Userbot:
    def __init__(self):
        """
        Initializes the userbot with multiple clients.
        """
        self.clients = []
        clients = {"one": "SESSION1", "two": "SESSION2", "three": "SESSION3"}
        for key, string_key in clients.items():
            name = f"AloneXUB{key[-1]}"
            session = getattr(config, string_key, None)
            if session and session != "?":
                setattr(
                    self,
                    key,
                    Client(
                        name=name,
                        api_id=config.API_ID,
                        api_hash=config.API_HASH,
                        session_string=session,
                    ),
                )
            else:
                setattr(self, key, None)

    async def boot_client(self, num: int, ub: Client):
        if not ub:
            return
        await ub.start()
        try:
            await ub.send_message(config.LOGGER_ID, "Assistant Started")
        except Exception as ex:
            logger.warning(f"Assistant {num} failed to send message in log group: {ex}")

        ub.id = ub.me.id
        ub.name = ub.me.first_name
        ub.username = ub.me.username
        ub.mention = ub.me.mention
        self.clients.append(ub)
        try:
            await ub.join_chat("SayaTeam")
        except:
            pass
        logger.info(f"Assistant {num} started as @{ub.username}")

    async def boot(self):
        if config.SESSION1 and self.one:
            await self.boot_client(1, self.one)
        if config.SESSION2 and self.two:
            await self.boot_client(2, self.two)
        if config.SESSION3 and self.three:
            await self.boot_client(3, self.three)

    async def exit(self):
        if config.SESSION1 and self.one:
            try:
                await self.one.stop()
            except:
                pass
        if config.SESSION2 and self.two:
            try:
                await self.two.stop()
            except:
                pass
        if config.SESSION3 and self.three:
            try:
                await self.three.stop()
            except:
                pass
        logger.info("Assistants stopped.")
