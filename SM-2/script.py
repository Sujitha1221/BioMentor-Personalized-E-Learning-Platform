from flashcards import Card, run_cards, load_cards_from_csv
from review_quality_rating import word_accuracy  # Importing the function
import datetime

def review_card(card):
    """Review a card and calculate quality based on user input."""
    print(f"\nFront: {card.top}")
    
    # Prompt the user to type the answer
    user_input = input("Enter your answer: ").strip()
    
    # Calculate quality based on the word accuracy function
    quality = word_accuracy(card.bot, user_input)
    print(f"Calculated quality rating: {quality}")
    print(f"Actual Vocabulary: {card.bot}")
    
    return quality


if __name__ == "__main__":
    now = datetime.datetime.now()

    # Load cards from the vocabulary CSV file
    csv_path = "data/vocabulary.csv"
    cards = load_cards_from_csv(csv_path)

    # Simulate spaced repetition for 10 days
    for day in range(10):
        print(f"\nDay {day + 1}: Reviewing cards on {now.strftime('%Y-%m-%d')}")
        review_log = run_cards(cards, now, review_card, max_reviews=5, max_new=5, randomize=True)
        
        # Show daily review log
        print("\nDaily Review Log:")
        for entry in review_log:
            print(f" - {entry}")

        # Simulate the passing of a day
        now += datetime.timedelta(days=1)

        # Display the updated state of all cards
        print("\nUpdated Card States:")
        for card in cards:
            print(card)
