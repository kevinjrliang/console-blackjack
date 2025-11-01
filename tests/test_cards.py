"""Unit tests for the `cards` module (Card and Deck).

These tests exercise edge cases and error handling for the low-level
card/deck primitives so higher-level game logic can rely on well-defined
behaviour.
"""

import unittest

from cards import Card, Deck


class TestCard(unittest.TestCase):
    def test_str_face_and_ace(self):
        # Ace
        self.assertEqual(str(Card(0, 1)), "AS")
        # Numbered
        self.assertEqual(str(Card(1, 10)), "10H")
        # Face cards
        self.assertEqual(str(Card(2, 11)), "JC")
        self.assertEqual(str(Card(3, 12)), "QD")
        self.assertEqual(str(Card(0, 13)), "KS")

    def test_invalid_suit_index_raises(self):
        # Creating a card with an out-of-range suit won't validate on init,
        # but trying to stringify it should raise an IndexError.
        c = Card(99, 5)
        with self.assertRaises(IndexError):
            _ = str(c)


class TestDeck(unittest.TestCase):
    def test_num_decks_must_be_positive(self):
        with self.assertRaises(ValueError):
            Deck(0)

    def test_deck_counts_and_order(self):
        d = Deck(1)
        self.assertEqual(len(d.deck), 52)

        # draw(0) should return an empty list and not modify the deck
        before = len(d.deck)
        drawn = d.draw(0)
        self.assertEqual(drawn, [])
        self.assertEqual(len(d.deck), before)

        # draw all cards returns the full set and empties the deck
        all_cards = d.draw(len(d.deck))
        self.assertEqual(len(all_cards), 52)
        self.assertEqual(len(d.deck), 0)

    def test_draw_more_than_available_raises(self):
        d = Deck(1)
        # drain deck
        _ = d.draw(len(d.deck))
        with self.assertRaises(IndexError):
            d.draw(1)

    def test_return_to_deck_appends_and_reports_count(self):
        d = Deck(1)
        drawn = d.draw(3)
        self.assertEqual(len(d.deck), 49)
        n = d.returnToDeck(drawn)
        self.assertEqual(n, 3)
        self.assertEqual(len(d.deck), 52)

    def test_shuffle_preserves_multiset(self):
        d = Deck(2)
        before = [(c.suit, c.number) for c in d.deck]
        d.shuffleDeck()
        after = [(c.suit, c.number) for c in d.deck]
        self.assertEqual(sorted(before), sorted(after))


if __name__ == "__main__":
    unittest.main()
