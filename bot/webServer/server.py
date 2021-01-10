import asyncio
import logging
from typing import Final, NoReturn

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from ..webServer.hash import checkHash, getCheckString
from ..Exceptions import USERCHAT_STR_WRONG_FORMAT
from ..config import config
from ..handlers import onSuccess
from ..userChat import userChat

routes = web.RouteTableDef()
logger: Final = logging.getLogger(__name__)

routes.static('/styles.css', 'bot/webServer/resources/')


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
        checkString = data['payload'].replace("\r\n", "\n")
        if checkHash(checkString, data['hash']):
            await onSuccess(user_chat.userId, user_chat.chatId)  # unMute in the group
            return html_response("<h1>Verification Successful</h1>")
        else:
            return html_response("<h1>Thanks for Solving </h1> </br> But it was a fake url")
    except USERCHAT_STR_WRONG_FORMAT:
        return html_response("<h1>Thanks for Solving </h1> </br> But url format is incorrect")
    except KeyError:
        return html_response("<h1>Sorry. Not expected user</h1> </br> Maybe your time limit is reached !")


@routes.get("/")
async def root_route_handler(_):
    return web.json_response({"status": "running"})


@routes.get("/{chatid}")
async def index(request):
    argDict = request.rel_url.query
    context = {'uc': argDict['id'] + '_' + request.match_info['chatid'],
               'ctitle': f'Hello {argDict.get("first_name", "there")}',
               'payload': getCheckString(argDict),
               'hash': argDict['hash']}
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
    # uncomment line 89
    asyncio.run(start())
