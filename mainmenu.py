import pygame
import pygame_menu
from pygame_menu import themes
from game import level_cycle, terminate
from constants import WIDTH, HEIGHT, SIZE


level_to_load = 0


def main_menu():
    global level_to_load
    pygame.init()
    surface = pygame.display.set_mode(SIZE)

    def start_the_game():
        menu._open(loading)
        pygame.time.set_timer(update_loading, 50)

    def level_menu():
        menu._open(level)

    def set_difficulty(value, difficulty):
        global level_to_load
        print(difficulty)
        level_to_load = difficulty

    menu = pygame_menu.Menu('Welcome', WIDTH, HEIGHT, theme=themes.THEME_SOLARIZED)
    menu.add.text_input('Name: ')
    menu.add.button('Levels', level_menu)
    menu.add.button('Play', start_the_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    level = pygame_menu.Menu('Select a Difficulty', WIDTH, HEIGHT, theme=themes.THEME_BLUE)
    level.add.selector('Level :', [('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6)],
                       onchange=set_difficulty)

    loading = pygame_menu.Menu('Loading the Game...', WIDTH, HEIGHT, theme=themes.THEME_SOLARIZED)
    loading.add.progress_bar("Progress", progressbar_id="1", width=300)

    arrow = pygame_menu.widgets.RightArrowSelection()

    update_loading = pygame.USEREVENT + 0

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == update_loading:
                progress = loading.get_widget("1")
                progress.set_value(progress.get_value() + 1)
                if progress.get_value() == 100:
                    pygame.time.set_timer(update_loading, 0)
                    level_cycle(level_to_load)
            if event.type == pygame.QUIT:
                terminate()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(surface)
            if menu.get_current().get_selected_widget():
                arrow.draw(surface, menu.get_current().get_selected_widget())

        pygame.display.update()
