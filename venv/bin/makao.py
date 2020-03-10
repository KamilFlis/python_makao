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

class CardSuit(Enum):
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'


# special cards in game - 2, 3, 4, jack, ace, king of spades and king of hearts
specialCards = { CardValue.Two, CardValue.Three, CardValue.Four, CardValue.Jack,
                 CardValue.Ace, (CardValue.King, CardSuit.SPADES), (CardValue.King, CardSuit.HEARTS)}

# card info
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def show(self):
        print("{} of {}".format(self.value.name, self.suit.value))

    def is_special(self):
        return self in specialCards


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

    # special cards - temporary method
    def wypisz(self):
        counter=0
        for card in self.cards:
            if card.is_special():
                counter+=1
                card.show()
        print(counter)


#player info
class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name

    def show_hand(self):
        for card in self.hand:
            card.show()


class Game:
    def __init__(self):
        self.players = [Player("Kamil"), Player("Computer")]
        self.deck = Deck()
        self.table = []
        self.deal()

    # gives player 5 cards and places 1 card on table
    def deal(self):
        self.deck.shuffle()
        # add 5 cards to player's hand
        for card in range(0, 5):
            for player in self.players:
                player.hand.append(self.deck.draw())


        while len(self.table) is 0:    # <------- condition to loop if first card was special
            topCard = self.deck.cards[len(self.deck.cards) - 1]
            # Checks if first card on table isn't special
            if not topCard.is_special():
                self.table.append(self.deck.draw())
            else:
                self.deck.shuffle()

        print("Cards in deck:", self.deck.count())
        print("On table: ")
        self.table[0].show()

    def put_on_table(self):
        pass


    def can_put(self):
        pass


#deck = Deck()
#deck.show()
#deck.wypisz()

makao = Game()
print("On hand")
makao.players[0].show_hand()

