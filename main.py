from PIL import Image, ImageFont, ImageDraw

base_image = Image.open("okacho.jpg").convert("RGBA")
# base_image.show()

# use image
# wm = Image.open("watermark.png").convert("RGBA")
# wm.show()
# or generate text
# blend images


# ch_opacity = 255
# ch_text = "Okacho"
ch_font = ImageFont.truetype("arial.ttf", 40)


# # measure dimensions of a box with our text with a font given
# ch_text_size = ch_font.getsize(ch_text)
# # print(ch_text_size)
# # first, create blank image, don't matter what's the fill but zero opacity
# txt = Image.new('RGBA', size=ch_text_size, color=(255, 255, 255, 0))
# # then we draw a single text line on top of that with nonzero opacity, left-top anchor alignment
# d = ImageDraw.Draw(txt)
# d.text((0, 0), text=ch_text, font=ch_font, anchor="lt", fill=(255, 255, 255, ch_opacity))
# ch_position = (base_image.size[0] - ch_text_size[0], 7 + base_image.size[1] - ch_text_size[1])
# # Both our images must have mode RGBA to use this particular method
# base_image.alpha_composite(txt, dest=ch_position)
# base_image.show()

# result = base_image.convert('RGB')
# result.save("name.jpg")

def process(main_image, coordinates, wm_image, wm_image_mult, wm_text=None, wm_text_cfg=None):
    base = Image.open(main_image).convert("RGBA")
    if wm_text is None:
        wm = Image.open(wm_image).convert("RGBA")
        wm = wm.resize((int(wm.width*wm_image_mult), int(wm.height*wm_image_mult)))
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
