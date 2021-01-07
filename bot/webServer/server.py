import asyncio
import logging
from typing import Final, NoReturn

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from ..Exceptions import USERCHAT_STR_WRONG_FORMAT
from ..config import config
from ..handlers import onSuccess
from ..userChat import userChat

routes = web.RouteTableDef()
logger: Final = logging.getLogger(__name__)


def html_response(text: str):
    return web.Response(text=text, content_type='text/html')


@routes.post('/response')
async def resp(request):
    data = await request.post()
    response = data['h-captcha-response']
    if not response:
        raise web.HTTPUnauthorized
    logger.info("%s submited form", data['ids'])
    session = request.app['client_session']
    correct: bool = await checkResponse(response, session)
    if not correct:
        return html_response("<h1>Verification Failed</h1>")
    try:
        user_chat: userChat = userChat.parseStr(data['ids'])
        logger.info("correct by user %s in %s chat", user_chat.userId, user_chat.chatId)
    except USERCHAT_STR_WRONG_FORMAT:
        return html_response("<h1>Thanks for Solving </br> But url format is incorrect</h1>")
    else:
        await onSuccess(user_chat.userId, user_chat.chatId)  # unMute in the group
        return html_response("<h1>Verification Successful</h1>")


@routes.get("/")
async def root_route_handler(_):
    return web.json_response({"status": "running"})


@routes.get("/{userchat}")
async def index(request):
    context = {'uc': request.match_info['userchat'],
               'ctitle': 'Hello there'}
    return await aiohttp_jinja2.render_template_async(
        'captchaPage.html', request, context=context)


async def checkResponse(response: str, session):
    async with session.post('https://hcaptcha.com/siteverify',
                            data={'response': response,
                                  'secret': config.HCAPTCHA_API,
                                  'sitekey': 'acece2fb-a692-41fd-8507-1a5b630ef353'}) as rsp:
        txt = await rsp.json()
        logger.info(txt)
        return txt.get('success', False)


async def client_session_ctx(appObj: web.Application) -> NoReturn:
    logger.debug('Creating ClientSession')
    appObj['client_session'] = aiohttp.ClientSession()

    yield

    logger.debug('Closing ClientSession')
    await appObj['client_session'].close()


async def start():
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(client_session_ctx)
    aiohttp_jinja2.setup(
        app, enable_async=True,
        loader=jinja2.FileSystemLoader("bot/webServer/resources/"))  # todo: change path
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    await aiohttp.web.TCPSite(runner, host='0.0.0.0', port=80).start()
    logger.info("WebServer Started")
    # await asyncio.Event().wait()  # blocking


if __name__ == "__main__":
    # uncomment line 86
    asyncio.run(start())
