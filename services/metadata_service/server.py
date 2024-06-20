import asyncio
import os

from aiohttp import web

from .api.run import RunApi
from .api.flow import FlowApi

from .api.step import StepApi
from .api.task import TaskApi
from .api.artifact import ArtificatsApi
from .api.admin import AuthApi

from .api.metadata import MetadataApi
from services.data.postgres_async_db import AsyncPostgresDB
from services.utils import DBConfiguration

import logging
import time


def app(loop=None, db_conf: DBConfiguration = None, middlewares=None):

    loop = loop or asyncio.get_event_loop()
    app = web.Application(loop=loop, middlewares=middlewares)
    async_db = AsyncPostgresDB()
    loop.run_until_complete(async_db._init(db_conf))
    FlowApi(app)
    RunApi(app)
    StepApi(app)
    TaskApi(app)
    MetadataApi(app)
    ArtificatsApi(app)
    AuthApi(app)
    return app


def main():
    is_iam = os.environ.get("MF_METADATA_USE_IAM", "False") == "True"
    if not is_iam:
        loop = asyncio.get_event_loop()
        the_app = app(loop, DBConfiguration())
        handler = the_app.make_handler()
        port = os.environ.get("MF_METADATA_PORT", 8080)
        host = str(os.environ.get("MF_METADATA_HOST", "0.0.0.0"))
        f = loop.create_server(handler, host, port)

        srv = loop.run_until_complete(f)
        print("serving on", srv.sockets[0].getsockname())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
    else:
        loop = asyncio.get_event_loop()
        port = os.environ.get("MF_METADATA_PORT", 8080)
        host = str(os.environ.get("MF_METADATA_HOST", "0.0.0.0"))
        
        while True:
            logging.info("IAM LOOP STARTING")
            the_app = app(loop, DBConfiguration())
            handler = the_app.make_handler()
            f = loop.create_server(handler, host, port)

            srv = loop.run_until_complete(f)
            print("serving on", srv.sockets[0].getsockname())
            try:
                loop.run_forever()
                logging.info("IAM LOOPING")
                time.sleep(900)
                loop.stop() 
                logging.info("IAM LOOP STOPPED")
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
