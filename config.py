"""Configuration constants for console-blackjack.

Centralize hard-coded values here so they can be changed easily.
"""

# Monetary/defaults
DEFAULT_INCREMENTS: float = 50.0
DEFAULT_MINIMUM_BUY: float = 50.0

# Gameplay
MAX_HANDS: int = 5
DEFAULT_NUM_DECKS: int = 6
DEALER_STAND_THRESHOLD: int = 17

# Timings (seconds)
SLEEP_SHUFFLE: float = 0.5
SLEEP_DEAL: float = 1.0
SLEEP_SHORT: float = 0.5
SLEEP_LONG: float = 2.0
