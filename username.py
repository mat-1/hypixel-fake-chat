import aiohttp

cached_datas = {}

s = aiohttp.ClientSession()

async def get_username_data(username):
	if username.lower() in cached_datas:
		return cached_datas[username.lower()]
	print('eeeee')
	r = await s.get(f'https://api.slothpixel.me/api/players/{username}')
	try:
		data = await r.json()
	except:
		data = {}
	if 'username' not in data:
		print('bruh', data)
		data = {
			'username': username,
			'rank_formatted': '&7'
		}
	else:
		data = {
			'username': data['username'],
			'rank_formatted': data['rank_formatted'],
		}
	print('pog', data)
	data['rank_formatted'] = data['rank_formatted'].replace('YOUTUBER', 'YOUTUBE') # bruh
	cached_datas[username.lower()] = data
	return data