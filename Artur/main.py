from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

Window.size = (450, 700)

class MenuScreen(Screen):
    def go_game(self, *args):
        self.manager.current = "game"
# Перехід до екрана налаштувань
    def go_settings(self, *args):
        self.manager.current = "settings"
# Вихід з програми
    def exit_app(self, *args):
        app.stop()

    
class GameScreen(Screen):
    
    # Повернення до меню
    def go_menu(self, *args):
        self.manager.current = "menu"
        
class SettingsScreen(Screen):
    def go_menu(self, *args):
        self.manager.current = "menu"

class MediumApp(App):
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

app = MediumApp()
app.run()



