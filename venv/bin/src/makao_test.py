import makao
import unittest
import unittest.mock

# Brak kart do dobrania w talii - oczekiwane zabrane karty ze stołu (oprócz ostatniej) i utworzona nowa talia - sprawdzenie długości listy przechowującej karty w talii i na stole.
# Sprawdzenie czy można położyć kartę pasującą do zasad gry - oczekiwane położenie karty na stole.
# Sprawdzenie czy można położyć kartę niepasującą do zasad gry - oczekiwana informacja, że nie można położyć tej karty.
# Sprawdzenie warunku zwycięstwa (pusta "ręka" gracza) - oczekiwany komunikat o zwycięstwie danego gracza.
# Dobieranie karty z talii - oczekiwane: karta z talii trafia do rąk gracza.
# Test kart specjalnych i nałożonych poszczególnych restrykcji.

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = makao.Game()

    # no cards to draw - expected cards taken from table (except for top of table), put in deck and one card from deck put in player's hand
    def test_draw_if_no_cards_in_deck(self):
        # given
        amount = 1
        for card in self.game.deck.cards:
            self.game.table.append(card)

        self.game.deck.cards = []

        # when
        deck_len_expected = len(self.game.table) - amount - 1

        # method tested
        self.game.draw_card(self.game.players[0], amount)

        # then
        self.assertEqual(len(self.game.table), 1, 'Number of cards on table should equal 1')
        self.assertEqual(len(self.game.deck.cards), deck_len_expected, 'Number of cards in deck should be' + str(deck_len_expected))
        self.assertEqual(len(self.game.players[0].hand), (5 + amount), 'Number of cards in hands player should be' + str((5 + amount)))


    # tests if card can be put on table if it is playable
    def test_can_put_on_table(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.FIVE))
        card_val = makao.Card(makao.CardSuit.SPADES, makao.CardValue.FIVE)
        card_suit = makao.Card(makao.CardSuit.HEARTS, makao.CardValue.EIGHT)
        card_not_playable = makao.Card(makao.CardSuit.CLUBS, makao.CardValue.SEVEN)

        # when
        output_is_playable_value = self.game.current().is_playable(card_val)
        output_is_playable_suit = self.game.current().is_playable(card_suit)
        output_is_not_playable = self.game.current().is_playable(card_not_playable)

        # then
        self.assertTrue(output_is_playable_value, 'Card should have the same value as the one on table')
        self.assertTrue(output_is_playable_suit, 'Card should have the same suit as the one on table')
        self.assertFalse(output_is_not_playable, 'Card should have same suit or value')

    # tests if player won
    def test_player_won(self):

        # when
        # game not finished
        output_not_finished = self.game.win_con(0)

        # game finished
        self.game.players[0].hand = []
        output_finished = self.game.win_con(0)

        # then
        self.assertTrue(output_not_finished, 'Win_con should return true, game is not finished yet')
        self.assertFalse(output_finished, 'Win_con should return false, game is finished')


    # tests if drawn card is in player's hand
    def test_draw_card(self):
        # given
        expected = self.game.deck.cards[-1]

        # when
        self.game.draw_card(self.game.players[0], 1)
        output = self.game.players[0].hand[-1]

        # then
        self.assertEqual(output, expected, 'Card in hand should be ' + str(expected) + ' not ' + str(output))


    # special cards tests
    # jack
    def test_special_jack(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.JACK))

        # mocking input value for demanding '6'
        with unittest.mock.patch.object(__builtins__, 'input', lambda value: '6'):
            self.game.make_restriction(1)

        # when
        # puts jack
        expected_jack = 2
        output_jack = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.JACK), self.game.players[0])

        # puts illegal card
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.THREE), self.game.players[0])

        # puts demanded card
        demand = makao.CardValue.SIX
        output_demand = self.game.restriction(makao.Card(makao.CardSuit.CLUBS, demand), self.game.players[0])

        # then
        self.assertEqual(output_jack, expected_jack, 'Output should be ' + str(expected_jack))
        self.assertFalse(output_illegal, 'Output should be false')
        self.assertTrue(output_demand, 'Output should be true')

    # ace
    def test_special_ace(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.ACE))

        # mocking input value for demanding 'SPADES'
        with unittest.mock.patch.object(__builtins__, 'input', lambda value: '0'):
            self.game.make_restriction(1)

        # when
        # puts ace
        expected_ace = 2
        output_ace = self.game.restriction(makao.Card(makao.CardSuit.CLUBS, makao.CardValue.ACE), self.game.players[0])

        # puts illegal card
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.FIVE), self.game.players[0])

        # puts demanded card
        demand = makao.CardSuit.SPADES
        output_demand = self.game.restriction(makao.Card(demand, makao.CardValue.EIGHT), self.game.players[0])

        # then
        self.assertEqual(output_ace, expected_ace, 'Output should be ' + str(expected_ace))
        self.assertFalse(output_illegal, 'Output should be false')
        self.assertTrue(output_demand, 'Output should be true')

    # two
    def test_special_two(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.TWO))
        self.game.make_restriction(0)
        self.game.table.append(makao.Card(makao.CardSuit.SPADES, makao.CardValue.TWO))
        self.game.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 4
        output_draw = self.game.card_pending

        # puts two
        output_two = self.game.restriction(makao.Card(makao.CardSuit.DIAMONDS, makao.CardValue.TWO), self.game.players[1])

        # puts three of same suit
        output_three = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.THREE), self.game.players[1])

        # puts special king (spades)
        output_king = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.KING), self.game.players[1])

        # puts three of other suit = illegal card
        expected_illegal = -1
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.THREE), self.game.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))

    # three
    def test_special_three(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.THREE))
        self.game.make_restriction(0)
        self.game.table.append(makao.Card(makao.CardSuit.SPADES, makao.CardValue.THREE))
        self.game.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 6
        output_draw = self.game.card_pending

        # puts three
        output_three = self.game.restriction(makao.Card(makao.CardSuit.CLUBS, makao.CardValue.THREE), self.game.players[1])

        # puts two of same suit
        output_two = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.TWO), self.game.players[1])

        # puts special king (spades)
        output_king = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.KING), self.game.players[1])

        # puts two of other suit = illegal card
        expected_illegal = -1
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.TWO), self.game.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))

    # king
    def test_special_king(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.KING))
        self.game.make_restriction(0)

        # when
        # cards to draw after two two's
        expected_draw = 5
        output_draw = self.game.card_pending

        # puts two of same suit
        output_two = self.game.restriction(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.TWO), self.game.players[1])

        # puts three of same suit
        output_three = self.game.restriction(makao.Card(makao.CardSuit.HEARTS, makao.CardValue.THREE), self.game.players[1])

        # puts another special king
        output_king = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.KING), self.game.players[1])

        # puts two of other suit = illegal card
        expected_illegal = -1
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.CLUBS, makao.CardValue.TWO), self.game.players[1])

        # then
        self.assertEqual(output_draw, expected_draw, 'Output should be' + str(expected_draw))
        self.assertTrue(output_two, 'Should be true')
        self.assertTrue(output_three, 'Should be true')
        self.assertTrue(output_king, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))

    # four
    def test_special_four(self):
        # given
        self.game.table.append(makao.Card(makao.CardSuit.DIAMONDS, makao.CardValue.FOUR))
        self.game.make_restriction(0)
        self.game.table.append(makao.Card(makao.CardSuit.SPADES, makao.CardValue.FOUR))
        self.game.make_restriction(0)

        # when
        expected_wait = 2
        output_wait = self.game.stops_pending

        # puts four
        output_four = self.game.restriction(makao.Card(makao.CardSuit.CLUBS, makao.CardValue.FOUR), self.game.players[1])

        # puts illegal card
        expected_illegal = -1
        output_illegal = self.game.restriction(makao.Card(makao.CardSuit.SPADES, makao.CardValue.QUEEN), self.game.players[1])

        # then
        self.assertEqual(output_wait, expected_wait, "Should be " +  str(expected_wait))
        self.assertTrue(output_four, 'Should be true')
        self.assertEqual(output_illegal, expected_illegal, 'Should be ' + str(expected_illegal))


if __name__ == '__main__':
    unittest.main()