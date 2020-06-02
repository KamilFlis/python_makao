"""This module defines logic behind Macao card game."""
import random
from enum import Enum
from enum import IntEnum
from collections import Counter
import pygame
from properties import CARDS_PATH

# card values - name + value
class CardValue(IntEnum):
    """Card values from two to ace enumerated."""
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
    """Cards suits enumerated."""
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'

# special cards set
SPECIAL_CARDS = set()
SPECIAL_CARD_VALUES = [CardValue.TWO, CardValue.THREE,
                       CardValue.FOUR, CardValue.JACK, CardValue.ACE]
for card_suit in CardSuit:
    for card_val in SPECIAL_CARD_VALUES:
        SPECIAL_CARDS.add((card_val, card_suit))

SPECIAL_CARDS.add((CardValue.KING, CardSuit.SPADES))
SPECIAL_CARDS.add((CardValue.KING, CardSuit.HEARTS))
SPECIAL_CARDS = frozenset(SPECIAL_CARDS)

# values for jack restriction
NOT_SPECIAL_VALUES = []
SPECIAL_VALUES, _ = zip(*SPECIAL_CARDS)
for card_val in CardValue:
    if card_val not in SPECIAL_VALUES:
        NOT_SPECIAL_VALUES.append(card_val)

# card info
class Card:
    """Card object represents single playing card."""

    def __init__(self, suit, value, image=None):
        self.suit = suit
        self.value = value
        self.image = image

    def __str__(self):
        return "{} of {}".format(self.value.name, self.suit.value)

    def is_special(self):
        """Checks if card is in special cards."""
        return SPECIAL_CARDS.__contains__((self.value, self.suit))

    # check if card can be put on table (same color or value)
    def is_playable(self, other):
        """Checks if card can be put on table by the game rules."""
        if self.suit == other.suit or self.value == other.value:
            return True
        return False


# deck info and methods
class Deck:
    """Deck class represents full deck of cards."""

    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        """Builds deck of cards."""
        for suit in CardSuit:
            for val in CardValue:
                path = CARDS_PATH + str(val.value) + str(suit.value) + '.png'
                self.cards.append(Card(suit, val, pygame.image.load(path)))

    def shuffle(self):
        """Shuffles deck."""
        random.shuffle(self.cards)

    def show(self):
        """Show"""
        for card in self.cards:
            print(card)

    def draw(self):
        """Draws one card from deck."""
        return self.cards.pop()

    def count(self):
        """Counts how many cards are in deck."""
        return len(self.cards)


# player info
class Player:
    """Class represents player."""

    def __init__(self, name, player_id, is_bot=False):
        self.hand = []
        self.name = name
        self.player_id = player_id
        self.stop = 0
        self.turn = False
        self.is_bot = is_bot

    def toggle_turn(self):
        """Changes turn."""
        self.turn = not self.turn

class Restriction:
    """Class represents restriction made by special cards."""

    active = False
    def __init__(self):
        self.function = None
        self.turns = 0
        self.information = None

    def create(self, function, turns, information):
        """Creates restriction.

        :param bool function function: Returns True if can put card on table
        False if can't put card on table
        -1 if can't put card but function
        2 if can put card no mather what
        :param int turns: States how many turns restriction is active
        :param string information: Informs what card can be played
        """
        self.active = True
        self.function = function
        self.turns = turns
        self.information = information

    def disable(self):
        """Disables restriction."""
        self.active = False

    def turn(self):
        """Disables restriction if turns equals 0 else decreases number of turns by 1."""
        if self.active:
            if self.turns == 0:
                self.disable()
            else:
                self.turns -= 1

    def info(self):
        """Returns information about what card can be played."""
        if self.active:
            return self.information

    def __call__(self, card, player, mock=False):
        if self.active:
            return self.function(card, player, mock)
        return True


class Game:
    """Represents macao card game."""

    def __init__(self):
        self.players = [Player("Bot", 0, True), Player("You", 1)]
        self.restriction = Restriction()
        self.card_pending = 0
        self.stops_pending = 0
        self.deck = Deck()
        self.table = []
        self.deal()
        self.players[1].toggle_turn()

    def current(self):
        """Returns last card on table."""
        return self.table[-1]

    # gives player 5 cards and places 1 card on table
    def deal(self):
        """Deals 5 cards to players."""
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
        """Draws cards.

        :param player: player who will draw cards
        :param quantity: number of cards that will be drawn
        """
        for _ in range(quantity):
            if self.deck.count():
                player.hand.append(self.deck.draw())
            else:
                self.deck.cards = [card for card in self.table]
                self.table.clear()
                self.table.append(self.deck.cards.pop())
                self.deck.shuffle()
                player.hand.append(self.deck.draw())

    def find_playable(self, player):
        """Finds if player can put any card on table.

        :param player: player who's cards are checked
        :returns: None if player can't play any cards or list of playable cards
        """
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
        """Checks if chosen card can be put on table.

        :param player: player
        :param index: card index in hand
        :return: card that will be put on table or none
        """
        card_to_put_on_table = [index]

        for card_index in card_to_put_on_table:
            if player.hand[card_to_put_on_table[0]].value != player.hand[card_index].value:
                print('Can\'t put this card on table')
                self.draw_card(player, 1)
                return None

        cards = [player.hand[index] for index in card_to_put_on_table]
        card = cards[0]
        restriction = self.restriction(card, player, True)
        if restriction == -1:
            return None
        elif (not card.is_playable(self.current()) or restriction is False) and restriction != 2:
            return None

        self.restriction.turn()
        player.hand = [_ for _ in player.hand if _ not in cards]
        return cards

    def bot_turn(self, player):
        """Finds cards in bot's hand that can be played.

        :param player: bot
        :return: None if can't play any card or list of cards that can be played
        """
        playable = self.find_playable(player)

        if playable is None:
            return None

        card = random.choice(playable)
        player.hand = [_ for _ in player.hand if _ not in card]
        return card

    def two(self, player_id, index):
        """Creates restriction made by special card 'two'."""
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
                self.draw_card(self.players[player_to_draw], self.card_pending)
                self.card_pending = 0
                self.restriction.turn()
                return -1
            return False

        self.restriction.create(two_restriction, 1, 'You can put only 2 or 3 or special king')

    def three(self, player_id, index):
        """Creates restriction made by special card 'three'."""
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
                self.draw_card(self.players[player_to_draw], self.card_pending)
                self.card_pending = 0
                self.restriction.turn()
                return -1
            return False

        self.restriction.create(three_restriction, 1, 'You can put only 2 or 3 or special king')

    def four(self, player_id, index):
        """Creates restriction made by special card 'four'."""
        self.stops_pending += 1
        def four_restriction(changed, player, mock=False):
            if changed.value == CardValue.FOUR:
                return True
            elif not mock:
                player.stop += self.stops_pending
                self.stops_pending = 0
                self.restriction.turn()
                return -1
            return False

        self.restriction.create(four_restriction, 1, 'You can put only 4')

    def jack(self, player_id, index):
        """Creates restriction made by special card 'jack'."""
        card = self.current()
        if not self.players[player_id].is_bot:
            value = index
        else:
            counter = Counter(
                card.value for card in self.players[player_id].hand
                if card.value in NOT_SPECIAL_VALUES
            )

            if not counter:
                value = None
            else:
                value = counter.most_common(1)
                value = value[0][0]

        # only chosen value or jack
        def jack_restriction(changed, player, mock=False):
            if value is None:
                # don't change
                return changed.suit == self.current().suit
            elif changed.value == value or changed.value == CardValue.JACK:
                return 2
            return False

        if value is None:
            value = 'any ' + card.suit.value

        self.restriction.create(jack_restriction, 2, 'You can put only jack or ' + str(value))
        if value is None:
            self.restriction.turn()

    def king(self, player_id, index):
        """Creates restriction made by special card 'king'."""
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
                    self.draw_card(self.players[player_to_draw], self.card_pending)
                    self.card_pending = 0
                    self.restriction.turn()
                    return -1
                return False
            else:
                if (changed.value == CardValue.KING and changed.suit == CardSuit.HEARTS) or \
                        ((changed.value == CardValue.TWO or changed.value == CardValue.THREE) and
                         changed.suit == CardSuit.SPADES):
                    return True
                elif not mock:
                    self.draw_card(self.players[player_to_draw], self.card_pending)
                    self.card_pending = 0
                    self.restriction.turn()
                    return -1
                return False

        self.restriction.create(king_restriction, 1, 'You can put only 2 or 3 or special king')

    def ace(self, player_id, index):
        """Creates restriction made by special card 'ace'."""
        if not self.players[player_id].is_bot:
            suit = index

        else:
            counter = Counter(card.suit for card in self.players[player_id].hand)
            suit = counter.most_common(1)
            suit = suit[0][0]

        def ace_restriction(changed, player, mock=False):
            if changed.suit == suit or changed.value == CardValue.ACE:
                return 2
            return False

        self.restriction.create(ace_restriction, 2, 'You can put only Ace or ' + str(suit.value))

    def make_restriction(self, player_id, index=None):
        """Calls corresponding restriction's method base on card put on table."""
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
        """Condition to check if game is finished."""
        return False if not self.players[player_id].hand else True


# def turn(game, player_id):
#     """Plays in console."""
#     # show top of table
#     print("Cards in deck: " + str(game.deck.count()))
#     print("Cards on table: " + str(len(game.table)))
#     print("Table: ", end='')
#     print(game.current())
#     player = game.players[player_id]
#
#     if player.stop > 0:
#         print("Player #" + str(player.player_id) + " waits", player.stop, "turns")
#         player.stop -= 1
#         return
#
#     game.restriction.turn()
#
#     if player_id != 0:
#         player.show_hand()
#
#     print("Player #" + str(player_id) + " turn")
#     print("Player #" + str(player_id) + " card count:", len(player.hand))
#     time.sleep(1)
#
#     if player_id != 0:
#         cards = game.player_turn(player, index)
#     else:
#         cards = game.bot_turn(player)
#
#     if cards is not None:
#         for card in cards:
#             print("Player #" + str(player_id) + " puts", card, "on table")
#             game.table.append(card)
#             if not game.win_con(player_id):
#                 print("Player #" + str(player_id) + " won")
#                 exit(0)
#             game.make_restriction(player_id)



if __name__ == "__main__":
    print("Not this file")
