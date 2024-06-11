from sanic import Sanic
from sanic.log import logger
from tortoise.contrib.sanic import register_tortoise
import random
import string

from models import *

app= Sanic("app")

app.static('/', './frontend/')

app.config.ADMIN_CODE= ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))
logger.info('Here is your admin code: '+app.config.ADMIN_CODE)
#https://sanic.dev/en/guide/running/configuration.html#loading


register_tortoise(
    app, db_url="sqlite://database/database.sqlite3", modules={"models": ["models"]}, generate_schemas=True
)


if __name__ == "__main__":
    app.prepare(host='0.0.0.0', port=10000, access_log=True, dev=True)
    Sanic.serve()
