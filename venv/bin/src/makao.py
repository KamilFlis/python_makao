import random
import time
from enum import Enum
from enum import IntEnum
from collections import Counter
import pygame
from properties import CARDS_PATH

# card values - name + value
class CardValue(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class CardSuit(Enum):
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'

# special cards set
SPECIAL_CARDS = set()
SPECIAL_CARD_VALUES = [CardValue.TWO, CardValue.THREE, CardValue.FOUR, CardValue.JACK, CardValue.ACE]
for card_suit in CardSuit:
    for card_val in SPECIAL_CARD_VALUES:
        SPECIAL_CARDS.add((card_val, card_suit))

SPECIAL_CARDS.add((CardValue.KING, CardSuit.SPADES))
SPECIAL_CARDS.add((CardValue.KING, CardSuit.HEARTS))
SPECIAL_CARDS = frozenset(SPECIAL_CARDS)

# card info
class Card:

    def __init__(self, suit, value, image=None):
        self.suit = suit
        self.value = value
        self.image = image

    def __str__(self):
        return "{} of {}".format(self.value.name, self.suit.value)

    def is_special(self):
        return SPECIAL_CARDS.__contains__((self.value, self.suit))

    # check if card can be put on table (same color or value)
    def is_playable(self, other):
        if self.suit == other.suit or self.value == other.value:
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
                path = CARDS_PATH + str(val.value) + str(suit.value) + '.png'
                self.cards.append(Card(suit, val, pygame.image.load(path)))

    def shuffle(self):
        random.shuffle(self.cards)

    def show(self):
        for card in self.cards:
            print(card)

    def draw(self):
        return self.cards.pop()

    def count(self):
        return len(self.cards)


# player info
class Player:

    def __init__(self, name, player_id, is_bot=False):
        self.hand = []
        self.name = name
        self.player_id = player_id
        self.stop = 0
        self.turn = False
        self.is_bot = is_bot

    def show_hand(self):
        for i in range(len(self.hand)):
            print(str(i) + ":", end=' ')
            print(self.hand[i])
        print(len(self.hand), ": Draw card")
        print((len(self.hand) + 1), ": EXIT!")

    def toggle_turn(self):
        self.turn = not self.turn

class Restriction:

    active = False
    def __init__(self):
        self.function = None
        self.turns = 0
        self.information = None

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
            return self.information

    def __call__(self, card, player, mock=False):
        if self.active:
            return self.function(card, player, mock)
        return True


class Game:

    def __init__(self):
       # print("Makao!")
        self.players = [Player("Computer", 0, True), Player("Kamil", 1)]
        self.restriction = Restriction()
        self.card_pending = 0
        self.stops_pending = 0
        self.deck = Deck()
        self.table = []
        self.deal()
        self.players[1].toggle_turn()

    def current(self):
        return self.table[-1]

    # gives player 5 cards and places 1 card on table
    def deal(self):
        """
        Deals 5 cards to players.
        """
        self.deck.shuffle()
        # add 5 cards to player's hand
        for _ in range(5):
            for player in self.players:
                player.hand.append(self.deck.draw())

        while not self.table:    # <-- condition to loop if first card was special
            # Checks if first card on table isn't special else shuffles deck
            if not self.deck.cards[-1].is_special():
                self.table.append(self.deck.draw())
            else:
                self.deck.shuffle()

    def draw_card(self, player, quantity):
        print("Player #" + str(player.player_id) + " draws", quantity, "cards")
        for _ in range(quantity):
            if self.deck.count():
                player.hand.append(self.deck.draw())
            else:
                print("Empty deck, shuffling cards...")
                time.sleep(3)
                self.deck.cards = [card for card in self.table]
                self.table.clear()
                self.table.append(self.deck.cards.pop())
                self.deck.shuffle()
                player.hand.append(self.deck.draw())

    def find_playable(self, player):
        playable = []
        for card in player.hand:
            restriction = self.restriction(card, player, True)
            if restriction and card.is_playable(self.current()) or restriction == 2:
                playable.append([card])

        if not playable:
            restriction = self.restriction(player.hand[0], player, False)
            if restriction == -1:
                return None
            self.draw_card(player, 1)
            return None

        return playable

    def player_turn(self, player, index):

        card_to_put_on_table = [index]

        for card_index in card_to_put_on_table:
            if player.hand[card_to_put_on_table[0]].value != player.hand[card_index].value:
                print("Can't put this card on table")
                self.draw_card(player, 1)
                return None

        cards = [player.hand[index] for index in card_to_put_on_table]

        card = cards[0]
        restriction = self.restriction(card, player, True)
        if restriction == -1:
            return None
        elif (not card.is_playable(self.current()) or restriction is False) and restriction != 2:
            print('Can\'t put this card on table')
            #self.draw_card(player, 1)
            return None

        player.hand = [_ for _ in player.hand if _ not in cards]
        return cards

    def bot_turn(self, player):
        playable = self.find_playable(player)

        if playable is None:
            return None

        else:
            card = random.choice(playable)
            player.hand = [_ for _ in player.hand if _ not in card]

            return card

    def two(self, player_id, index):
        card = self.current()
        self.card_pending += 2
        # can put only two or three in the same color; else draws two cards
        def two_restriction(changed, player, mock=False):
            if card.suit == CardSuit.SPADES or card.suit == CardSuit.HEARTS:
                if changed.value == CardValue.KING and changed.suit == card.suit or \
                        (changed.value == CardValue.TWO) or \
                        (changed.value == CardValue.THREE and changed.suit == card.suit):
                    return True
            if (changed.value == CardValue.TWO) or \
                    (changed.value == CardValue.THREE and changed.suit == card.suit):
                return True
            elif not mock:
                player_to_draw = 1 if player_id == 0 else 0
                print("Cards to draw " + str(self.card_pending))
                self.draw_card(self.players[player_to_draw], self.card_pending)
                self.card_pending = 0
                return -1
            return False

        self.restriction.create(two_restriction, 1, "You can put only 2 or 3 or special king")

    def three(self, player_id, index):
        card = self.current()
        self.card_pending += 3
        # can put only three or two in the same color; else draws three cards
        def three_restriction(changed, player, mock=False):
            if card.suit == CardSuit.SPADES or card.suit == CardSuit.HEARTS:
                if changed.value == CardValue.KING and changed.suit == card.suit:
                    return True
            if (changed.value == CardValue.THREE) or \
                    (changed.value == CardValue.TWO and changed.suit == card.suit):
                return True
            elif not mock:
                player_to_draw = 1 if player_id == 0 else 0
                print("Cards to draw " + str(self.card_pending))
                self.draw_card(self.players[player_to_draw], self.card_pending)
                self.card_pending = 0
                return -1
            return False

        self.restriction.create(three_restriction, 1, "You can put only 2 or 3 or special king")

    def four(self, player_id, index):
        self.stops_pending += 1
        def four_restriction(changed, player, mock=False):
            if changed.value == CardValue.FOUR:
                return True
            elif not mock:
                player.stop += self.stops_pending
                self.stops_pending = 0
                return -1
            return False

        self.restriction.create(four_restriction, 1, "You can put only 4")

    def jack(self, player_id, index):
        card = self.current()
        if not self.players[player_id].is_bot:
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
            values = {
                4: None,
                5: CardValue.FIVE,
                6: CardValue.SIX,
                7: CardValue.SEVEN,
                8: CardValue.EIGHT,
                9: CardValue.NINE,
                10: CardValue.TEN,
                11: CardValue.QUEEN
            }

            value = values.get(value, lambda: exit(1))

        else:
            counter = Counter(
                card.value for card in self.players[player_id].hand if not card.is_special() \
                or card.value == CardValue.KING
            )

            if not counter:
                value = None
            else:
                value = counter.most_common(1)
                value = value[0][0]

        print("Player #" + str(player_id) + " chose", value)

        # only chosen value or jack
        def jack_restriction(changed, player, mock=False):
            if value is None:
                # don't change
                return changed.is_playable(card)
            if changed.value == value or changed.value == CardValue.JACK:
                return 2
            return False

        if value is None:
            value = 'whatever'

        self.restriction.create(jack_restriction, 2, "You can put only jack or " + str(value))

    def king(self, player_id, index):
        card = self.current()
        self.card_pending += 5
        def king_restriction(changed, player, mock=False):
            player_to_draw = 1 if player_id == 0 else 0
            if card.suit == CardSuit.HEARTS:
                if (changed.value == CardValue.KING and changed.suit == CardSuit.SPADES) or \
                        ((changed.value == CardValue.TWO or changed.value == CardValue.THREE) and
                         changed.suit == CardSuit.HEARTS):
                    return True
                elif not mock:
                    print("Cards to draw " + str(self.card_pending))
                    self.draw_card(self.players[player_to_draw], self.card_pending)
                    self.card_pending = 0
                    return -1
                return False
            else:
                if (changed.value == CardValue.KING and changed.suit == CardSuit.HEARTS) or \
                        ((changed.value == CardValue.TWO or changed.value == CardValue.THREE) and
                         changed.suit == CardSuit.SPADES):
                    return True
                elif not mock:
                    print("Cards to draw " + str(self.card_pending))
                    self.draw_card(self.players[player_to_draw], self.card_pending)
                    self.card_pending = 0
                    return -1
                return False

        self.restriction.create(king_restriction, 2, "You can put only 2 or 3 or special King")

    def ace(self, player_id, index):
        if not self.players[player_id].is_bot:
            print("0 - Spades")
            print("1 - Hearts")
            print("2 - Clubs")
            print("3 - Diamonds")
            # suit = input("Choose color: ")
            # suit = int(suit)
            # suits = {
            #     0: CardSuit.SPADES,
            #     1: CardSuit.HEARTS,
            #     2: CardSuit.CLUBS,
            #     3: CardSuit.DIAMONDS
            # }
            #
            # suit = suits.get(suit, lambda: exit(1))
            suit = index

        else:
            counter = Counter(card.suit for card in self.players[player_id].hand)
            suit = counter.most_common(1)
            suit = suit[0][0]

        print("Player #" + str(player_id) + " chose", suit)

        def ace_restriction(changed, player, mock=False):
            if changed.suit == suit or changed.value == CardValue.ACE:
                return 2
            return False

        self.restriction.create(ace_restriction, 1, 'You can put only Ace or ' + str(suit.value))

    def make_restriction(self, player_id, index=None):
        card = self.current()
        if card.is_special():
            restriction = {
                CardValue.TWO: self.two,
                CardValue.THREE: self.three,
                CardValue.FOUR: self.four,
                CardValue.JACK: self.jack,
                CardValue.KING: self.king,
                CardValue.ACE: self.ace
            }

            func = restriction.get(card.value)
            func(player_id, index)

    # win condition - empty hand means player won
    def win_con(self, player_id):
        return False if not self.players[player_id].hand else True



def turn(game, player_id):
    # show top of table
    print("Cards in deck: " + str(game.deck.count()))
    print("Cards on table: " + str(len(game.table)))
    print("Table: ", end='')
    print(game.current())
    player = game.players[player_id]

    if player.stop > 0:
        print("Player #" + str(player.player_id) + " waits", player.stop, "turns")
        player.stop -= 1
        return

    game.restriction.turn()

    if player_id != 0:
        player.show_hand()

    print("Player #" + str(player_id) + " turn")
    print("Player #" + str(player_id) + " card count:", len(player.hand))
    time.sleep(1)

    if player_id != 0:
        cards = game.player_turn(player, index)
    else:
        cards = game.bot_turn(player)

    if cards is not None:
        for card in cards:
            print("Player #" + str(player_id) + " puts", card, "on table")
            game.table.append(card)
            if not game.win_con(player_id):
                print("Player #" + str(player_id) + " won")
                exit(0)
            game.make_restriction(player_id)



if __name__ == "__main__":
    print("Not this file")
    exit(0)
    macao = Game()
    while macao.win_con(0) or macao.win_con(1):
        turn(macao, 0)
        turn(macao, 1)
