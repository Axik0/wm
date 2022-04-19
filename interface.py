import os
# prevents kivy from spamming into our console (but also covers errors!)
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
import io
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window


class Watermark(App):
    # Window.minimum_height = 700
    # Window.minimum_width = 100
    Window.size = (400, 800)
    def build(self):
        return MainPage()


class MainPage(GridLayout):
    # looks like we can leave properties without def init and self.* at the beginning but they will work the same way
    loaded_image = ObjectProperty(None)
    result_image = ObjectProperty(None)

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


if __name__ == '__main__':
    Watermark().run()
