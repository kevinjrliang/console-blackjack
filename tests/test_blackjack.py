"""Unit tests for basic Blackjack components.

This module tests small, deterministic behaviors:
- Deck creation for single and multiple decks (counts)
- Drawing and returning cards to the deck
- Hand scoring (Ace handling) and blackjack detection
- Game forwards `num_decks` to the Deck constructor

These tests avoid any interactive prompts and exercise pure logic only.
"""

import unittest
import config
from blackjack import Deck, Card, Hand, Game


class TestDeckAndHand(unittest.TestCase):
    def test_single_deck_count(self):
        # Creating a single deck should produce 52 cards
        d = Deck(1)
        self.assertEqual(len(d.deck), 52)

    def test_multiple_decks_count(self):
        # Creating multiple decks should multiply the count
        d = Deck(6)
        self.assertEqual(len(d.deck), 52 * 6)

    def test_draw_and_return(self):
        # Drawing removes cards from the deck and returning them restores count
        d = Deck(1)
        initial = len(d.deck)
        drawn = d.draw(3)
        self.assertEqual(len(drawn), 3)
        self.assertEqual(len(d.deck), initial - 3)
        returned = d.returnToDeck(drawn)
        self.assertEqual(returned, 3)
        self.assertEqual(len(d.deck), initial)

    def test_hand_aces_and_blackjack(self):
        # Ace + 9 should count the ace as 11 to make 20
        h = Hand([Card(0, 1), Card(0, 9)], 10)
        self.assertEqual(h.score, 20)

        # Ace + King should be recognized as a blackjack (two-card 21)
        h2 = Hand([Card(0, 1), Card(1, 13)], 10)
        self.assertTrue(h2.blackjack)

    def test_multiple_aces(self):
        # Multiple aces should be counted correctly (A, A, 9 == 21)
        h = Hand([Card(0, 1), Card(1, 1), Card(2, 9)], 5)
        self.assertEqual(h.score, 21)

    def test_bust_detection(self):
        # A simple bust: 10 + 9 + 5 = 24
        h = Hand([Card(0, 10), Card(0, 9), Card(0, 5)], 5)
        self.assertTrue(h.bust)

    def test_draw_from_empty_deck_raises(self):
        # Drawing more cards than present should raise IndexError from list.pop
        d = Deck(1)
        # draw all cards
        _ = d.draw(len(d.deck))
        with self.assertRaises(IndexError):
            d.draw(1)

    def test_shuffle_preserves_multiset(self):
        # Shuffle should not change the multiset of cards in the deck
        d = Deck(2)
        before = [(c.suit, c.number) for c in d.deck]
        d.shuffleDeck()
        after = [(c.suit, c.number) for c in d.deck]
        # same counts for each (suit, number) pair
        self.assertEqual(sorted(before), sorted(after))


class TestGame(unittest.TestCase):
    def test_game_num_decks_forwarded(self):
        # Ensure the Game constructor forwards num_decks to Deck
        g = Game(1, 1000, config.DEFAULT_MINIMUM_BUY, [], num_decks=3)
        self.assertEqual(len(g.deck.deck), 52 * 3)

    def test_dealer_hits_until_threshold(self):
        # Dealer with 10+6 (16) should draw until reaching or exceeding the stand threshold
        g = Game(1, 1000, config.DEFAULT_MINIMUM_BUY, [], num_decks=1)
        # set dealer to 10 and 6 => score 16
        g.dealer = Hand([Card(0, 10), Card(0, 6)], 0, isDealer=True)
        # arrange the deck so the next card to be popped is a 2 (so dealer will reach 18)
        g.deck.deck = [Card(0, 3), Card(0, 2)]
        initial_deck_len = len(g.deck.deck)

        # Run dealer draw loop (same logic used in Game.begin_game)
        while g.dealer.score < config.DEALER_STAND_THRESHOLD:
            g.hit(-1)

        # Dealer should have drawn the 2 and now have score >= threshold
        self.assertGreaterEqual(g.dealer.score, config.DEALER_STAND_THRESHOLD)
        self.assertTrue(any(c.number == 2 for c in g.dealer.cards))
        self.assertEqual(len(g.deck.deck), initial_deck_len - 1)

    def test_play_dealer_method(self):
        # Directly call Game.play_dealer() to ensure the method draws until threshold
        g = Game(1, 1000, config.DEFAULT_MINIMUM_BUY, [], num_decks=1)
        g.dealer = Hand([Card(0, 9), Card(0, 7)], 0, isDealer=True)  # 16
        # Put a single card (2) at the end so pop() will draw it
        g.deck.deck = [Card(0, 2)]
        initial_len = len(g.deck.deck)

        # run the dealer method (sleeps are short; we can patch time.sleep if needed)
        g.play_dealer()

        # Dealer should have drawn the 2 and reached at least the threshold
        self.assertTrue(any(c.number == 2 for c in g.dealer.cards))
        self.assertGreaterEqual(g.dealer.score, config.DEALER_STAND_THRESHOLD)
        self.assertEqual(len(g.deck.deck), initial_len - 1)


if __name__ == "__main__":
    unittest.main()
