#import pygame
import random
import time
from enum import Enum
from enum import IntEnum
from collections import Counter

# # path to card images
# cards_path = '/home/kamil/Code/Python/Makao/cards_resized_renamed/'
#
# # screen resolution
# screen_width, screen_height = 1024, 768

# card values - name + value
class CardValue(IntEnum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

class CardSuit(Enum):
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'

# special cards set
specialCards = set()
specialCardValues = [CardValue.Two, CardValue.Three, CardValue.Four, CardValue.Jack, CardValue.Ace]
for card_suit in CardSuit:
     for card_val in specialCardValues:
         specialCards.add((card_val.value, card_suit.value))

specialCards.add((CardValue.King.value, CardSuit.SPADES.value))
specialCards.add((CardValue.King.value, CardSuit.HEARTS.value))

# card info
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return "{} of {}".format(self.value.name, self.suit.value)

    def is_special(self):
        return specialCards.__contains__((self.value.value, self.suit.value))

    # check if card can be put on table (same color or value)
    def is_playable(self, other):
        if self.suit is other.suit or self.value is other.value:
            return True
        return False


# deck info and methods
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for suit in CardSuit:
            for val in CardValue:
                self.cards.append(Card(suit, val))

    def shuffle(self):
        random.shuffle(self.cards)

    def show(self):
        for c in self.cards:
            print(c)
            #c.show()

    def draw(self):
        return self.cards.pop()

    def count(self):
        return len(self.cards)


#player info
class Player:
    def __init__(self, name, game, player_id):
        self.hand = []
        self.name = name
        self.game = game
        self.player_id = player_id
        self.stop = 0

    def show_hand(self):
        for i in range(len(self.hand)):
            print(i, ":", end=' ')
            print(self.hand[i])
        print(len(self.hand), ": Draw card")
        print((len(self.hand) + 1), ": EXIT!")

    def draw_card(self, quantity):
        print("Draws", quantity, "cards")
        for _ in range(quantity):
            if self.game.deck.count():
                self.hand.append(self.game.deck.draw())
            else:
                print("Empty deck, shuffling cards...")
                time.sleep(3)
                self.game.deck.cards = [card for card in self.game.table]
                self.game.table.clear()
                self.game.table.append(self.game.deck.cards.pop())
                self.game.deck.shuffle()
                self.hand.append(self.game.deck.draw())

    def put_on_table(self):
        self.game.restriction.info()
        # card_to_put_on_table = input("Select: ")
        # card_to_put_on_table = int(card_to_put_on_table)
        card_to_put_on_table = list(map(int, input("Select: ").split()))

        # option to draw card
        if card_to_put_on_table[0] is len(self.hand):
            self.draw_card(1)
            return None

        # exit - temporary
        elif card_to_put_on_table[0] is len(self.hand) + 1:
            print("Exit successful!")
            exit(0)

        for card_index in card_to_put_on_table:
            if self.hand[card_to_put_on_table[0]].value != self.hand[card_index].value:
                print("Can't put this card on table")
                self.draw_card(1)
                return None

        cards = [self.hand[index] for index in card_to_put_on_table]

        card = cards[0]
        # card = self.hand[card_to_put_on_table]
        restriction = self.game.restriction(card, self)
        if restriction == -1:
            return None
        elif (not card.is_playable(self.game.current()) or restriction == False) and restriction != 2:
            print("Can't put this card on table")
            self.draw_card(1)
            return None


        self.hand = [_ for _ in self.hand if _ not in cards]
        return cards

        # return self.hand.pop(card_to_put_on_table)


class Bot(Player):
    def put_on_table(self):
        layable = []
        for card in self.hand:
            restriction = self.game.restriction(card, self, True)
            if restriction and card.is_playable(self.game.current()) or restriction == 2:
                layable.append([card])

        if len(layable):
            for card in layable:
                for card_in_hand in self.hand:
                    if card_in_hand != card[0] and card_in_hand.value == card[0].value:
                        card.append(card_in_hand)

            card = random.choice(layable)
            self.hand = [_ for _ in self.hand if _ not in card]

            return card

        else:
            restriction = self.game.restriction(self.hand[0], self, False)
            if restriction == -1:
                return None
            self.draw_card(1)
            return None


class Restriction:
    active = False
    def create(self, function, turns, information):
        self.active = True
        self.function = function
        self.turns = turns
        self.information = information

    def disable(self):
        self.active = False

    def turn(self):
        if self.active:
            if self.turns == 0:
                self.disable()
            else:
                self.turns -= 1

    def info(self):
        if self.active:
            print(self.information)

    def __call__(self, card, player, mock=False):
        if self.active:
            return self.function(card, player, mock)
        else:
            return True


class Game:
    def __init__(self):
        print("Makao!")
        self.players = [Bot("Computer", self, 0), Player("Kamil", self, 1)]
        self.restriction = Restriction()
        self.card_pending = 0
        self.stops_pending = 0
        self.deck = Deck()
        self.table = []
        self.deal()

    def current(self):
        return self.table[-1]

    # gives player 5 cards and places 1 card on table
    def deal(self):
        '''
        Deals 5 cards to players
        '''
        self.deck.shuffle()
        # add 5 cards to player's hand
        for card in range(5):
            for player in self.players:
                player.hand.append(self.deck.draw())

        while not self.table:    # <-- condition to loop if first card was special
            # Checks if first card on table isn't special else shuffles deck
            if not self.deck.cards[-1].is_special():
                self.table.append(self.deck.draw())
            else:
                self.deck.shuffle()


    def turn(self, player_id):
        '''
        Puts card on table if player can do it; if not automatically draws card from deck
        '''
        # show top of table
        print("Cards in deck: " + str(self.deck.count()))
        print("Cards on table: " + str(len(self.table)))
        print("Table: ", end = '')
        print(self.current())
        player = self.players[player_id]

        if player.stop > 0:
            print("Player #" + str(player.player_id) + " waits", player.stop, "turns")
            player.stop -= 1
            return

        self.restriction.turn()

        if player_id is not 0:
            player.show_hand()

        print("Player #" + str(player_id) + " turn")
        print("Player #" + str(player_id) + " card count:", len(player.hand))
        time.sleep(1)
        cards = player.put_on_table()

        if cards is not None:
            for card in cards:
                print("Player #" + str(player_id) + " puts", card.value.name, "of", card.suit.name, "on table")
                self.table.append(card)
                self.make_restriction(player_id)


    def make_restriction(self, player_id):
        card = self.current()
        # jack
        if card.value is CardValue.Jack:
            if player_id is not 0:
                print("4 - Don't change")
                print("5 - Five")
                print("6 - Six")
                print("7 - Seven")
                print("8 - Eight")
                print("9 - Nine")
                print("10 - Ten")
                print("11 - Queen")
                value = input("Change value:")
                value = int(value)
                if value is 4:
                    value = None
                elif value is 5:
                    value = CardValue.Five
                elif value is 6:
                    value = CardValue.Six
                elif value is 7:
                    value = CardValue.Seven
                elif value is 8:
                    value = CardValue.Eight
                elif value is 9:
                    value = CardValue.Nine
                elif value is 10:
                    value = CardValue.Ten
                elif value is 11:
                    value = CardValue.Queen
                else:
                    exit(1)
            else:
                c = Counter(card.value for card in self.players[player_id].hand if not card.is_special())
                print(c)
                value = c.most_common(1)
                value = value[0][0]
                if not len(c):
                    value = None

            print("Player $", player_id, "chose", value)

            # only chosen value or jack
            def jack_restriction(changed, player, mock=False):
                if value is None:
                    # don't change
                    return changed.is_playable(self.current())
                if changed.value is value or changed.value is CardValue.Jack:
                    return 2
                else:
                    return False

            if value is None:
                value = 'whatever'
            self.restriction.create(jack_restriction, 2, "You can put only jack or " + str(value))
            return

        # ace
        if card.value is CardValue.Ace:
            if player_id is not 0:
                print("0 - Spades")
                print("1 - Hearts")
                print("2 - Clubs")
                print("3 - Diamonds")
                suit = input("Choose color: ")
                suit = int(suit)
                if suit is 0:
                    suit = CardSuit.SPADES
                elif suit is 1:
                    suit = CardSuit.HEARTS
                elif suit is 2:
                    suit = CardSuit.CLUBS
                elif suit is 3:
                    suit = CardSuit.DIAMONDS
                else:
                    exit(1)
            else:
                c = Counter(card.suit for card in self.players[player_id].hand)
                print(c)
                suit = c.most_common(1)
                suit = suit[0][0]
                print(suit)

            print("Player #", player_id, "chose", suit)

            def ace_restriction(changed, player, mock=False):
                if changed.suit is suit or changed.value is CardValue.Ace:
                    return 2
                else:
                    return False

            self.restriction.create(ace_restriction, 1, 'You can put only Ace or ' + str(suit))
            return

        # two
        if card.value is CardValue.Two:
            self.card_pending += 2
            print("outside two_restriction", type(card))
            # can put only two or three in the same color; else draws two cards
            def two_restriction(changed, player, mock=False):
                print("inside two_restriction", type(card))
                if card.suit is CardSuit.SPADES or card.suit is CardSuit.HEARTS:
                    if changed.value is CardValue.King and changed.suit is card.suit or (changed.value is CardValue.Two) or (changed.value is CardValue.Three and changed.suit is card.suit):
                        return True
                if (changed.value is CardValue.Two) or (changed.value is CardValue.Three and changed.suit is card.suit):
                    return True
                elif not mock:
                    print("CARDS to draw " + str(self.card_pending))
                    player.draw_card(self.card_pending)
                    self.card_pending = 0
                    return -1
                else:
                    return False
            self.restriction.create(two_restriction, 1, "You can put only 2 or 3 or special King")
            return

        # three
        if card.value is CardValue.Three:
            self.card_pending += 3
            print("outside three_restriction", type(card))
            # can put only three or two in the same color; else draws three cards
            def three_restriction(changed, player, mock=False):
                print("inside three_restriction", type(card))
                if card.suit is CardSuit.SPADES or card.suit is CardSuit.HEARTS:
                    if changed.value is CardValue.King and changed.suit is card.suit:
                        return True
                if (changed.value is CardValue.Three) or (changed.value is CardValue.Two and changed.suit is card.suit):
                    return True
                elif not mock:
                    print("CARDS to draw " + str(self.card_pending))
                    player.draw_card(self.card_pending)
                    self.card_pending = 0
                    return -1
                else:
                    return False
            self.restriction.create(three_restriction, 1, "You can put only 2 or 3 or special King")
            return

        # king
        if card.value is CardValue.King and (card.suit is CardSuit.SPADES or card.suit is CardSuit.HEARTS):
            self.card_pending += 5
            print("outside king_restriction", type(card))
            def king_restriction(changed, player, mock=False):
                print("Inside king_restriction", type(card))
                if card.suit is CardSuit.HEARTS:
                    if (changed.value is CardValue.King and changed.suit is CardSuit.SPADES) or ((changed.value is CardValue.Two or changed.value is CardValue.Three) and changed.suit is CardSuit.HEARTS):
                        return True
                    elif not mock:
                            print("CARDS to draw " + str(self.card_pending))
                            player.draw_card(self.card_pending)
                            self.card_pending = 0
                            return -1
                    else:
                        return False
                else:
                    if (changed.value is CardValue.King and changed.suit is CardSuit.HEARTS) or ((changed.value is CardValue.Two or changed.value is CardValue.Three) and changed.suit is CardSuit.SPADES):
                        return True
                    elif not mock:
                        print("CARDS to draw " + str(self.card_pending))
                        player.draw_card(self.card_pending)
                        self.card_pending = 0
                        return -1
                    else:
                        return False
            self.restriction.create(king_restriction, 1, "You can put only 2 or 3 or special King")
            return

        #four
        if card.value is CardValue.Four:
            self.stops_pending += 1
            def four_restriction(changed, player, mock=False):
                if changed.value is CardValue.Four:
                    return True
                elif not mock:
                    player.stop += self.stops_pending
                    self.stops_pending = 0
                    return -1
                else:
                    return False

            self.restriction.create(four_restriction, 1, "You can put only 4")
            # print("Player #1 waits", self.stops_pending, "turns") if player_id is 0 else print("Player #0 waits", self.stops_pending, "turns")
            return

    # win condition - empty hand means player won
    def win_con(self, player_id):
        if not self.players[player_id].hand:
            print("Player $" + str(player_id) + "won")
            exit(0)  # change game loop condition


if __name__ == "__main__":
    makao = Game()
    while not makao.win_con(0) or not makao.win_con(1):
        makao.turn(0)
        makao.turn(1)

#     # pygame initialization
#     pygame.init()
#
#     # create screen
#     screen = pygame.display.set_mode((screen_width, screen_height))
#
#     # title
#     pygame.display.set_caption("Makao")
#
#     makao = Game()
# #    screen.fill((3, 122, 48))
# #    makao.players[0].show_hand()
# #    makao.deck.show()
# #    makao.players[0].show_hand()
#
#   #  pygame.display.update()
#
#     running = True
#     while running:
#         # RGB color
#         # greenish background
#    #     screen.fill((3, 122, 48))
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 i = 1
#                 x -= 15
#                 makao.draw_card()
#
#
#         makao.players[0].show_hand()
#         pygame.display.update()
#
#     pygame.quit()

