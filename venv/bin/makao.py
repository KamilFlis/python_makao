import random
from enum import Enum
from enum import IntEnum

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


# card info
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def show(self):
        print("{} of {}".format(self.value, self.suit))


# deck info and methods
class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()

    def build(self):
        suits = ['Spades', 'Clubs', 'Hearts', 'Diamonds']
        for s in suits:
            for val in CardValue:
                self.cards.append(Card(s, val.name))

    def shuffle(self):
        random.shuffle(self.cards)

    def show(self):
        for c in self.cards:
            c.show()


# player info
class Player:
    def __init__(self, name):
        self.name = name

deck = Deck()
#deck.build()
deck.show()