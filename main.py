"""Shorten URL application."""

import json
import secrets
import aiofiles
from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
DEFAULT_URL = 'https://google.com'
DB_FILE = 'db.json'
URL_LEN = 6


@app.get('/')
async def root_page(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')


@app.post('/')
async def create_short_url(request: Request, url: Annotated[str, Form()]):
    short_url = secrets.token_urlsafe(URL_LEN)

    async with aiofiles.open(DB_FILE, 'r') as ldb_fh:
        content = await ldb_fh.read()

    db_dict = json.loads(content)
    db_dict[short_url] = url

    async with aiofiles.open(DB_FILE, 'w') as ldb_fh:
        await ldb_fh.write(json.dumps(db_dict, indent=4))
    return templates.TemplateResponse(request=request, name='result.html',
                                      context={'short_url': f'{request.url}{short_url}'})


@app.get('/{short_url}')
async def use_short_url(short_url):
    async with aiofiles.open(DB_FILE, 'r') as ldb_fh:
        content = await ldb_fh.read()
    db_dict = json.loads(content)
    return RedirectResponse(db_dict.get(short_url, DEFAULT_URL))
