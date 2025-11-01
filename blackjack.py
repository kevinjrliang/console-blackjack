import random
from typing import List, Optional
import time
import os
import config

# When TEST_MODE is True the code will avoid printing and sleeping which
# makes automated tests quieter and faster. Tests can enable this by either
# passing `test_mode=True` to `Game(...)` or by setting
# `Blackjack.TEST_MODE = True` before creating a Game instance.
TEST_MODE = False


def _print(*args, **kwargs):
    if not TEST_MODE:
        print(*args, **kwargs)


def _sleep(seconds: float):
    if not TEST_MODE:
        time.sleep(seconds)

class Card:
    suit: int
    number: int
    suits = ['S', 'H', 'C', 'D'] # suits

    def __init__(self, suit, number):
        self.suit = suit
        self.number = number

    def __str__(self):
        num = str(self.number)
        
        match self.number:
            case 1:
                num = 'A'
            case 11:
                num = 'J'
            case 12:
                num = 'Q'
            case 13:
                num = 'K'

        suit = self.suits[self.suit]
        return num+suit
    
    def __repr__(self):
        return self.__str__()
    
class Hand:
    cards: List[Card]
    score: int
    hideDealerCards: bool
    bust: bool
    bet: float
    status: int
    blackjack: bool
    split: bool

    def __init__(self, cards: List[Card], bet: float, isDealer: bool = False) -> None:
        self.hideDealerCards = isDealer
        self.cards = cards
        self.bust = False
        self.bet = bet
        self.status = 10 # 10 means in play, -1 lost, 0 tie, 1 win
        self.blackjack = False
        self.split = False

        self.updateScore()

    def addToHand(self, card: List[Card]) -> None:
        self.cards.extend(card)
        self.updateScore()
    
    def popFromHand(self) -> Card:
        card = self.cards.pop()
        self.updateScore()
        return card

    def updateScore(self) -> None:
        nonAces = []
        aces = 0
        for c in self.cards:
            if c.number == 1:
                aces += 1
            elif c.number > 9:
                nonAces.append(10)
            else:
                nonAces.append(c.number)
        score = sum(nonAces) + aces * 11

        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        self.score = score

        if self.score > 21:
            self.bust = True

        if self.score == 21 and len(self.cards) == 2:
            self.blackjack = True

    def finishHand(self, dealer: Hand):
        if self.bust or (not dealer.bust and dealer.score > self.score):
            self.status = -1
        elif dealer.score == self.score:
            self.status = 0
        else:
            self.status = 1

    def checkHand(self):
        return self.status
        

    def __str__(self) -> str:
        if len(self.cards) == 0:
            return ""
    
        if self.hideDealerCards:
            return str(self.cards[0]) + ", " + ", ".join(["XX" for c in self.cards[1:]])
        return ", ".join([str(c) for c in self.cards]) + " - Score: " + str(self.score)
    
    def __repr__(self) -> str:
        return self.__str__()
    
class Deck:
    deck: List[Card]

    def __init__(self, num_decks: int = 1) -> None:
        if num_decks < 1:
            raise ValueError("num_decks must be >= 1")
        numbers = [i + 1 for i in range(13)]  # numbers
        # build `num_decks` worth of cards
        self.deck = [Card(suit=s, number=n) for _ in range(num_decks) for n in numbers for s in range(4)]

    def shuffleDeck(self):
        random.shuffle(self.deck)

    def draw(self, num: int) -> List[Card]:
        ret = []
        for _ in range(num):
            ret.append(self.deck.pop())
        return ret
    
    def returnToDeck(self, cards: List[Card]) -> int:
        for c in cards:
            self.deck.append(c)
        return len(cards)
    
    def __str__(self) -> str:
        return str(self.deck)
    
    def __repr__(self) -> str:
        return self.__str__()
    
class Game:
    dealer: Hand
    hands: List[Hand]
    deck: Deck
    total_money: float
    minimum_buy: float

    num_hands: int

    def __init__(self, hands_to_play: int, total_money: float, minimum_buy: float = 50, starting_bets:List[float] = [], num_decks: int = config.DEFAULT_NUM_DECKS, test_mode: bool = False) -> None:
        """Initialize a Game.

        Args:
            hands_to_play: number of player hands.
            total_money: starting bankroll.
            minimum_buy: default bet per hand when not provided.
            starting_bets: optional list of starting bets.
            num_decks: how many 52-card decks to use in the shoe.
            test_mode: when True, suppress prints and sleeps (useful for tests).
        """
        # enable test mode for the module if requested
        if test_mode:
            global TEST_MODE
            TEST_MODE = True

        self.num_hands = hands_to_play
        self.deck = Deck(num_decks)
        self.total_money = total_money
        self.minimum_buy = minimum_buy
        self.hands = []
        for i in range(self.num_hands):
            if i < len(starting_bets):
                self.hands.append(Hand([], starting_bets[i]))
                self.total_money -= starting_bets[i]
            else:
                self.hands.append(Hand([], self.minimum_buy))
                self.total_money -= self.minimum_buy

        self.dealer = Hand([], 0, isDealer=True)


    def hit(self, player_no: int):
        if player_no == -1:
            self.dealer.addToHand(self.deck.draw(1))
        else:
            self.hands[player_no].addToHand(self.deck.draw(1))

    def deal(self):
        valid = False
        while not valid:
            valid = True
            for _ in range(2):
                for h in self.hands:
                    cards = self.deck.draw(1)
                    h.addToHand(cards)

            d_cards = self.deck.draw(2)
            self.dealer.addToHand(d_cards)

            if (self.dealer.score == 21):
                _print("Dealer has 21, resetting: " + str(self.dealer))
                self.resetDeck()
                valid = False

    def resetDeck(self):
        for h in self.hands:
            self.deck.returnToDeck(h.cards)
            h.cards = []
        self.deck.returnToDeck(self.dealer.cards)
        self.dealer.cards = []
        self.deck.shuffleDeck()

    def gameState(self, current_hand: Optional[int] = None, end_game: bool = False):
        _print("--------------------------------------")
        dealer_suffix = " <-- Dealer's turn" if current_hand is None and not end_game else ""
        _print("Dealer's Hand: " + str(self.dealer) + dealer_suffix)
        _print("\n")
        _print("Here are your hands: ")
        for i, h in enumerate(self.hands):
            if end_game:
                if h.status == -1:
                    _print(f"Hand {i + 1}: " + str(h) + f" - Bet: ${h.bet:.2f}" + " --LOSE--")
                elif h.status == 0:
                    _print(f"Hand {i + 1}: " + str(h) + f" - Bet: ${h.bet:.2f}" + " ==DRAW==")
                elif h.status == 1:
                    _print(f"Hand {i + 1}: " + str(h) + f" - Bet: ${h.bet:.2f}" + " **WIN**")
                else:
                    _print(f"Hand {i + 1}: " + str(h) + f" - Bet: ${h.bet:.2f}" + " ERROR INVALID HAND STATUS")
            else:
                playing_suffix = " <-- Playing" if current_hand == i else ""
                _print(f"Hand {i + 1}: " + str(h) + f" - Bet: ${h.bet:.2f}" + playing_suffix)
        _print("\n")
        _print(f"Total Money: ${self.total_money:.2f}")
        _print("--------------------------------------")
        _print("\n")

    def actionPrompt(self, hand_i: int):
        hand = self.hands[hand_i]
        if hand.blackjack:
            _print(f"Blackjack for hand {hand_i + 1}!")
            self.gameState()
            return
        elif hand.split and hand.cards[0].number == 1:
            _print("Split Aces, drawing one card...")
            self.hit(hand_i)
            self.gameState()
            return
        _print(f"Playing hand #{hand_i + 1}... Please enter the number for action")

        actions = ["Hit", "Stay"]
        

        if len(hand.cards) == 2:
            if not hand.split and self.total_money >= hand.bet:
                actions.append("Double")

                if hand.cards[0].number == hand.cards[1].number:
                    actions.append("Split")

        question = [f"{i + 1}. {a}" for i, a in enumerate(actions)]
        valid_response = [f"{i + 1}" for i in range(len(actions))]
        user_input = waitForInput(" | ".join(question) + ": ", valid_response)

        match user_input:
            case "1":
                while user_input == "1":
                    self.hit(hand_i)
                    self.gameState(current_hand=hand_i)
                    if hand.bust:
                        _print("Hand busted!")
                        break
                    else:
                        _print("Hit")
                    _print(f"Playing hand #{hand_i + 1}... Please enter the number for action")
                    user_input = waitForInput("1. Hit | 2. Stay: ", ["1", "2"])
                    if user_input == "2":
                        _print("Stay")
            case "2":
                _print("Stay")
            case "3":
                self.total_money -= hand.bet
                # double down: match the current bet
                hand.bet += hand.bet
                self.hit(hand_i)
                self.gameState(current_hand=hand_i)
                if hand.bust:
                    _print("Doubled and hand busted!")
                else:
                    _print("Doubled")
            case "4":
                
                self.total_money -= hand.bet
                new_hand = Hand([hand.popFromHand()], hand.bet)

                hand.split = True
                new_hand.split = True
                temp = []
                for i, h in enumerate(self.hands):
                    temp.append(h)
                    if i == hand_i:
                        temp.append(new_hand)
                self.hands = temp
                
                self.gameState()
                self.actionPrompt(hand_i)
                






    def begin_game(self):
        """Run a single round: shuffle, deal, run player turns, then dealer, then settle.

        This now delegates to `play_players()` and `play_dealer()` so those
        flows can be exercised independently in unit tests.
        """
        _print("Game Started!")
        self.deck.shuffleDeck()
        _sleep(0.5)
        _print("Dealing Cards...\n")
        self.deal()
        _sleep(1)

        # Player's turn
        self.play_players()

        # Dealer's move
        self.play_dealer()

        _print("Game Results")
        self.gameState(end_game=True)

    def play_players(self):
        """Iterate through each player's hand and prompt for actions."""
        i = 0
        while i < len(self.hands):
            h = self.hands[i]
            self.gameState(current_hand=i)
            self.actionPrompt(i)
            _sleep(0.5)
            i += 1

    def play_dealer(self):
        """Run the dealer's drawing logic and settle all hands against the dealer."""
        # Reveal dealer cards and draw until stand threshold
        self.dealer.hideDealerCards = False
        _print("Dealer reveals hidden card!")
        self.gameState()
        _sleep(1)
        while self.dealer.score < 17:
            _print("Dealer Draws...")
            _sleep(2)
            self.hit(-1)
            self.gameState()

            if (self.dealer.score > 17):
                _sleep(2)

        # Finalize results and adjust bankroll
        for h in self.hands:
            h.finishHand(self.dealer)
            if h.checkHand() == 0:
                self.total_money += h.bet
            elif h.checkHand() == 1:
                if h.blackjack:
                    self.total_money += h.bet * 2.5
                else:
                    self.total_money += h.bet * 2

def waitForInput(message: str, validResponses: List[str]):
    user_input = input(message)
    while user_input not in validResponses:
        _print("\nPlease enter a valid choice.")
        user_input = input(message)
    _print("\n")
    return user_input
    
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    _print('\n')
    _print("How much do you want to buy in?")
    buy_in = float(input())
    increments = 50.0
    play = True
    while play:
        play = False
        temp_buy = buy_in
        _print("How many hands do you want to play? Enter a number from 1 to 5")
        num_hands = int(waitForInput("Number of hands: ", ["1", "2", "3", "4", "5"]))
        bets: List[float] = []
        for i in range(num_hands):
            valid_bets = [str(int((i + 1) * increments)) for i in range(int(temp_buy // increments))]
            _print("What would you like to bet for hand " + str(i + 1) + "? Possible bets are: " + ", ".join(valid_bets) + ".")
            bet = float(waitForInput("Bet: ", valid_bets))
            bets.append(bet)
            temp_buy -= bet
        game = Game(num_hands, buy_in, increments, bets)
        game.begin_game()

        _print("Play again?")
        user_input = waitForInput("1. Yes | 2. Exit: ", ["1", "2"])

        if user_input == "1":
            play = True
            buy_in = game.total_money
            os.system('cls' if os.name == 'nt' else 'clear')