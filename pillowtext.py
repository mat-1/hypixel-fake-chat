from PIL import Image, ImageFont, ImageDraw
import os
import re
import random

text_size = 16

font = ImageFont.truetype('fonts/Minecraft.otf', text_size)


color_codes = {
	'0': (0, 0, 0),
	'1': (0, 0, 170),
	'2': (0, 170, 0),
	'3': (0, 170, 170),
	'4': (170, 0, 0), # red
	'5': (170, 0, 170),
	'6': (255, 170, 0), # gold
	'7': (170, 170, 170),
	'8': (85, 85, 85),
	'9': (85, 85, 254),
	'a': (85, 254, 85),
	'b': (85, 254, 254),
	'c': (254, 85, 85),
	'd': (254, 85, 254),
	'e': (255, 255, 85),
	'f': (255, 255, 255)
}	

def create_image_from_formatted_text(formatted_text):
	im = Image.new(
		'RGBA',
		(1, 1),
		(0,0,0,0)
	)

	draw = ImageDraw.Draw(im)

	def get_text_width(string):
		return draw.textsize(string, font)[0]

	unformatted_text = re.sub(r'&.', '', formatted_text)

	width, height = draw.textsize(unformatted_text, font)
	im = im.resize((width + (text_size // 8) + 2, height + (text_size // 8)))

	draw = ImageDraw.Draw(im)

	current_x = 0
	current_y = 0
	next_character_is_formatter = False
	current_color = (255,255,255)
	is_bold = False


	for character in formatted_text:
		if character == '&':
			next_character_is_formatter = True
		elif next_character_is_formatter:
			if character in color_codes:
				current_color = color_codes[character]
			elif character == 'r':
				current_color = (255,255,255)
				is_bold = False
			elif character == 'l':
				is_bold = True
			next_character_is_formatter = False
		elif character == '\n':
			current_x = 0
			current_y += text_size + (text_size // 4)
		else:
			character_offset_y = 0

			if character in '+-':
				# the font is weird /shrug
				character_offset_y = -2

			dark_color = (
				int(current_color[0] * .25),
				int(current_color[1] * .25),
				int(current_color[2] * .25)
			)
			shadow_x = current_x + (text_size // 8)
			shadow_y = current_y + (text_size // 8) + character_offset_y
			draw.text(
				(shadow_x, shadow_y),
				character,
				font=font,
				fill=dark_color,
			)
			if is_bold:
				draw.text(
					(shadow_x + 2, shadow_y),
					character,
					font=font,
					fill=dark_color,
				)

			draw.text(
				(current_x, current_y + character_offset_y),
				character,
				font=font,
				fill=current_color
			)
			if is_bold:
				draw.text(
					(current_x + 2, current_y + character_offset_y),
					character,
					font=font,
					fill=current_color
				)


			character_width = get_text_width(character)
			if is_bold:
				character_width += 2
			current_x += character_width
	return im

def add_background(foreground, filename=None):
	if not filename:
		filename = random.choice(os.listdir('backgrounds'))
	background = Image.open('backgrounds/' + filename)
	background = background.convert('RGBA')

	new_foreground = Image.new('RGBA', (foreground.width, background.height), (0,0,0,0))
	text_x = 4
	text_y = (background.height - foreground.height)
	new_foreground.paste(
		foreground,
		(
			text_x,
			text_y
		)
	)

	background.alpha_composite(new_foreground)

	output = background.crop((
		0,
		background.height - foreground.height,
		foreground.width + 4,
		background.height # (background.height - foreground.height)
	))

	return output