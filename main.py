from PIL import Image, ImageFont, ImageDraw

ch_font = ImageFont.truetype("arial.ttf", 40)

# result = base_image.convert('RGB')
# result.save("name.jpg")

def process(main_image, coordinates, wm_image, wm_image_cfg, wm_text=None, wm_text_cfg=None):
    base = Image.open(main_image).convert("RGBA")
    if wm_text is None:
        wm = Image.open(wm_image).convert("RGBA")
        # we are going to synchronise wm image size with our visualisation via 2 factors in cfg[0]
        wm = wm.resize((int(base.width*wm_image_cfg[0][0]), int(base.height*wm_image_cfg[0][1])))
        # this method sets alpha layer of a whole watermark image as we need, before composition
        wm.putalpha(wm_image_cfg[1])
    else:
        # measure dimensions of a box with our text with a font given
        text_size = ch_font.getsize(wm_text)
        # print(ch_text_size)
        # first, create blank image, don't matter what's the fill but zero opacity
        wm = Image.new('RGBA', size=text_size, color=(255, 255, 255, 0))
        # then we draw a single text line on top of that with nonzero opacity, left-top anchor alignment
        d = ImageDraw.Draw(wm)
        d.text((0, 0), text=wm_text, font=ch_font, anchor="lt", fill=(255, 255, 255, int(wm_text_cfg)))
    position = (int(coordinates[0][0]/coordinates[1][0]*base.size[0]), base.size[1] - int(coordinates[0][1]/coordinates[1][1]*base.size[1]))
    base.alpha_composite(wm, dest=position)
    base.show()
