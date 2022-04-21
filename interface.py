import os
# prevents kivy from spamming into our console (but also covers errors!)
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
import io
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage

class Watermark(App):
    Window.minimum_height = 600
    Window.minimum_width = 300
    Window.size = (400, 800)

    def build(self):
        return MainPage()

class MainPage(GridLayout):
    # looks like we can leave properties without def init and self.* at the beginning but they will work the same way
    loaded_image = ObjectProperty(None)
    result_image = ObjectProperty(None)
    wm_coordinates = ObjectProperty(None)

    def test(self, arg):
        print(arg)

    def img_coord_calc(self, global_coord, inscr_image_size, img_container_size, offset):
        """When we click on our image area, we get some raw_coord related to the whole app window.
        This method transforms those to the local coordinates of some point of current image.
        We assume that our window has default size and each image fits its square container automatically.
        Usage of round function results in 0.5px inaccuracy for our filler calc which is also assumed negligible"""
        # first, note that our image is superseded by one button (starting from the very bottom)
        int_cont_coord = [global_coord[_] - offset[_] for _ in range(2)]
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
        # we don't need anything except our image, that's why we should apply a condition first
        if inf_crop < int_cont_coord[0] < sup_crop or inf_crop < int_cont_coord[1] < sup_crop:
            self.wm_coordinates = [round(int_cont_coord[_] - filler_ds[_]) for _ in range(2)]
            # print(self.wm_coordinates)

    def img_click(self, inscr_image_size, img_container_size, offset):
        global_coords = Window.mouse_pos
        self.img_coord_calc(global_coords, inscr_image_size, img_container_size, offset)

        self.ids.text_wm.pos = global_coords

        self.ids.img_wm.pos = global_coords


    def main_img_load(self):
        self.show_load()
        self.ids.main_img.source = 'test.jpg'
        print(self.loaded_image)

    def img_wm(self):
        self.show_load()
        self.ids.img_wm.source = self.loaded_image
        # self.ids.img_wm.opacity = 0.5
        print(self.loaded_image)

    def text_wm(self, text, opacity):
        self.ids.text_wm.text = text
        self.ids.text_wm.color[3] = opacity/255

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load image (jpg or png)", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save image", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        # self.ids.main_img.source = 'result.jpg'
        # self.ids.text_wm.text = ''
        # self.ids.img_wm.opacity = 0

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0]), 'rb') as stream:
            self.loaded_image = stream.read()
        testim = CoreImage(self.loaded_image, ext='jpg')
        texttest = testim.texture
        self.dismiss_popup()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.result_image)
        self.dismiss_popup()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ImageBtn(ButtonBehavior, Image):
    """adds button on_press capability to an Image"""
    pass


if __name__ == '__main__':
    Watermark().run()

