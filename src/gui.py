"""This module defines GUI of Macao card game"""
import time

import pygame

import makao
import properties

# create screen
SCREEN = pygame.display.set_mode((properties.SCREEN_WIDTH, properties.SCREEN_HEIGHT))

CARD_BACK_IMG = pygame.image.load(f'{properties.CARDS_PATH}gray_back.png').convert_alpha()

INFO_IMG = pygame.image.load(properties.INFO_PATH).convert_alpha()
CLOSE_BUTTON = pygame.image.load(properties.CLOSE_BUTTON_PATH).convert_alpha()

# suits for ace restriction select
SUITS = []
for suit in makao.CardSuit:
    path = f'{properties.CARDS_PIP_PATH}{suit.value}.png'
    image = pygame.image.load(path).convert_alpha()
    rectangle = image.get_rect()
    SUITS.append((image, rectangle))

def text_objects(text, font, color):
    """Helper function for text."""
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def message_display(text, center, color=properties.BLACK_TEXT, size=20):
    """Writes text on screen."""
    font = pygame.font.SysFont(properties.FONT, size)
    text_surf, text_rect = text_objects(text, font, color)
    text_rect.center = center
    SCREEN.blit(text_surf, text_rect)

def button(msg, x, y, width, height, i_color, a_color, text_pos=None):
    """Draws button on screen."""
    if text_pos is None:
        text_pos = (x + width / 2, y + height / 2)

    mouse = pygame.mouse.get_pos()
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        rect = pygame.draw.rect(SCREEN, a_color, (x, y, width, height))
    else:
        rect = pygame.draw.rect(SCREEN, i_color, (x, y, width, height))

    message_display(msg, text_pos)
    return rect

def helper():
    """Draw help button"""
    help_rect = INFO_IMG.get_rect()
    help_rect.center = (properties.SCREEN_WIDTH - 50, 50)
    return SCREEN.blit(INFO_IMG, help_rect)

def display_help():
    """Display help screen after clicking help button"""
    SCREEN.fill(properties.FRAME_COLOR)

    close_rect = CLOSE_BUTTON.get_rect()
    close_rect.center = (properties.SCREEN_WIDTH - 50, 50)
    SCREEN.blit(CLOSE_BUTTON, close_rect)
    width = properties.SCREEN_WIDTH / 2
    height = 50
    height_dx = 25
    message_display('Game rules:', (width, height), properties.WHITE_TEXT)
    message_display('You can put any card of the same suit or value as the one on table.',
                    (width, height + height_dx), properties.WHITE_TEXT)
    message_display('You can select more than 1 card of the same value.',
                    (width, height + 2 * height_dx), properties.WHITE_TEXT)
    message_display('After selecting cards click on confirm button.',
                    (width, height + 3 * height_dx), properties.WHITE_TEXT)
    message_display('Restriction made by special cards are shown on screen when '
                    'special card is played.',
                    (width, height + 4 * height_dx), properties.WHITE_TEXT)
    message_display('If you don\'t have any card you can play card will be automatically drawn.',
                    (width, height + 5 * height_dx), properties.WHITE_TEXT)
    message_display('Special cards include:',
                    (width, height + 6 * height_dx), properties.WHITE_TEXT)
    message_display('Two\'s: Enemy has to draw 2 cards.',
                    (width, height + 7 * height_dx), properties.WHITE_TEXT)
    message_display('Three\'s: Enemy has to draw 3 cards.',
                    (width, height + 8 * height_dx), properties.WHITE_TEXT)
    message_display('Four\'s: Enemy waits turn.',
                    (width, height + 9 * height_dx), properties.WHITE_TEXT)
    message_display('Jack\'s: Can choose not special card.',
                    (width, height + 10 * height_dx), properties.WHITE_TEXT)
    message_display('King of Hearts and King of Spades: Enemy has to draw 5 cards.',
                    (width, height + 11 * height_dx), properties.WHITE_TEXT)
    message_display('Ace\'s: Can choose suit.',
                    (width, height + 12 * height_dx), properties.WHITE_TEXT)

    pygame.display.update()

    # close help
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if close_rect.collidepoint(pygame.mouse.get_pos()):
                return False

    return True

def show_cards(game):
    """Draws player's cards on bottom of screen."""
    x = properties.SCREEN_WIDTH / 2 - 35 * len(game.players[1].hand) / 2
    y = properties.SCREEN_HEIGHT / 10 * 8.5
    cards = []
    for card in game.players[1].hand:
        card_image = card.image
        rect = card_image.get_rect()
        rect.center = (x, y)
        cards.append(SCREEN.blit(card_image, rect))
        x += 35
    return cards

def show_enemy_cards(game):
    """Draws upside down cards on top of screen."""
    x = properties.SCREEN_WIDTH / 2 - 35 * len(game.players[0].hand) / 2
    y = properties.SCREEN_HEIGHT / 10 * 1.5
    for _ in range(len(game.players[0].hand)):
        rect = CARD_BACK_IMG.get_rect()
        rect.center = (x, y)
        SCREEN.blit(CARD_BACK_IMG, rect)
        x += 35

def show_table(game):
    """Draws cards on table up to 4 cards at a time."""
    x, y = properties.SCREEN_WIDTH / 2, properties.SCREEN_HEIGHT / 2
    for card in game.table[-4:]:
        card_image = card.image
        rect = card_image.get_rect()
        rect.center = (x, y)
        SCREEN.blit(card_image, rect)
        x += 30

def show_deck():
    """Draws deck on screen."""
    x, y = properties.SCREEN_WIDTH / 8, properties.SCREEN_HEIGHT / 2
    rect = CARD_BACK_IMG.get_rect()
    rect.center = (x, y)
    return SCREEN.blit(CARD_BACK_IMG, rect)

def enemy_turn(game):
    """Plays cards of bot player."""
    time.sleep(1)
    game.restriction.info()
    player = game.players[0]

    if player.stop > 0:
        player.stop -= 1
        game.restriction.turn()
        return

    game.restriction.turn()
    cards = game.bot_turn(player)
    if cards:
        for _ in cards:
            game.table.append(_)
            game.make_restriction(0)

def ace_restriction_select():
    """Draws pips buttons to choose suit when special card ace is played."""
    x, y = properties.SCREEN_WIDTH / 2, properties.SCREEN_HEIGHT / 2
    width, height = SUITS[0][1].width, SUITS[0][1].height
    SUITS[0][1].center = (x - width / 2, y - height / 2)
    SUITS[1][1].center = (x + width / 2, y - height / 2)
    SUITS[2][1].center = (x - width / 2, y + height / 2)
    SUITS[3][1].center = (x + width / 2, y + height / 2)

    for index, card_suit in enumerate(makao.CardSuit):
        button(None, SUITS[0][1].center[0] - width / 2, SUITS[0][1].center[1] - height / 1.45,
               2 * width, height / 5, properties.FRAME_COLOR, properties.FRAME_COLOR)

        button('Choose suit', SUITS[0][1].center[0] - width / 2 + 5,
               SUITS[0][1].center[1] - height / 1.45 + 5, 2 * width - 10,
               height / 5 - 5, properties.TABLE_CAPTION_COLOR, properties.TABLE_CAPTION_COLOR)

        button(None, SUITS[index][1].center[0] - width / 2, SUITS[index][1].center[1] - height / 2,
               width, height, properties.FRAME_COLOR, properties.FRAME_COLOR)

        button(None, SUITS[index][1].center[0] - width / 2 + 5,
               SUITS[index][1].center[1] - height / 2 + 5, width - 10, height - 10,
               properties.BUTTON_COLOR, properties.OVER_BUTTON_COLOR)

        SCREEN.blit(SUITS[index][0], SUITS[index][1])
        if SUITS[index][1].collidepoint(pygame.mouse.get_pos()):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return card_suit

        pygame.display.update()

def jack_restriction_select():
    """Draws number buttons to choose value when special card jack is played."""
    x, y = properties.SCREEN_WIDTH / 2, properties.SCREEN_HEIGHT / 2
    width, height = 120, 120

    button(None, x - width * 2, y - height * 1.5, width * 4, height / 2,
           properties.FRAME_COLOR, properties.FRAME_COLOR)
    button('Choose value', x - width * 2 + 5, y - height * 1.5 + 5, width * 4 - 8, height / 2 - 8,
           properties.TABLE_CAPTION_COLOR, properties.TABLE_CAPTION_COLOR)

    buttons = []

    ii = -2
    for num in range(5, 9):
        button(None, x + width * ii, y - height, width, height,
               properties.FRAME_COLOR, properties.FRAME_COLOR)
        buttons.append(button(str(num), x + width * ii + 5, y - height + 5, width - 8, height - 8,
                              properties.BUTTON_COLOR, properties.OVER_BUTTON_COLOR))
        ii += 1

    ii = -2
    for num in range(9, 13):
        if num == 11:
            num = 'Q'
        elif num == 12:
            num = 'Nothing'

        button(None, x + width * ii, y, width, height,
               properties.FRAME_COLOR, properties.FRAME_COLOR)
        buttons.append(button(str(num), x + width * ii + 5, y + 5, width - 8, height - 8,
                              properties.BUTTON_COLOR, properties.OVER_BUTTON_COLOR))
        ii += 1

    for index, value in enumerate(buttons):
        if value.collidepoint(pygame.mouse.get_pos()):
            if index != len(buttons) - 1:
                change_value = makao.NOT_SPECIAL_VALUES[index]
            else:
                # change to None
                change_value = 11
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return change_value

    pygame.display.update()

def my_turn(game, index):
    """Plays cards of human player."""
    player = game.players[1]
    cards = game.player_turn(player, index)
    if cards:
        for _ in cards:
            game.table.append(_)
            # jack - select requested value
            if _.value == makao.CardValue.JACK:
                select = False
                while not select:
                    for event in pygame.event.get():
                        pass
                    select = jack_restriction_select()
                if select == 11:
                    select = None
                game.make_restriction(1, select)

            # ace - select requested suit
            elif _.value == makao.CardValue.ACE:
                select = False
                while not select:
                    for event in pygame.event.get():
                        pass
                    ace_restriction_select()
                    select = ace_restriction_select()
                game.make_restriction(1, select)
            else:
                game.make_restriction(1)

def change_turn(game):
    """Changes turn."""
    for player in game.players:
        player.toggle_turn()
    draw_gui(game)

def popup(text):
    """Draws popup on screen."""
    rect_width = 400
    rect_height = 80

    x = properties.SCREEN_WIDTH / 2 - rect_width / 2
    y = (properties.SCREEN_HEIGHT * 2) / 3 - rect_height / 2
    center = (x + rect_width / 2, y + rect_height / 2)
    button(text, x, y, rect_width, rect_height,
           properties.TEXT_BACKGROUND_COLOR, properties.TEXT_BACKGROUND_COLOR,
           (center[0], center[1] - rect_height / 3))

    clicked = False
    width, height = 50, 50
    rect = button('OK', center[0] - width / 2, center[1] - height / 4,
                  width, height, properties.BUTTON_COLOR, properties.OVER_BUTTON_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if rect.collidepoint(pos):
                clicked = True

    pygame.display.update()
    return clicked

def show_restriction(game):
    """Draws rectangle showing restriction."""
    for player in game.players:
        if player.stop > 0:
            button(f'{player.name} waits {player.stop} turns', 0, 0, 200, 20,
                   properties.TEXT_BACKGROUND_COLOR, properties.TEXT_BACKGROUND_COLOR)

    if game.players[1].turn:
        if game.restriction.info():
            button(game.restriction.info(), 0, 0, 400, 25,
                   properties.TEXT_BACKGROUND_COLOR, properties.TEXT_BACKGROUND_COLOR)
            pygame.display.update()

def check_if_can_play(game):
    """Checks if player can play any cards."""
    player = game.players[1]
    if player.turn:
        if player.stop > 0:
            player.stop -= 1
            game.restriction.turn()
            change_turn(game)
            return

        playable = game.find_playable(player)
        if playable is None:
            closed_popup = False
            while not closed_popup:
                if game.restriction.active:
                    if game.restriction.function.__name__ == 'four_restriction':
                        closed_popup = popup(f'You can\'t put any card. You\'re waiting '
                                             f'{player.stop} turns')
                    else:
                        closed_popup = popup('You can\'t put any card. Drawing card...')
                else:
                    closed_popup = popup('You can\'t put any card. Drawing card...')

            draw_gui(game)
            pygame.display.update()
            game.restriction.turn()
            change_turn(game)

def draw_gui(game, cards=None):
    """Fills background and draws all elements."""
    SCREEN.fill(properties.BACKGROUND_COLOR)
    deck = show_deck()
    my_hand = show_cards(game)
    info = helper()
    show_enemy_cards(game)
    show_table(game)
    if game.players[0].turn:
        button('Bot\'s turn', properties.SCREEN_WIDTH - 100, 0, 100, 20,
               properties.TEXT_BACKGROUND_COLOR, properties.TEXT_BACKGROUND_COLOR)
    else:
        button('Your turn', properties.SCREEN_WIDTH - 100, 0, 100, 20,
               properties.TEXT_BACKGROUND_COLOR, properties.TEXT_BACKGROUND_COLOR)

    return deck, my_hand, info

def main():
    """This function plays the game."""
    pygame.init()
    pygame.display.set_caption("Macao")

    # list to hold indexes of cards
    cards_to_put_on_table = []
    clicked = False

    macao = makao.Game()
    running = True
    while running:

        draw, my_cards, info = draw_gui(macao)
        check_if_can_play(macao)
        show_restriction(macao)

        if not macao.win_condition(0) or not macao.win_condition(1):
            closed_popup = False
            while not closed_popup:
                closed_popup = popup('End Game!')
            running = False

        # enemy turn
        if macao.players[0].turn:
            enemy_turn(macao)
            change_turn(macao)

        # confirm button to put on table
        if cards_to_put_on_table:
            but = button('Confirm', properties.SCREEN_WIDTH / 2 - 40,
                         properties.SCREEN_HEIGHT / 3 * 2 - 25, 80, 50,
                         properties.BUTTON_COLOR, properties.OVER_BUTTON_COLOR)

            if but.collidepoint(pygame.mouse.get_pos()):
                clicked = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                # information
                if info.collidepoint(pos):
                    SCREEN.fill(properties.FRAME_COLOR)
                    help_on = True
                    while help_on:
                        help_on = display_help()
                        # help_on = False
                        pygame.display.update()

                if macao.players[1].turn:
                    #draw card
                    if draw.collidepoint(pos):
                        macao.draw_card(macao.players[1], 1)
                        cards_to_put_on_table.clear()
                        draw, my_cards, info = draw_gui(macao)
                        change_turn(macao)

                    # select card to play
                    for index, card in enumerate(my_cards):
                        card_pos = card
                        if card is not my_cards[-1]:
                            card_pos.width = 35

                        if card_pos.collidepoint(pos):
                            hand_length = len(macao.players[1].hand)
                            table_length = len(macao.table)

                            # can put more than 1 card
                            if index not in cards_to_put_on_table:
                                cards_to_put_on_table.append(index)

                draw, my_cards, info = draw_gui(macao)
                if clicked:
                    my_turn(macao, cards_to_put_on_table)
                    cards_to_put_on_table.clear()
                    clicked = False

                    # condition ensures user can click on cards
                    # that can't be played and nothing happens
                    if hand_length != len(macao.players[1].hand) and \
                            table_length != len(macao.table):
                                change_turn(macao)

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
