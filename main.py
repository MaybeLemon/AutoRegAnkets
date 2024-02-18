from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
import threading
from logic_file import AutoAnkets


class MyApp(App):
    def build(self):
        self.autoankets_obj = None
        self.login_input = TextInput(hint_text='Логин', multiline=False,
                                     write_tab=False)
        self.password_input = TextInput(hint_text='Пароль', password=True,
                                        multiline=False, write_tab=False)
        self.login_button = Button(text='Войти', on_press=self.login)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        input_container = BoxLayout(orientation='vertical', spacing=10)
        input_container.add_widget(self.login_input)
        input_container.add_widget(self.password_input)

        layout.add_widget(
            Label(text='Авторизация', font_size='24sp', halign='center'))
        layout.add_widget(input_container)
        layout.add_widget(self.login_button)

        layout.size_hint = (0.95, 0.95)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        return layout

    def on_start(self):
        self.root.bind(on_key_down=self.on_key_down)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40 and self.login_input.focus:
            self.login(self.login_button)
            return True

    def login(self, instance):
        login = self.login_input.text
        password = self.password_input.text
        if not login or not password:
            self.show_popup('Ошибка', 'Пожалуйста, введите логин и пароль')
            return
        self.autoankets_obj = AutoAnkets()
        threading.Thread(target=self.authorize_and_display_ankets, args=(login, password)).start()

    def authorize_and_display_ankets(self, login, password):
        self.autoankets_obj.authorize(login, password)
        Clock.schedule_once(self.display_ankets, 2)

    def display_ankets(self, dt):
        if not self.autoankets_obj:
            return
        self.autoankets_obj.ankets_view()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        for id_number, text in self.autoankets_obj.db_ankets.items():
            btn = Button(text=text, font_size='20sp')
            btn.size_hint = (1, None)
            btn.bind(on_press=lambda instance, id_number=id_number: self.get_anket_and_post_data(id_number))
            layout.add_widget(btn)
        self.root_window.remove_widget(self.root_window.children[0])
        self.root_window.add_widget(layout)

    def get_anket_and_post_data(self, id_number):
        threading.Thread(target=self.get_and_post, args=(id_number,)).start()

    def get_and_post(self, id_number):
        if not self.autoankets_obj:
            return
        self.autoankets_obj.get_anket_from_user(id_number)
        response = self.autoankets_obj.post_data()
        if response.text == '1':
            self.show_popup('Успешно', 'Данные отправлены')
        else:
            self.show_popup('Ошибка', 'Данные не отправлены')

    def show_popup(self, title, text):
        def create_popup(dt):
            popup = Popup(title=title, content=Label(text=text), size_hint=(None, None), size=(400, 200))
            popup.open()

        Clock.schedule_once(create_popup)


if __name__ == '__main__':
    MyApp().run()
