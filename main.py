"""Shorten URL application."""

import os
import secrets
from typing import Annotated

import motor.motor_asyncio
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
DEFAULT_URL = 'https://google.com'
DB_FILE = 'db.json'
URL_LEN = 5

db_client = motor.motor_asyncio.AsyncIOMotorClient(
    host=os.getenv('MONGO_HOST', 'localhost'),
    port=os.getenv('MONGO_PORT', 27017),
    username=os.getenv('MONGO_USERNAME', 'root'),
    password=os.getenv('MONGO_PASSWORD', 'example'),
)


@app.get('/')
async def root_page(request: Request):
    """Root shortener page."""
    return templates.TemplateResponse(request=request, name='index.html')


@app.post('/')
async def create_short_url(request: Request, url: Annotated[str, Form()]):
    """Create short link."""
    short_url = secrets.token_urlsafe(URL_LEN)
    new_doc = {'short_url': short_url, 'long_url': url}
    await db_client['url_shortener']['urls'].insert_one(new_doc)
    return templates.TemplateResponse(request=request, name='result.html',
                                      context={'short_url': f'{request.url}{short_url}'})


@app.get('/{short_url}')
async def use_short_url(short_url):
    """Redirect endpoint."""
    url_doc = await db_client['url_shortener']['urls'].find_one({'short_url': short_url})
    url = url_doc['long_url']
    url_doc['hits_counter'] = url_doc.get('hits_counter', 0) + 1
    await db_client['url_shortener']['urls'].replace_one({'_id': url_doc['_id']}, url_doc)
    return RedirectResponse(url)
