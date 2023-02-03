import logging
from telegram import ForceReply, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application, CommandHandler, ContextTypes, filters, MessageHandler
import asyncio
import requests
from random import randint, randrange
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageSequence, ImageFont
import io
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_source_gif(query='money'):
    # Download gif source from giphy
    offset = randint(0, 50)
    giphy_api_response = requests.get(
        'https://api.giphy.com/v1/gifs/search?api_key=63PX5J59Sk9tTJ2FVaB0djksy4FwKp4p&limit=1&offset=' + str(
            offset) + '&q=' + query, headers={'Accept': 'application/json'})
    gif_url = giphy_api_response.json()['data'][0]['images']['downsized_large']['url']
    gif_file = BytesIO(requests.get(gif_url).content)  # Return it as pseudo-file
    return gif_file


def print_label(gif_file, text='sample text'):
    im = Image.open(gif_file)
    font = ImageFont.truetype('./fonts/unicode.impact.ttf', 62)

    # A list of the frames to be outputted
    frames = []

    for frame in ImageSequence.Iterator(im):
        # Draw the text on the frame
        frame = frame.convert('RGBA')
        d = ImageDraw.Draw(frame)
        d.text(
            (im.width * 0.5, im.height - 2),
            text,
            font=font,
            anchor='mb',
            stroke_width=2,
            stroke_fill="#000"
        )

        del d

        b = io.BytesIO()
        frame.save(b, format="GIF")
        frame = Image.open(b)

        # Then append the single frame image to a list of frames
        frames.append(frame)

    pseudo_file = BytesIO()
    frames[0].save(pseudo_file, format='gif', save_all=True, append_images=frames[1:])
    pseudo_file.seek(0)
    pseudo_file.name = 'output.gif'
    return pseudo_file


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        # reply_markup=ForceReply(selective=True),
    )


async def send_bobux(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        count_of_bobux = min(abs(int(context.args[0])) if len(context.args) else randint(0, 50), 999)
    except ValueError:
        count_of_bobux = randint(0, 50)

    text = 'money' if int(count_of_bobux) > 0 else 'no+money'

    logging.info(text)
    source = get_source_gif(query=text)
    printed = print_label(source, str(count_of_bobux) + ' bobux')
    await update.message.reply_document(document=printed)

if __name__ == '__main__':
    application = ApplicationBuilder().token('5600274140:AAGh6VaTSwkQK2mBHnFm33OW6avOxeurUJ0').build()
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bobux", send_bobux))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    # asyncio.run(send_gif(reciever_id, count_of_bobux))
