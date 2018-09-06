import tdl
from src.Presenter import Presenter
from src.sqlloader import SQLLoader


class View:
    def __init__(self):
        tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)
        loader = SQLLoader.get_instance()
        gui_settings = loader.load_gui_settings()
        self.root = tdl.init(gui_settings['screen_width'], gui_settings['screen_height'], title="Roguelike",
                             fullscreen=False)
        tdl.setFPS(gui_settings['fps_limit'])
        self.con = tdl.Console(gui_settings['screen_width'], gui_settings['screen_height'])
        self.panel = tdl.Console(gui_settings['screen_width'], gui_settings['panel_height'])
        self.fighting_panel = tdl.Console(gui_settings['screen_width'], gui_settings['screen_height'])
        self.presenter = Presenter(self.root, self.con, self.panel, self.fighting_panel)
        self.game_state = 'playing'

    def start(self):
        while not tdl.event.is_window_closed():
            self.presenter.render()
            tdl.flush()

            user_input = tdl.event.key_wait()
            player_action = self.handle_key_input(user_input)

            if player_action == 'exit':
                break

            self.game_state = self.presenter.handle_player_action(player_action)
            if self.game_state == 'dead' or self.game_state == 'won':
                break

    def handle_key_input(self, user_input):
        """
        if user_input.key == 'ENTER' and user_input.alt:
            # Alt+Enter: toggle fullscreen
            tdl.set_fullscreen(not tdl.get_fullscreen())
            return user_input.key
        """

        if user_input.key == 'ESCAPE':
            return 'exit'  # exit game

        if self.game_state == 'playing':
            # movement keys
            if user_input.key == 'UP':
                return user_input.key

            elif user_input.key == 'DOWN':
                return user_input.key

            elif user_input.key == 'LEFT':
                return user_input.key

            elif user_input.key == 'RIGHT':
                return user_input.key
            else:
                return 'didnt-take-turn'

        elif self.game_state == 'fighting':

            if user_input.key == 'LEFT':
                return user_input.key

            elif user_input.key == 'RIGHT':
                return user_input.key

            elif user_input.key == '1':
                return user_input.key

            elif user_input.key == '2':
                return user_input.key

            elif user_input.key == '3':
                return user_input.key

            elif user_input.key == '4':
                return user_input.key

            elif user_input.key == '5':
                return user_input.key

            elif user_input.key == '6':
                return user_input.key

            elif user_input.key == '7':
                return user_input.key

            elif user_input.key == '8':
                return user_input.key

            elif user_input.key == '9':
                return user_input.key

            elif user_input.key == '0':
                return user_input.key

            elif user_input.key == 'SPACE':
                return user_input.key

            else:
                return 'didnt-take-turn'
