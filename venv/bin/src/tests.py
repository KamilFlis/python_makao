from makao import *
import mock
import unittest

# Brak kart do dobrania w talii - oczekiwane zabrane karty ze stołu (oprócz ostatniej) i utworzona nowa talia - sprawdzenie długości listy przechowującej karty w talii i na stole.
# Sprawdzenie czy można położyć kartę pasującą do zasad gry - oczekiwane położenie karty na stole.
# Sprawdzenie czy można położyć kartę niepasującą do zasad gry - oczekiwana informacja, że nie można położyć tej karty.
# Sprawdzenie warunku zwycięstwa (pusta "ręka" gracza) - oczekiwany komunikat o zwycięstwie danego gracza.
# Dobieranie karty z talii - oczekiwane: karta z talii trafia do rąk gracza.
# Test kart specjalnych i nałożonych poszczególnych restrykcji.

class Tests(unittest.TestCase):

    # no cards to draw - expected cards taken from table (except for top of table), put in deck and one card from deck put in player's hand
    def test_draw_if_no_cards_in_deck(self):
        # given
        amount = 1
        macao = Game()
        for card in macao.deck.cards:
            macao.table.append(card)

        macao.deck.cards = []

        # when
        deck_len_expected = len(macao.table) - amount - 1

        # method tested
        macao.players[0].draw_card(amount)

        # then
        self.assertEqual(len(macao.table), 1, 'Number of cards on table should equal 1')
        self.assertEqual(len(macao.deck.cards), deck_len_expected, 'Number of cards in deck should be' + str(deck_len_expected))
        self.assertEqual(len(macao.players[0].hand), (5 + amount), 'Number of cards in hands player should be' + str((5 + amount)))


    # tests if card can be put on table if it is playable
    def test_can_put_on_table(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.Five))
        card_val = Card(CardSuit.SPADES, CardValue.Five)
        card_suit = Card(CardSuit.HEARTS, CardValue.Eight)
        card_not_playable = Card(CardSuit.CLUBS, CardValue.Seven)

        # when
        output_is_playable_value = macao.current().is_playable(card_val)
        output_is_playable_suit = macao.current().is_playable(card_suit)
        output_is_not_playable = macao.current().is_playable(card_not_playable)

        # then
        self.assertTrue(output_is_playable_value, 'Card should have the same value as the one on table')
        self.assertTrue(output_is_playable_suit, 'Card should have the same suit as the one on table')
        self.assertFalse(output_is_not_playable, 'Card should have same suit or value')


    # tests if player won
    def test_player_won(self):
        # given
        macao = Game()

        # when
        # game not finished
        output_not_finished = macao.win_con(0)

        # game finished
        macao.players[0].hand = []
        output_finished = macao.win_con(0)

        # then
        self.assertTrue(output_not_finished, 'Win_con should return true, game is not finished yet')
        self.assertFalse(output_finished, 'Win_con should return false, game is finished')


    # tests if drawn card is in player's hand
    def test_draw_card(self):
        # given
        macao = Game()
        expected = macao.deck.cards[-1]

        # when
        macao.players[0].draw_card(1)
        output = macao.players[0].hand[-1]

        # then
        self.assertEqual(output, expected, 'Card in hand should be ' + str(expected) + ' not ' + str(output))


    # special cards tests
    # jack
    def test_special_jack(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.Jack))

        # mocking input value for demanding '6'
        with mock.patch.object(__builtins__, 'input', lambda value: '6'):
            macao.make_restriction(1)

        # when
        # puts jack
        expected_jack = 2
        output_jack = macao.restriction(Card(CardSuit.SPADES, CardValue.Jack), macao.players[0])

        # puts illegal card
        output_illegal = macao.restriction(Card(CardSuit.SPADES, CardValue.Three), macao.players[0])

        # puts demanded card
        demand = CardValue.Six
        output_demand = macao.restriction(Card(CardSuit.CLUBS, demand), macao.players[0])

        # then
        self.assertEqual(output_jack, expected_jack, 'Output should be ' + str(expected_jack))
        self.assertFalse(output_illegal, 'Output should be false')
        self.assertTrue(output_demand, 'Output should be true')


    # ace
    def test_special_ace(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.Ace))

        # mocking input value for demanding 'SPADES'
        with mock.patch.object(__builtins__, 'input', lambda value: '0'):
            macao.make_restriction(1)

        # when
        # puts ace
        expected_ace = 2
        output_ace = macao.restriction(Card(CardSuit.CLUBS, CardValue.Ace), macao.players[0])

        # puts illegal card
        output_illegal = macao.restriction(Card(CardSuit.HEARTS, CardValue.Five), macao.players[0])

        # puts demanded card
        demand = CardSuit.SPADES
        output_demand = macao.restriction(Card(demand, CardValue.Eight), macao.players[0])

        # then
        self.assertEqual(output_ace, expected_ace, 'Output should be ' + str(expected_ace))
        self.assertFalse(output_illegal, 'Output should be false')
        self.assertTrue(output_demand, 'Output should be true')


    # two
    def test_special_two(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.Two))
        macao.make_restriction(0)
        macao.table.append(Card(CardSuit.SPADES, CardValue.Two))
        macao.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 4
        output_draw = macao.card_pending

        # puts two
        output_two = macao.restriction(Card(CardSuit.DIAMONDS, CardValue.Two), macao.players[1])

        # puts three of same suit
        output_three = macao.restriction(Card(CardSuit.SPADES, CardValue.Three), macao.players[1])

        # puts special king (spades)
        output_king = macao.restriction(Card(CardSuit.SPADES, CardValue.King), macao.players[1])

        # puts three of other suit = illegal card
        expected_illegal = -1
        output_illegal = macao.restriction(Card(CardSuit.HEARTS, CardValue.Three), macao.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))


    # three
    def test_special_three(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.Three))
        macao.make_restriction(0)
        macao.table.append(Card(CardSuit.SPADES, CardValue.Three))
        macao.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 6
        output_draw = macao.card_pending

        # puts three
        output_three = macao.restriction(Card(CardSuit.CLUBS, CardValue.Three), macao.players[1])

        # puts two of same suit
        output_two = macao.restriction(Card(CardSuit.SPADES, CardValue.Two), macao.players[1])

        # puts special king (spades)
        output_king = macao.restriction(Card(CardSuit.SPADES, CardValue.King), macao.players[1])

        # puts two of other suit = illegal card
        expected_illegal = -1
        output_illegal = macao.restriction(Card(CardSuit.HEARTS, CardValue.Two), macao.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))


    # king
    def test_special_king(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.HEARTS, CardValue.King))
        macao.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 5
        output_draw = macao.card_pending

        # puts two of same suit
        output_two = macao.restriction(Card(CardSuit.HEARTS, CardValue.Two), macao.players[1])

        # puts three of same suit
        output_three = macao.restriction(Card(CardSuit.HEARTS, CardValue.Three), macao.players[1])

        # puts another special king
        output_king = macao.restriction(Card(CardSuit.SPADES, CardValue.King), macao.players[1])

        # puts two of other suit = illegal card
        expected_illegal = -1
        output_illegal = macao.restriction(Card(CardSuit.CLUBS, CardValue.Two), macao.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))


    # four
    def test_special_four(self):
        # given
        macao = Game()
        macao.table.append(Card(CardSuit.DIAMONDS, CardValue.Four))
        macao.make_restriction(0)
        macao.table.append(Card(CardSuit.SPADES, CardValue.Four))
        macao.make_restriction(0)

        # when
        expected_wait = 2
        output_wait = macao.stops_pending

        # puts four
        output_four = macao.restriction(Card(CardSuit.CLUBS, CardValue.Four), macao.players[1])

        # puts illegal card
        expected_illegal = -1
        output_illegal = macao.restriction(Card(CardSuit.SPADES, CardValue.Queen), macao.players[1])

        # then
        self.assertEqual(output_wait, expected_wait, "Should be " +  str(expected_wait))
        self.assertTrue(output_four, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))


if __name__ == '__main__':
    unittest.main()