import pygame
import random
from enum import Enum
from enum import IntEnum

# path to card images
cards_path = '/home/kamil/Code/Python/Makao/cards_resized_renamed/'

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
    def __init__(self, suit, value, img_path):
        self.suit = suit
        self.value = value
        self.image = pygame.image.load(img_path)

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
                self.cards.append(Card(suit, val, cards_path + '{}{}.png'.format(val.value, suit.value)))

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
        self.players = [Player("Zygrfryda"), Player("Computer")]
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


##########################
    def put_on_table(self):
        for i in range(0, len(self.players[0].hand)):
            print(i, ":", end =' ')
            self.players[0].hand[i].show()     #self.players[0].show_hand()
        cardToPutOnTable = input("Select: ")
        cardToPutOnTable = int(cardToPutOnTable)
        #add buttons on cards
        self.table.append(self.players[0].hand.pop(cardToPutOnTable))

        for card in self.table:
            card.show()

##################


    # checks restrictions made by special cards and checks if card can be put on table
    def can_put_on_table(self):
        pass


carddd = Card(CardValue.King, CardSuit.HEARTS, "/home/kamil/Code/Python/Makao/cards_resized/KH.png")
print(str(carddd.suit.value)+str(carddd.value.value))

# main function
if __name__ == "__main__":


    # pygame initialization
    pygame.init()

    # create screen
    screen_width, screen_height = 1024, 768
    screen = pygame.display.set_mode((screen_width, screen_height))

    # title
    pygame.display.set_caption("Makao")


    makao = Game()



    running = True
    while running:

        # RGB color
        # greenish background
        screen.fill((3, 122, 48))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()


    pygame.quit()


