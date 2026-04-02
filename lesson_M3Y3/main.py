from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

#
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import NumericProperty
# from kivy.lang import Builder
# from kivy.utils import hex_colormap, colormap
# from kivy.metrics import sp, dp
# from kivy import platform

Window.size = (450, 600)
# Встановлює розмір вікна: ширина 450px, висота 600px
# Актуально тільки для ПК, на мобільних пристроях ігнорується


class MenuScreen(Screen):
    # Клас екрана головного меню, успадковує Screen
    # Kivy автоматично знайде правило <MenuScreen> у medium.kv

    def go_game(self):
        self.manager.current = "game"
        # self.manager — це ScreenManager, до якого належить цей екран
        # .current = "game" — перемикає на екран з name="game"
        self.manager.transition.direction = "left"
        # Анімація переходу: екран "виїжджає" вліво

    def go_settings(self):
        self.manager.current = "settings"
        self.manager.transition.direction = "up"
        # Анімація переходу: екран "виїжджає" вгору

    def exit_app(self):
        App.get_running_app().stop()
        # get_running_app() — повертає поточний запущений екземпляр App
        # .stop() — завершує програму


class GameScreen(Screen):
    score = NumericProperty(0)
    # Лічильник очок. NumericProperty — не звичайна змінна Python.
    # Коли score змінюється в Python, Label з text: str(root.score)
    # у kv-файлі оновлюється автоматично без додаткового коду

    def on_pre_enter(self, *args):
        # Вбудований метод Screen.
        # Викликається ПЕРЕД тим, як екран стає видимим (під час анімації переходу).
        # Використовується для скидання стану перед показом екрана.
        self.score = 0
        # Скидає рахунок на 0 при кожному вході в екран гри
        app.LEVEL = 0
        # Скидає поточний рівень на початковий
        self.ids.level_complete.opacity = 0
        # self.ids — словник всіх віджетів з id у kv-файлі для цього екрана
        # level_complete — id Label з текстом "Level Complete!"
        # opacity: 0 — робить його невидимим
        self.ids.fish.fish_index = 0
        # fish — id віджета Fish
        # fish_index = 0 — скидає індекс поточної риби на першу
        return super().on_pre_enter(*args)
        # Викликає оригінальний метод батьківського класу Screen.
        # Завжди потрібно викликати super() у on_pre_enter / on_enter,
        # щоб не зламати внутрішню логіку ScreenManager

    def on_enter(self, *args):
        # Вбудований метод Screen.
        # Викликається ПІСЛЯ того, як екран повністю відобразився.
        self.start_game()
        return super().on_enter(*args)

    def start_game(self):
        self.ids.fish.new_fish()
        # Викликає метод new_fish() у віджеті Fish —
        # завантажує першу рибу і починає гру

    def level_complete(self, *args):
        self.ids.level_complete.opacity = 1
        # Робить Label "Level Complete!" видимим.
        # *args потрібен тому, що цей метод викликається через Clock.schedule_once,
        # який завжди передає аргумент dt (delta time — час з попереднього кадру)

    def go_menu(self):
        self.manager.current = "menu"
        self.manager.transition.direction = "right"


class SettingsScreen(Screen):
    def go_menu(self):
        self.manager.current = "menu"
        self.manager.transition.direction = "down"


class Fish(Image):
    # Fish успадковує Image — тобто сам є зображенням.
    # Додає до Image логіку кліків і зміни риби.

    fish_current = None
    # Назва поточної риби (ключ зі словника FISHES), наприклад "fish1"

    fish_index = 0
    # Індекс поточної риби у списку рівня LEVELS[LEVEL].
    # 0 — перша риба, 1 — друга і т.д.

    hp_current = None
    # Поточна кількість HP риби. Зменшується при кожному кліку.

    def on_kv_post(self, base_widget):
        # Вбудований метод Kivy.
        # Викликається після того, як kv-файл повністю побудував цей віджет
        # і всі його дочірні елементи готові.
        # Безпечне місце для збереження посилань на батьківські віджети.
        self.GAME_SCREEN = self.parent.parent
        # self.parent — BoxLayout (безпосередній батько Fish у kv)
        # self.parent.parent — GameScreen (батько BoxLayout)
        # Зберігаємо посилання, щоб потім звертатися до self.GAME_SCREEN.score
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
        self.opacity = 1
        # Робить рибу видимою (після defeated() вона була прихована)

    def defeated(self):
        self.opacity = 0
        # Ховає рибу після того, як її HP впало до 0

    def on_touch_down(self, touch):
        # Вбудований метод Kivy. Викликається при будь-якому дотику/кліку на екран.
        # touch — об'єкт з координатами кліку

        if not self.collide_point(*touch.pos) or not self.opacity:
            return
        # self.collide_point(*touch.pos) — перевіряє, чи потрапив клік
        # у межі прямокутника віджета Fish.
        # *touch.pos розпаковує (x, y) з об'єкта touch.
        # Якщо клік поза рибою АБО риба невидима — ігноруємо клік.

        self.hp_current -= 1
        # Зменшує HP риби на 1
        self.GAME_SCREEN.score += 1
        # Збільшує рахунок гравця на 1

        if self.hp_current <= 0:
            self.defeated()
            if len(app.LEVELS[app.LEVEL]) > self.fish_index + 1:
                # Якщо у рівні є ще риби після поточної —
                # переходимо до наступної через 1.2 секунди
                self.fish_index += 1
                Clock.schedule_once(self.new_fish, 1.2)
                # Clock.schedule_once(функція, затримка_в_секундах) —
                # викликає функцію один раз через вказаний час
            else:
                # Риб більше немає — рівень завершено
                Clock.schedule_once(self.GAME_SCREEN.level_complete, 1.2)
                self.fish_index = 0
                # Скидає індекс для можливого рестарту

        return super().on_touch_down(touch)
        # Передає подію далі по дереву віджетів


class MediumApp(App):
    LEVEL = 0
    # Поточний рівень гри. Індекс у списку LEVELS.

    FISHES = {
        "fish1": {"source": "assets/images/fish_01.png", "hp": 10},
        "fish2": {"source": "assets/images/fish_02.png", "hp": 20},
    }
    # Словник з даними всіх риб.
    # Ключ — назва риби, значення — словник з шляхом до зображення і кількістю HP.

    LEVELS = [["fish1", "fish2"]]
    # Список рівнів. Кожен рівень — список риб у порядку появи.
    # Зараз один рівень: спочатку fish1, потім fish2.

    def build(self):
        # Вбудований метод App. Викликається один раз при запуску програми.
        # Повертає кореневий віджет — те, що відображається у вікні.
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(SettingsScreen(name="settings"))
        # name= — рядковий ідентифікатор екрана.
        # Саме це значення використовується у self.manager.current = "game"
        return sm


app = MediumApp()
# Створює екземпляр застосунку. Змінна app використовується у коді
# для доступу до FISHES, LEVELS, LEVEL через app.FISHES тощо.

app.run()
# Запускає головний цикл Kivy — відкриває вікно і починає обробку подій.
