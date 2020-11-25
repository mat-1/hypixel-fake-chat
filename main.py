import username
import pillowtext
import asyncio
from aiohttp import web
import io

loop = asyncio.get_event_loop()

mode_cache = {}

def get_mode_unformatted(mode):
	if mode in mode_cache:
		return mode_cache[mode]
	with open(f'modes/{mode}.txt') as f:
		unformatted_text = f.read().strip()
		mode_cache[mode] = unformatted_text
	return unformatted_text

async def do_render(mode, ign, data=None, transparent=False):
	username_data = await username.get_username_data(ign)
	rank_formatted = username_data['rank_formatted']
	ign = username_data['username']
	print(rank_formatted, repr(rank_formatted))
	if rank_formatted != '&7':
		username_with_rank_formatted = rank_formatted + ' ' + ign
	else:
		username_with_rank_formatted = '&7' + ign
	
	formatted_text = get_mode_unformatted(mode)\
		.replace('{user}', username_with_rank_formatted)\
		.replace('{ign}', ign)\
		.replace('{data}', data)
	print(formatted_text)
	foreground = await loop.run_in_executor(
		None,
		pillowtext.create_image_from_formatted_text,
		formatted_text,
	)
	if not transparent:
		image = await loop.run_in_executor(None, pillowtext.add_background, foreground)
	else:
		image = foreground
	with io.BytesIO() as output:
		image.save(output, format='png')
		contents = output.getvalue()
	return contents


routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
	return web.Response(text='ok')

@routes.get('/render.png')
async def render_image(request):
	ign = request.query.get('u', '???')
	mode = request.query.get('m', 'chat')
	content = request.query.get('d', '???')\
		.replace('\\n', '\n')\
		.replace('\\\\', '\\')
	transparent = request.query.get('t', '0').lower() in {'1', 'true'}
	print(ign, mode, content)
	output_bytes = await do_render(mode, ign, content, transparent=transparent)
	return web.Response(
		body=output_bytes,
		content_type='image/png'
	)
 

app = web.Application()
app.add_routes(routes)
web.run_app(app)
