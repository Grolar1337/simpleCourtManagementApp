from sanic import Sanic, Blueprint
from sanic.log import logger
from tortoise.contrib.sanic import register_tortoise
import random
import string

from user import user
from schedule import schedule
from models import *

app= Sanic("app")

app.static('/', './frontend/index.html')

app.config.ADMIN_CODE= ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))
logger.info('Here is your admin code: '+app.config.ADMIN_CODE)
#https://sanic.dev/en/guide/running/configuration.html#loading


api_group= Blueprint.group(
    user, schedule, url_prefix="/api")

app.blueprint(api_group)

register_tortoise(
    app, db_url="sqlite://database/database.sqlite3", modules={"models": ["models"]}, generate_schemas=True
)


if __name__ == "__main__":
    app.prepare(host='0.0.0.0', port=10000, access_log=True, dev=True)
    Sanic.serve()
