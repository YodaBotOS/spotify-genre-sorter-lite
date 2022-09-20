import json
import aiohttp

async def json_or_text(response: aiohttp.ClientResponse):
    try:
        if response.headers['content-type'] == 'application/json':
            return await response.json()
    except KeyError:
        # Thanks Cloudflare
        pass

    text = await response.text(encoding='utf-8')

    try:
        js = json.loads(text)
    except Exception as e:
        #raise e
        return text
    else:
        return js
