from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.utils import platform


class MenuScreen(Screen):
    def go_game(self, *args):
        self.manager.current = "game"

        self.manager.transition.direction = "left"

    # Перехід до екрана налаштувань
    def go_settings(self, *args):
        self.manager.current = "settings"
        self.manager.transition.direction = "left"

    # Вихід з програми
    def exit_app(self, *args):
        app.stop()


class GameScreen(Screen):
    score = NumericProperty(0)

    def on_pre_enter(self, *args):
        self.score = 0
        app.LEVEL = 0
        self.ids.level_complete.opacity = 0
        self.ids.fish.fish_index = 0
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.start_game()
        return super().on_enter(*args)

    def start_game(self):
        self.ids.fish.new_fish()

    def level_complete(self, *args):
        self.ids.level_complete.opacity = 1

    # Повернення до меню
    def go_menu(self, *args):
        self.manager.current = "menu"


class SettingsScreen(Screen):
    def go_menu(self, *args):
        self.manager.current = "menu"
        self.manager.transition.direction = "left"


class RotatedImage(Image):
    ...  # Порожній клас, який просто додає властивість angle для обертання зображення


class Fish(RotatedImage):
    # Fish успадковує Image — тобто сам є зображенням.
    # Додає до Image логіку кліків і зміни риби.

    fish_current = None
    # Назва поточної риби (ключ зі словника FISHES), наприклад "fish1"

    fish_index = 0
    # Індекс поточної риби у списку рівня LEVELS[LEVEL].
    # 0 — перша риба, 1 — друга і т.д.

    hp_current = None
    # Поточна кількість HP риби. Зменшується при кожному кліку.
    anim_play = False
    interaction_block = True  # Блокування взаємодії під час анімації. True — взаємодія заблокована, False — дозволена.
    COEF_MULT = 1.5  # Коефіцієнт для збільшення розміру риби під час анімації плавання. 1.5 — збільшує на 50%.
    angle = NumericProperty(0)

    def on_kv_post(self, base_widget):
        # Вбудований метод Kivy.
        # Викликається після того, як kv-файл повністю побудував цей віджет
        # і всі його дочірні елементи готові.
        # Безпечне місце для збереження посилань на батьківські віджети.
        self.GAME_SCREEN = self.parent.parent.parent
        # self.parent — BoxLayout (безпосередній батько Fish у kv)
        # self.parent.parent — GameScreen (батько BoxLayout)
        # Зберігаємо посилання, щоб потім звертатися до self.GAME_SCREEN.score
        self.click_music = SoundLoader.load("assets/click.mp3")
        if self.click_music:
            self.click_music.volume = 1.0
        return super().on_kv_post(base_widget)

    def new_fish(self, *args):
        # Завантажує нову рибу: встановлює зображення і HP
        self.fish_current = app.LEVELS[app.LEVEL][self.fish_index]
        # app.LEVELS[app.LEVEL] — список риб поточного рівня, наприклад ['fish1', 'fish2']
        # [self.fish_index] — бере рибу за індексом, наприклад 'fish1'
        self.source = app.FISHES[self.fish_current]["source"]
        # Встановлює шлях до зображення риби
        self.hp_current = app.FISHES[self.fish_current]["hp"]
        # Встановлює кількість HP риби
        # self.opacity = 1
        # Робить рибу видимою (після defeated() вона була прихована)

        self.swim()  # Запускає анімацію плавання риби

    def swim(self):  # Анімація появи риби: зліва, з збільшенням розміру і поверненням до нормального
        self.pos = (self.GAME_SCREEN.x - self.width, self.GAME_SCREEN.height / 2)
        self.opacity = 1
        swim = Animation(x=self.GAME_SCREEN.width / 2 - self.width / 2, duration=1)
        swim.start(self)

        swim.bind(on_complete=lambda w, a: setattr(self, "interaction_block", False))

    def defeated(self):
        self.interaction_block = True
        # Анімація обертання
        anim = Animation(angle=self.angle + 360, d=1, t='in_cubic')

        # Запам'ятовуємо старі розмір і позицію для анімації зменьшення
        old_size = self.size.copy()
        old_pos = self.pos.copy()
        # Новий розмір
        new_size = (self.size[0] * self.COEF_MULT * 3, self.size[1] * self.COEF_MULT * 3)
        # Нова позиція риби при збільшенні
        new_pos = (self.pos[0] - (new_size[0] - self.size[0]) / 2, self.pos[1] - (new_size[0] - self.size[1]) / 2)
        # АНІМАЦІЯ ЗБІЛЬШЕННЯ/ЗМЕНЬШЕННЯ
        anim &= Animation(size=(new_size), t='in_out_bounce') + Animation(size=(old_size), duration=0)
        anim &= Animation(pos=(new_pos), t='in_out_bounce') + Animation(pos=(old_pos), duration=0)

        # anim = Animation(size=(self.size[0] * self.COEF_MULT * 2, self.size[1] * self.COEF_MULT * 2)) + Animation(size=old_size)
        anim &= Animation(opacity=0)  # + Animation(opacity = 1)
        anim.start(self)

    def on_touch_down(self, touch):
        # Вбудований метод Kivy. Викликається при будь-якому дотику/кліку на екран.
        # touch — об'єкт з координатами кліку

        if not self.collide_point(*touch.pos) or not self.opacity:
            return

        if not self.anim_play and not self.interaction_block:
            self.hp_current -= 1
            self.GAME_SCREEN.score += 1

            if self.click_music:
                self.click_music.play()

            # Клік призвів до зменшення hp риби
            if self.hp_current > 0:
                # Запам'ятовуємо старі розмір і позицію для анімації зменшення
                old_size = self.size.copy()
                old_pos = self.pos.copy()

                # Новий розмір
                new_size = (self.size[0] * self.COEF_MULT, self.size[1] * self.COEF_MULT)
                # Нова позиція риби при збільшенні
                new_pos = (self.pos[0] - (new_size[0] - self.size[0]) / 2,
                           self.pos[1] - (new_size[0] - self.size[1]) / 2)

                # АНІМАЦІЯ ЗБІЛЬШЕННЯ/ЗМЕНЬШЕННЯ
                zoom_anim = Animation(size=(new_size), duration=0.05) + Animation(size=(old_size), duration=0.05)
                zoom_anim &= Animation(pos=(new_pos), duration=0.05) + Animation(pos=(old_pos), duration=0.05)

                zoom_anim.start(self)
                self.anim_play = True

                zoom_anim.bind(on_complete=lambda *args: setattr(self, "anim_play", False))
                # Після завершення анімації зменшення розміру, встановлюємо anim_play в False, щоб дозволити наступну анімацію при наступному кліку.

            # Клік призвів до знищення риби
            else:
                self.defeated()

                # Запуск нової риби або анымації завершення рівня після 1 секунди програвання зникнення риби
                if len(app.LEVELS[app.LEVEL]) > self.fish_index + 1:
                    self.fish_index += 1
                    Clock.schedule_once(self.new_fish, 1.2)
                else:
                    Clock.schedule_once(self.GAME_SCREEN.level_complete, 1.2)
                    self.fish_index = 0  # додати для скидання індексу риби після завершення рівня, щоб при повторному вході в рівень починати з першої риби

        return super().on_touch_down(touch)


class ClickerApp(App):
    LEVEL = 0

    FISHES = {
        "fish1": {"source": "assets/images/photo_2_2026-04-03_14-41-45.png", "hp": 3},
        "fish2": {"source": "assets/images/photo_4_2026-04-03_14-41-45.png", "hp": 5},
        "fish3": {"source": "assets/images/photo_5_2026-04-03_14-41-45.png", "hp": 10}
    }
    LEVELS = [["fish1", "fish2", "fish3"]]

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if platform != 'android':
    Window.size = (450, 700)

app = ClickerApp()
app.run()
