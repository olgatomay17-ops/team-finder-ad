import io
import os
import random
import uuid

from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 200
AVATAR_COLOR_MIN = 60
AVATAR_COLOR_MAX = 140
RGB_CHANNELS = 3
AVATAR_FONT_SIZE = 110
AVATAR_TEXT_COLOR = (255, 255, 255)

AVATAR_FONT_PATH = "fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"


def generate_avatar(name):
    color = tuple(random.randint(AVATAR_COLOR_MIN, AVATAR_COLOR_MAX) for _ in range(RGB_CHANNELS))

    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)
    letter = name[0].upper()

    font_path = finders.find(AVATAR_FONT_PATH)
    font = (
        ImageFont.truetype(font_path, AVATAR_FONT_SIZE)
        if font_path and os.path.exists(font_path)
        else ImageFont.load_default()
    )

    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) / 2 - bbox[1]

    draw.text(
        (x, y),
        letter,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return ContentFile(
        buffer.getvalue(),
        name=f"avatar_{uuid.uuid4()}.png",
    )
