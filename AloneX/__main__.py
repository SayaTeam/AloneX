# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import asyncio
import importlib
import sys

from pyrogram import idle

from AloneX import (anon, app, config, db,
                   logger, stop, userbot, yt)
from AloneX.core.web import start_web_server
from AloneX.plugins import all_modules


async def main():
    await start_web_server()
    
    try:
        await db.connect()
    except Exception as ex:
        logger.error(f"MongoDB connection notice: {ex}")

    try:
        await app.boot()
    except Exception as ex:
        logger.error(f"Bot boot error: {ex}")

    try:
        await userbot.boot()
    except Exception as ex:
        logger.error(f"Userbot boot error: {ex}")

    try:
        await anon.boot()
    except Exception as ex:
        logger.error(f"PyTgCalls boot error: {ex}")

    for module in all_modules:
        try:
            importlib.import_module(f"AloneX.plugins.{module}")
        except Exception as ex:
            logger.error(f"Failed to load plugin {module}: {ex}")

    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        try:
            await yt.save_cookies(config.COOKIES_URL)
        except Exception as ex:
            logger.error(f"Error saving cookies: {ex}")

    try:
        sudoers = await db.get_sudoers()
        app.sudoers.update(sudoers)
        app.bl_users.update(await db.get_blacklisted())
        logger.info(f"Loaded {len(app.sudoers)} sudo users.")
    except Exception as ex:
        logger.error(f"Error loading sudoers: {ex}")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
