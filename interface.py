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


    def img_click(self, image_size, img_container_size, offset):
        """we assume that our image fits square container by width or height"""
        global_coord = Window.mouse_pos
        print('click', img_container_size, Window.mouse_pos)
        img_proportion = image_size[0]/image_size[1]
        if img_proportion >= 1:
            filler_ds = (0, round(abs(img_container_size[0] * (1 - 1/img_proportion)))/2)
        else:
            filler_ds = (round(abs(img_container_size[0] * (1 - img_proportion)))/2, 0)
        print(filler_ds)
        int_cont_coord = [global_coord[_] - offset[_] for _ in range(2)]
        print(int_cont_coord)
        # intr_img_coord = [int_cont_coord[_] - filler_ds[_] for _ in range(2) if filler_ds]

    def text_wm(self, text, opacity):
        print(text)
        print(opacity)

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load image (jpg or png)", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save image", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0]), 'rb') as stream:
            self.loaded_image = stream.read()
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
