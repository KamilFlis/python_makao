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


specialCards = [CardValue.Two, CardValue.Three, CardValue.Four, CardValue.Jack, CardValue.Ace]
#specialCards = [2, 3, 4, 11, 14]

class CardSuit(Enum):
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'


# card info
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def show(self):
        print("{} of {}".format(self.value.name, self.suit.value))


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

    # special cards - to deleeete
    def wypisz(self):
        counter=0
        for card in self.cards:
            if not (((card.value is CardValue.King)
                    and (card.suit is  CardSuit.HEARTS
                         or card.suit is  CardSuit.CLUBS))
                    or card.value in specialCards):
                counter+=1
                card.show()
        print(counter)


#player info
class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name

    def showHand(self):
        for card in self.hand:
            card.show()


class Game:
    def __init__(self):
        self.players = [Player("Kamil"), Player("Computer")]
        self.deck = Deck()
        self.table = []
        self.deal()

    #gives player 5 cards and places 1 card on table
    def deal(self):
        self.deck.shuffle()
        for card in range(0, 5):
            for player in self.players:
                player.hand.append(self.deck.draw())

        card = self.deck.cards[len(self.deck.cards) - 1]

        # Correct this condition (special card cant be first on table)
        #while len(self.table) is 0:     <------- condition to loop if first card was special
            if not (((card.value is CardValue.King)
                  and (card.suit is CardSuit.HEARTS
                       or card.suit is CardSuit.CLUBS))
                or card.value in specialCards):
                self.table.append(self.deck.draw())

        for card in self.table:
            card.show()
        print("Cards in deck:", self.deck.count())
        print("On table: ")
        self.table[0].show()


#deck = Deck()
#deck.show()
#deck.wypisz()

makao = Game()
print("On hand")
makao.players[0].showHand()

