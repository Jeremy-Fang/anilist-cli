import asyncio
import webbrowser

from aiohttp import web


def open_browser(url: str) -> None:
    webbrowser.open(url)


async def run_callback_server(
    port: int, path: str = "/callback", timeout: float = 120.0
) -> str | None:
    fut: asyncio.Future[str | None] = asyncio.get_running_loop().create_future()

    async def on_callback(request: web.Request) -> web.Response:
        fut.set_result(request.rel_url.query.get("code"))
        return web.Response(
            text="<html><body><h1>Authorized. You can close this tab.</h1>"
                 "</body></html>",
            content_type="text/html",
        )

    app = web.Application()
    app.router.add_get(path, on_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "localhost", port).start()

    try:
        auth_code = await asyncio.wait_for(fut, timeout=timeout)
        await asyncio.sleep(0.5)
    except TimeoutError:
        auth_code = None
    finally:
        await runner.cleanup()

    return auth_code
