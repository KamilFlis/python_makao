import pygame
import makao
import properties
import time

# create screen
screen = pygame.display.set_mode((properties.SCREEN_WIDTH, properties.SCREEN_HEIGHT))

CARD_BACK_IMG = pygame.image.load(properties.CARDS_PATH + 'gray_back.png').convert_alpha()

# suits for ace restriction select
SUITS = []
for suit in makao.CardSuit:
    path = properties.CARDS_PIP_PATH + suit.value + '.png'
    image = pygame.image.load(path).convert_alpha()
    rect = image.get_rect()
    SUITS.append((image, rect))


#### - message/rectangles/buttons functions
def text_objects(text, font):
    text_surface = font.render(text, True, (0,0,0))
    return text_surface, text_surface.get_rect()

def message_display(text, center, size=20):
    font = pygame.font.SysFont(properties.FONT, size)
    text_surf, text_rect = text_objects(text, font)
    text_rect.center = center
    screen.blit(text_surf, text_rect)

def button(msg, x, y, w, h, ic, ac, text_pos=None):
    if text_pos is None:
        text_pos = (x + w / 2, y + h / 2)

    mouse = pygame.mouse.get_pos()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        rect = pygame.draw.rect(screen, ac,(x,y,w,h))
    else:
        rect = pygame.draw.rect(screen, ic,(x,y,w,h))

    message_display(msg, text_pos)
    return rect

####
def show_cards(game):
    x, y = properties.SCREEN_WIDTH / 2 - 35 * len(game.players[1].hand) / 2, properties.SCREEN_HEIGHT / 10 * 8.5
    cards = []
    for card in game.players[1].hand:
        image = card.image
        rect = image.get_rect()
        rect.center = (x, y)
        cards.append(screen.blit(image, rect))
        x += 35
    return cards

def show_enemy_cards(game):
    x, y = properties.SCREEN_WIDTH / 2 - 35 * len(game.players[0].hand) / 2, properties.SCREEN_HEIGHT / 10 * 1.5
    for _ in range(len(game.players[0].hand)):
        rect = CARD_BACK_IMG.get_rect()
        rect.center = (x, y)
        screen.blit(CARD_BACK_IMG, rect)
        x += 35

def show_table(game):
    x, y = properties.SCREEN_WIDTH / 2, properties.SCREEN_HEIGHT / 2
    for card in game.table[-4:]:
        image = card.image
        rect = image.get_rect()
        rect.center = (x, y)
        screen.blit(image, rect)
        x += 30

def show_deck():
    x, y = properties.SCREEN_WIDTH / 8, properties.SCREEN_HEIGHT / 2
    rect = CARD_BACK_IMG.get_rect()
    rect.center = (x, y)
    return screen.blit(CARD_BACK_IMG, rect)

def enemy_turn(game):
    time.sleep(1)
    game.restriction.info()
    player = game.players[0]

    if player.stop > 0:
        print("player #" + str(player.player_id) + " waits", player.stop, "turns")
        player.stop -= 1
        game.restriction.turn()
        return

    game.restriction.turn()
    cards = game.bot_turn(player)
    if cards:
        for _ in cards:
            game.table.append(_)
            game.make_restriction(0)

def ace_restriction_select(mouse):
    x, y = properties.SCREEN_WIDTH / 2, properties.SCREEN_HEIGHT / 2
    width, height = SUITS[0][1].width, SUITS[0][1].height
    SUITS[0][1].center = (x - width / 2, y - height / 2)
    SUITS[1][1].center = (x + width / 2, y - height / 2)
    SUITS[2][1].center = (x - width / 2, y + height / 2)
    SUITS[3][1].center = (x + width / 2, y + height / 2)

    for index, suit in enumerate(makao.CardSuit):
        black_rect = SUITS[index][1]
        white_rect = black_rect.inflate(-3, -3)

        screen.fill(properties.BLACK, black_rect)
        screen.fill(properties.GREY, white_rect)
        screen.blit(SUITS[index][0], SUITS[index][1])
        print('Drawing')

        # change colors while hovered
        if SUITS[index][1].collidepoint(mouse):
            screen.fill(properties.BLACK, black_rect)
            screen.fill(properties.DARK_GREY, white_rect)
            screen.blit(SUITS[index][0], SUITS[index][1])
            print('Hovering!')

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    print('Clicking!!')
                    print(suit)
                    return suit

    pygame.display.update()
    return True

def jack_restriction_select():
    pass

def my_turn(game, index):
    player = game.players[1]
    game.restriction.turn()
    cards = game.player_turn(player, index)
    if cards:
        for _ in cards:
            game.table.append(_)

            select = False
            while not select:
                print('tutaj')
                mouse = pygame.mouse.get_pos()
                ace_restriction_select(mouse)

            if _.value == makao.CardValue.ACE:
                select = False
                print('selected? ', select)
                while not select:
                    ace_restriction_select()
                    # select = ace_restriction_select()
                    print('seleeeeeect')
                    if select == makao.CardSuit.SPADES:
                        break

                game.make_restriction(1, select)
            else:
                game.make_restriction(1)

def change_turn(game):
    for player in game.players:
        player.toggle_turn()
    draw_gui(game)

def popup(text):
    rect_width = 350
    rect_height = 80

    x, y = properties.SCREEN_WIDTH / 2 - rect_width / 2, (properties.SCREEN_HEIGHT * 2) / 3 - rect_height / 2
    center = (x + rect_width / 2, y + rect_height / 2)
    button(text,
            x,
            y,
            rect_width,
            rect_height,
            properties.DARK_WHITE,
            properties.DARK_WHITE,
            (center[0], center[1] - rect_height / 3))

    clicked = False
    width, height = 50, 50
    rect = button('OK', center[0] - width / 2, center[1] - height / 4, width, height, properties.GREY, properties.DARK_GREY)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if rect.collidepoint(pos):
                clicked = True

    pygame.display.update()
    return clicked

def show_restriction(game):
    if game.players[1].turn:
        if game.restriction.info():
            button(game.restriction.info(), 0, 0, 400, 25, properties.DARK_WHITE, properties.DARK_WHITE)

def check_if_can_play(game):
    player = game.players[1]
    if player.turn:
        if player.stop > 0:
            print("player #" + str(player.player_id) + " waits", player.stop, "turns")
            player.stop -= 1
            game.restriction.turn()
            print('is active? 1', game.restriction.active)
            change_turn(game)
            return

        playable = game.find_playable(player)
        if playable is None:
            closed_popup = False
            print('is active? 2', game.restriction.active)
            while not closed_popup:
                closed_popup = popup('You can\'t put any card. Drawing card...')

            game.restriction.turn()
            change_turn(game)

def draw_gui(game):
    screen.fill(properties.BACKGROUND_COLOR)
    deck = show_deck()
    my_hand = show_cards(game)
    show_enemy_cards(game)
    show_table(game)


    return deck, my_hand

def main():
    pygame.init()

    pygame.display.set_caption("Makao")

    macao = makao.Game()
    running = True
    while running:
        draw, my_cards = draw_gui(macao)

        check_if_can_play(macao)
        show_restriction(macao)

        # enemy turn
        if macao.players[0].turn:
            enemy_turn(macao)
            change_turn(macao)

        if not macao.win_con(0) or not macao.win_con(1):
            # add popup to say who's won

            # closed_popup = False
            # while not closed_popup:
                # closed_popup = popup('Player ')
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if macao.players[1].turn:
                    # draw card
                    if draw.collidepoint(pos):
                        macao.draw_card(macao.players[1], 1)
                        draw, my_cards = draw_gui(macao)
                        change_turn(macao)

                    # select card to play
                    for index, card in enumerate(my_cards):
                        card_pos = card
                        if card is not my_cards[-1]:
                            card_pos.width = 35

                        if card_pos.collidepoint(pos):
                            hand_length = len(macao.players[1].hand)
                            table_length = len(macao.table)
                            my_turn(macao, index)
                            draw, my_cards = draw_gui(macao)

                            # condition ensures user can click on cards that can't be played and nothing happens
                            if hand_length != len(macao.players[1].hand) and table_length != len(macao.table):
                                change_turn(macao)



        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
