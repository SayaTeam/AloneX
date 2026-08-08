# ALONE-CODER
import os
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="AloneX Music Bot is running!", status=200)

async def start_web_server():
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/healthz", health_check)
    app.router.add_get("/ping", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server started and listening on 0.0.0.0:{port}")
