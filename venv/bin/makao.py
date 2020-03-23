#import pygame
import random
from enum import Enum
from enum import IntEnum

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

    def show(self):
        print("{} of {}".format(self.value.name, self.suit.value))

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
            c.show()

    def draw(self):
        return self.cards.pop()

    def count(self):
        return len(self.cards)


#player info
class Player:
    def __init__(self, name, id):
        self.hand = []
        self.name = name
        self.id = id

    def show_hand(self):
        for card in self.hand:
            card.show()


class Game:
    def __init__(self):
        print("Makao!")
        self.players = [Player("Kamil", 0), Player("Computer", 1)]
        self.deck = Deck()
        self.table = []
        self.deal()

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

        while not self.table:    # <------- condition to loop if first card was special
            # Checks if first card on table isn't special else shuffles deck
            if not self.deck.cards[-1].is_special():
                self.table.append(self.deck.draw())
            else:
                self.deck.shuffle()


    def put_on_table(self):
        '''
        Puts card on table if player can do it; if not automatically draws card from deck
        '''
        # show top of table
        print("Table: ", end = '')
        self.table[-1].show()

        ########### - in progress
        if self.table[-1].is_special():
            print("SPECIAL!!!!!!")
            self.check_restrictions()
        ###########

        # show cards in hand to select
        for i in range(len(self.players[0].hand)):
            print(i, ":", end = ' ')
            self.players[0].hand[i].show()
        print(len(self.players[0].hand), ": Draw card")

        how_many_cards_can_you_play = 0
        # checks if you can put any card on table - if not automatically draws card
        for card in self.players[0].hand:
            if card.is_playable(self.table[-1]):
                how_many_cards_can_you_play += 1

        if how_many_cards_can_you_play is 0:
            print("You couldn't put any card on table, Drawing card from deck...")
            self.draw_card(0)
        else:
            print("Number of cards you can play:", how_many_cards_can_you_play)
            card_to_put_on_table = input("Select: ")
            card_to_put_on_table = int(card_to_put_on_table)

            # option to draw card
            if card_to_put_on_table is len(self.players[0].hand):
                self.draw_card(0)
            # check i card can be put on table
            elif self.can_put_on_table(card_to_put_on_table):
                self.table.append(self.players[0].hand.pop(card_to_put_on_table))


    # checks if card can be put on table
    def can_put_on_table(self, card):
        '''
        Checks if card can be put on table by game rules (same suit or value)
        :param card: compares card with one on the table
        :return: true if card can be put on table
        '''
        if not self.players[0].hand[card].is_playable(self.table[-1]):
            print("Can't put this card on table")
            return False
        return True

    # in progress
    def check_restrictions(self):
        card = self.table[-1]

        # switch case to use restriction methods
        restrictions = {
            CardValue.Two: self.restriction_two,
            CardValue.Three: self.restriction_three,
            CardValue.Four: self.restriction_four,
            CardValue.Jack: self.restriction_jack,
            CardValue.King: self.restriction_king,
            CardValue.Ace: self.restriction_ace
        }

        restriction = restrictions.get(card.value)
        restriction()

    # another class for restrictions ??
    # restriction made by '2'
    def restriction_two(self):
        '''
        Draw 2 cards
        :return:
        '''
        print("TWO")

    # restriction made by '3'
    def restriction_three(self):
        '''
        Draw 3 cards
        :return:
        '''
        print("THREE")

    # restriction made by '4'
    def restriction_four(self):
        '''
        Loose turn
        :return:
        '''
        print("FOUR")

    # restriction made by 'jack'
    def restriction_jack(self):
        '''
        Can change figure to (5-10 or Queen)
        :return:
        '''
        print("JACK")

    # restriction made by 'king'
    def restriction_king(self):
        '''
        Draw 5 cards
        :return:
        '''
        print("KING")

    # restriction made by 'ace'
    def restriction_ace(self):
        '''
        Choose color
        :return:
        '''
        print("ACE")

    # win condition - empty hand means player won
    def win_con(self, player_id):
        if not self.players[player_id].hand:
            print("You won")
            exit(0)  # change game loop condition

    # draw one card --> put in player's hand
    def draw_card(self, player_id):
        self.players[player_id].hand.append(self.deck.draw())




if __name__ == "__main__":
    makao = Game()
    while not makao.win_con(0):
        makao.put_on_table()


# main function
# if __name__ == "__main__":
#
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

