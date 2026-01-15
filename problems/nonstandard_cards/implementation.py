import random
import time


class EmojiCard:
    def __init__(self, emoji, name, value, tier):
        self.emoji = emoji
        self.name = name
        self.value = value
        self.tier = tier

    def __repr__(self):
        return f"{self.emoji} ({self.tier})"


def create_deck():
    # Define the card hierarchy
    card_data = [
        # Legendary - Value 5
        ("🐉", "Dragon", 5, "Legendary"),
        ("🦄", "Unicorn", 5, "Legendary"),
        ("👽", "Alien", 5, "Legendary"),
        ("👾", "Invader", 5, "Legendary"),
        # Epic - Value 4
        ("🦁", "Lion", 4, "Epic"),
        ("🐯", "Tiger", 4, "Epic"),
        ("🐻", "Bear", 4, "Epic"),
        ("🦈", "Shark", 4, "Epic"),
        # Rare - Value 3
        ("🍕", "Pizza", 3, "Rare"),
        ("🍔", "Burger", 3, "Rare"),
        ("🌮", "Taco", 3, "Rare"),
        ("🍣", "Sushi", 3, "Rare"),
        # Uncommon - Value 2
        ("🌵", "Cactus", 2, "Uncommon"),
        ("🍄", "Mushroom", 2, "Uncommon"),
        ("🌻", "Sunflower", 2, "Uncommon"),
        ("🌲", "Pine", 2, "Uncommon"),
        # Common - Value 1
        ("🧦", "Sock", 1, "Common"),
        ("📎", "Paperclip", 1, "Common"),
        ("🧱", "Brick", 1, "Common"),
        ("🧻", "Toilet Paper", 1, "Common"),
    ]

    # Create 2 of each card for a 40-card deck
    deck = []
    for char, name, val, tier in card_data:
        deck.append(EmojiCard(char, name, val, tier))
        deck.append(EmojiCard(char, name, val, tier))

    return deck


def play_war_game():
    print("--- ⚔️  STARTING EMOJI WAR ⚔️  ---")
    deck = create_deck()
    random.shuffle(deck)

    # Split deck
    player1_deck = deck[:20]
    player2_deck = deck[20:]

    round_num = 1
    max_rounds = 1000  # Safety break to prevent infinite loops

    while player1_deck and player2_deck and round_num <= max_rounds:
        # Check if players have cards to play
        if not player1_deck or not player2_deck:
            break

        p1_card = player1_deck.pop(0)
        p2_card = player2_deck.pop(0)

        print(f"\nRound {round_num}:")
        print(f"P1 plays {p1_card} vs P2 plays {p2_card}")

        pot = [p1_card, p2_card]

        # Resolution logic
        winner = None

        if p1_card.value > p2_card.value:
            winner = "P1"
        elif p2_card.value > p1_card.value:
            winner = "P2"
        else:
            print("   👉 It's a WAR! ⚔️")
            # War logic
            # Each player needs at least 2 cards to do a war (1 face down, 1 face up)
            # If they don't have enough, they lose immediately.
            if len(player1_deck) < 2 or len(player2_deck) < 2:
                if len(player1_deck) < 2 and len(player2_deck) < 2:
                    print("   Both ran out of cards during war! It's a draw.")
                    return
                elif len(player1_deck) < 2:
                    winner = "P2"
                else:
                    winner = "P1"
            else:
                # Add face down cards
                pot.append(player1_deck.pop(0))
                pot.append(player2_deck.pop(0))

                # Add face up war cards
                p1_war_card = player1_deck.pop(0)
                p2_war_card = player2_deck.pop(0)

                pot.append(p1_war_card)
                pot.append(p2_war_card)

                print(f"   [War] P1 reveals {p1_war_card} vs P2 reveals {p2_war_card}")

                if p1_war_card.value > p2_war_card.value:
                    winner = "P1"
                elif p2_war_card.value > p1_war_card.value:
                    winner = "P2"
                else:
                    # If tie again, just split pot to prevent infinite recursion complexity in this simple example
                    winner = "Tie"

        # Distribute winnings
        if winner == "P1":
            player1_deck.extend(pot)
            print(f"   ✅ Player 1 wins the round! (Deck: {len(player1_deck)})")
        elif winner == "P2":
            player2_deck.extend(pot)
            print(f"   ✅ Player 2 wins the round! (Deck: {len(player2_deck)})")
        else:
            # In a double tie/complex scenario, return cards to owners to keep game moving
            mid = len(pot) // 2
            player1_deck.extend(pot[:mid])
            player2_deck.extend(pot[mid:])
            print("   Draw round. Cards returned.")

        round_num += 1

    print("\n--- 🏁 GAME OVER 🏁 ---")
    if len(player1_deck) > len(player2_deck):
        print(f"🏆 Player 1 Wins with {len(player1_deck)} cards!")
    elif len(player2_deck) > len(player1_deck):
        print(f"🏆 Player 2 Wins with {len(player2_deck)} cards!")
    else:
        print("🤝 It's a Draw!")


if __name__ == "__main__":
    play_war_game()
