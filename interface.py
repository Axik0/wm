import os
# prevents kivy from spamming into our console (but also covers errors!)
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
import io
from main import process, img_filler_calc

# has to be prior to any other kivy framework import
from kivy import Config
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage


class Watermark(App):
    Window.size = (400, 800)

    def build(self):
        self.icon = 'icon_heart.png'
        return MainPage()


class MainPage(GridLayout):
    # looks like we can leave properties without def init and self.* at the beginning but they will work the same way
    result = ObjectProperty(None)
    loaded_image = ObjectProperty(None)
    main_image = ObjectProperty(None)
    wm_image = ObjectProperty(None)
    wm_text = StringProperty(None)
    wm_coordinates = ObjectProperty(None)
    # this is the only place where we set up extra wm preferences(the other values are dependent)
    wm_image_cfg = ObjectProperty([(40, 40), 128])
    wm_text_cfg = ObjectProperty(["arial.ttf", 40, 128])
    # comfortable watermark size multiplier
    fs_mult = 0.04

    def img_coord_calc(self, global_coord, inscr_image_size, img_container_size, offset):
        """When we click on our image area, we get some raw_coord related to the whole app window.
        This method transforms those to the local coordinates of some point of current image.
        We assume that our window has default size and each image fits its square container automatically.
        Usage of round function results in 0.5px inaccuracy for our filler calc which is also assumed negligible"""
        # first, note that our image is superseded by one button (starting from the very bottom)
        int_cont_coord = [global_coord[_] - offset[_] for _ in range(2)]
        filler_ds, inf_crop, sup_crop = img_filler_calc(inscr_image_size, img_container_size)
        # we don't need anything except our image, that's why we should apply a condition first
        if inf_crop < int_cont_coord[0] < sup_crop or inf_crop < int_cont_coord[1] < sup_crop:
            self.wm_coordinates = [[round(int_cont_coord[_] - filler_ds[_]) for _ in range(2)], inscr_image_size]

    def img_click(self, inscr_image_size, img_container_size, offset):
        global_coords = Window.mouse_pos
        self.img_coord_calc(global_coords, inscr_image_size, img_container_size, offset)
        # let's split text and image watermark cases basing on presence of any submitted text in a field
        if self.ids.text_wm.text is "":
            # let's get rid of any fillers in our GUI visualisation before placing a watermark image
            wmi = self.ids.img_wm
            filler = img_filler_calc(wmi.norm_image_size, wmi.size)[0]
            # subtract left/top filler before we place our image
            # kivy places image differently (over click - kivy vs under click - PIL), we convert to PIL way
            wmi.pos = (global_coords[0] - filler[0], global_coords[1] - filler[1] - wmi.size[1])
            # wmi's visible size is a (fixed) factor of main image container size
            # subtract any fillers if present, PIL processor doesn't use those
            self.wm_image_cfg[0] = [wmi.size_hint[_]-2*filler[_]/img_container_size[_] for _ in range(2)]
        else:
            # also convert y-coordinate to comply with an actual PIL placement way
            self.ids.text_wm.pos = (global_coords[0], global_coords[1] - self.ids.text_wm.size[1])

    def clear_watermarks(self):
        """removes (hides) any watermark (text/image) if it exists"""
        self.ids.img_wm.opacity = 0
        self.ids.text_wm.text = ""

    def text_wm(self, text, opacity):
        self.clear_watermarks()
        self.wm_text = self.ids.text_wm.text = text
        self.ids.text_wm.font_size = self.wm_text_cfg[1]*\
                    self.ids.main_img.size[1]/min(self.ids.main_img.texture_size[0], self.ids.main_img.texture_size[1])
        self.wm_text_cfg[2] = opacity
        self.ids.text_wm.color[3] = opacity/255

    def show_load(self, action_type):
        content = LoadDialog(a_type=action_type, load=self.load, cancel=self.dismiss_popup)
        if action_type:
            popup_text = "Load watermark image (png recommended)"
        else:
            popup_text = "Load main image (jpg or png)"
        self._popup = Popup(title=popup_text, content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        # proceed only if there are 2 images to process at least
        if self.main_image is not None and self.wm_coordinates is not None:
            content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
            self._popup = Popup(title="Save image", content=content, size_hint=(0.9, 0.9))
            self._popup.open()
            # self.ids.main_img.source = 'result.jpg'

    def dismiss_popup(self, action_type=None):
        self._popup.dismiss()
        if action_type is not None:
            self.clear_watermarks()
            if action_type:
                self.wm_image = self.loaded_image
                self.wm_text_cfg[1] = self.fs_mult * self.ids.img_wm.texture_size[0]
                self.ids.img_wm.texture = self.temp_image_tx
                self.ids.img_wm.opacity = self.wm_image_cfg[1] / 255
            else:
                self.main_image = self.loaded_image
                self.ids.main_img.texture = self.temp_image_tx

    def load(self, action_type, path, filename):
        with open(os.path.join(path, filename[0]), 'rb') as stream:
            self.loaded_image = io.BytesIO(stream.read())
        self.temp_image_tx = CoreImage(self.loaded_image, ext='png').texture
        self.dismiss_popup(action_type)

    def save(self, path, filename):
        self.result = process(self.main_image,
                                    self.wm_coordinates,
                                    self.wm_image,
                                    self.wm_image_cfg,
                                    self.wm_text,
                                    self.wm_text_cfg)
        with open(os.path.join(path, filename), 'wb') as stream:
            stream.write(self.result.getvalue())
        # !for some reason, coreimage here doesn't work without an extra layer of bytesio wrap!
        # self.ids.main_img.texture = CoreImage(io.BytesIO(self.result.getvalue()), ext='png').texture
        self.dismiss_popup()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    a_type = BooleanProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ImageBtn(ButtonBehavior, Image):
    """adds button on_press capability to an Image, note that ButtonBehavior has to be the very first one"""
    pass


if __name__ == '__main__':
    Watermark().run()
