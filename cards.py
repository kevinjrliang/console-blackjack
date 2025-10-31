import random
from typing import List
from itertools import product


class Card:
    """Represent a single playing card.

    The card stores a suit index which maps into `Card.suits` and a number
    in the range 1..13 where 1=Ace and 11..13 are face cards.
    """

    suit: int
    number: int
    suits = ["S", "H", "C", "D"]  # suits

    def __init__(self, suit, number):
        """Initialize a Card.

        Args:
            suit: integer index into Card.suits.
            number: rank of the card (1-13).
        """
        self.suit = suit
        self.number = number

    def __str__(self):
        """Return a short representation like 'AS', '10D' or 'KH'."""
        num = str(self.number)

        match self.number:
            case 1:
                num = "A"
            case 11:
                num = "J"
            case 12:
                num = "Q"
            case 13:
                num = "K"

        suit = self.suits[self.suit]
        return num + suit

    def __repr__(self):
        """Return same as __str__ for debugging contexts."""
        return self.__str__()


class Deck:
    """A shoe containing one or more standard 52-card decks.

    Provides basic operations like shuffle, draw and returnToDeck.
    """

    deck: List[Card]

    def __init__(self, num_decks: int = 1) -> None:
        """Create `num_decks` deck(s) of cards.

        Uses `Card.suits` to determine the number of suits instead of hardcoding 4.
        """
        if num_decks < 1:
            raise ValueError("num_decks must be >= 1")

        suits = range(len(Card.suits))
        numbers = range(1, 14)
        # iterate over decks so multiple decks are grouped together
        self.deck = [
            Card(suit=s, number=n)
            for _ in range(num_decks)
            for s, n in product(suits, numbers)
        ]

    def shuffleDeck(self):
        """Shuffle the deck of cards in place."""
        random.shuffle(self.deck)

    def draw(self, num: int) -> List[Card]:
        """Draw `num` cards from the deck and return them.

        Args:
            num: number of cards to draw.

        Returns:
            List[Card]: list of drawn Card objects (last-in-first-out order).
        """
        ret = []
        for _ in range(num):
            ret.append(self.deck.pop())
        return ret

    def returnToDeck(self, cards: List[Card]) -> int:
        """Return the provided cards to the deck (appended to the end).

        Args:
            cards: list of Card objects to return.

        Returns:
            int: number of cards returned.
        """
        for c in cards:
            self.deck.append(c)
        return len(cards)

    def __str__(self) -> str:
        """Return a compact string form of the deck (for debugging)."""
        return str(self.deck)

    def __repr__(self) -> str:
        """Alias for __str__ used by the interpreter."""
        return self.__str__()
