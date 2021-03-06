from PIL import Image, ImageFont, ImageDraw
import io

def img_filler_calc(inscr_image_size, img_container_size):
    """this aux function serves as filler calculator as we want to use it twice"""
    # we assume that our image fits square container by width or height
    if inscr_image_size[0] >= inscr_image_size[1]:
        # horizontal fit case, we have two equal top and bottom filler stripes surrounding our image
        filler_ds = (0, (img_container_size[1]-inscr_image_size[1])/2)
        inf_crop = filler_ds[1]
        sup_crop = img_container_size[1] - filler_ds[1]
    else:
        # vertical fit case, left and right filler stripes
        filler_ds = ((img_container_size[0]-inscr_image_size[0])/2, 0)
        inf_crop = filler_ds[0]
        sup_crop = img_container_size[0] - filler_ds[0]
    return filler_ds, inf_crop, sup_crop


def process(main_image, coordinates, wm_image, wm_image_cfg, wm_text=None, wm_text_cfg=None):
    """Main image processor. Takes two images or creates one for text watermark itself.
    Result is enclosed into buffer (bytesIO object) for transfer purpose, not yet saved to file"""
    base = Image.open(main_image).convert("RGBA")
    if wm_text is None:
        wm = Image.open(wm_image).convert("RGBA")
        # we are going to synchronise wm image size with our visualisation via 2 factors in cfg[0]
        wm = wm.resize((int(base.width*wm_image_cfg[0][0]), int(base.height*wm_image_cfg[0][1])))
        # for jpg this method sets an alpha layer of a whole watermark image, unused because breaks png_pics
        # wm.putalpha(wm_image_cfg[1])
    else:
        ch_font = ImageFont.truetype(wm_text_cfg[0], wm_text_cfg[1])
        # measure dimensions of a box with our text with a font given
        text_size = ch_font.getsize(wm_text)
        # first, create blank image, don't matter what's the fill but zero opacity
        wm = Image.new('RGBA', size=text_size, color=(255, 255, 255, 0))
        # then we draw a single text line on top of that with nonzero opacity, left-top anchor alignment
        d = ImageDraw.Draw(wm)
        d.text((0, 0), text=wm_text, font=ch_font, anchor="lt", fill=(255, 255, 255, int(wm_text_cfg[2])))
    position = (int(coordinates[0][0]/coordinates[1][0]*base.size[0]), base.size[1] - int(coordinates[0][1]/coordinates[1][1]*base.size[1]))
    base.alpha_composite(wm, dest=position)
    res = io.BytesIO()
    base.convert('RGB').save(res, format='JPEG')
    return res
