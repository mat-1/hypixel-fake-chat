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


def format_chat_message(author, content):
	# chat message
	text_formatted = author + '&f: ' + content
	return text_formatted

def format_dm_message(author, content):
	# chat message
	text_formatted = f'&dFrom &r{author}&r&7: &r&7{content}&r'
	return text_formatted

def format_friend_request(user):
	text_formatted = (
		'&9&m----------------------------------------------------&r&9\n'
		f'&r&eFriend request from &r{user}&r&9\n'
		'&r&a&l[ACCEPT]&r&8 - &r&c&l[DENY]&r&8 - &r&7&l[IGNORE]&r&9\n'
		'&r&9&m----------------------------------------------------&r'
	)
	return text_formatted

def format_party_request(user):
	text_formatted = (
		'&6-----------------------------------------------------\n'
		f'&r{user} &r&ehas invited you to join their party!\n'
		'&r&6Click here &r&eto join! You have 60 seconds to accept.&r&6\n'
		'&r&6-----------------------------------------------------&r'
	)
	return text_formatted

def format_party_message(user, content):
	text_formatted = f'&r&9Party > {user}&f: &r{content}&r'
	return text_formatted



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