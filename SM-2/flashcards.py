import datetime
import math
import random
import itertools
import csv

# Define the time format for consistent display
time_fmt = "%Y-%m-%d"

class Card:
    """
    Represents a single flashcard used in spaced repetition.
    Attributes:
        - top: The front side of the card (e.g., question, term).
        - bot: The back side of the card (e.g., answer, definition).
        - time: The last review time.
        - repetitions: Number of successful repetitions.
        - interval: Days until the next review.
        - easiness: Easiness factor (affects interval growth).
    """
    def __init__(self, top, bot, time, repetitions=0, interval=1, easiness=2.5):
        self.top = top
        self.bot = bot
        self.time = time.replace(second=0, microsecond=0)
        self.repetitions = repetitions
        self.interval = interval
        self.easiness = easiness

    @property
    def is_new(self):
        """Determine if the card is new (has not been reviewed yet)."""
        return self.repetitions == 0

    @property
    def next_time(self):
        """Calculate the next review date based on the current interval."""
        return self.time + datetime.timedelta(days=math.ceil(self.interval))

    def repeat(self, quality, time):
        """
        Update the card's state using the SM-2 algorithm.
        Parameters:
            - quality: Review quality (0-5) based on user performance.
            - time: The current datetime.
        """
        assert 0 <= quality <= 5, "Quality should be between 0 and 5."

        # Adjust easiness factor based on quality
        self.easiness = max(1.3, self.easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        if quality < 3:
            # If performance is poor, reset repetitions and interval
            self.repetitions = 0
            self.interval = 1
        else:
            # If performance is acceptable, increment repetitions
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1  # First repetition interval
            elif self.repetitions == 2:
                self.interval = 6  # Second repetition interval
            else:
                # Subsequent intervals grow based on easiness factor
                self.interval *= self.easiness

        # Update the review time
        self.time = time

    def __repr__(self):
        """Provide a human-readable representation of the card."""
        return (f"Card: {self.bot}, Next Review: {self.next_time.strftime(time_fmt)}, "
                f"Repetitions: {self.repetitions}, Interval: {self.interval:.2f}, Easiness: {self.easiness:.2f}")


def fetch_cards(cards, now, max_reviews=None, max_new=None, randomize=False):
    """
    Fetch cards for review based on their state and schedule.
    Parameters:
        - cards: List of all flashcards.
        - now: The current datetime.
        - max_reviews: Maximum number of scheduled reviews to fetch.
        - max_new: Maximum number of new cards to fetch.
        - randomize: Whether to shuffle the order of cards for review.
    Returns:
        - choose_next: Function to fetch the next card for review.
        - reject_card: Function to requeue cards for further review.
    """
    # Filter new cards and limit to max_new
    new_cards = list(itertools.islice((c for c in cards if c.is_new), max_new))
    new_cards.reverse()

    # Filter due cards for review and limit to max_reviews
    to_review = list(itertools.islice((c for c in cards if not c.is_new and c.next_time <= now), max_reviews))
    to_review.reverse()

    # Shuffle cards for randomness if required
    if randomize:
        random.shuffle(to_review)

    def choose_next():
        """Select the next card for review."""
        if to_review:
            return to_review.pop()
        elif new_cards:
            return new_cards.pop()
        return None  # No more cards available

    def reject_card(card):
        """Requeue the card for another review attempt."""
        if card.is_new:
            new_cards.insert(0, card)
        else:
            to_review.insert(0, card)

    return choose_next, reject_card


def run_cards(cards, now, review_card, max_reviews=None, max_new=None, randomize=False):
    """
    Execute the review process for the given cards.
    Parameters:
        - cards: List of all flashcards.
        - now: The current datetime.
        - review_card: Function to handle individual card review.
        - max_reviews: Maximum number of scheduled reviews.
        - max_new: Maximum number of new cards.
        - randomize: Whether to shuffle the review order.
    Returns:
        - log: A log of the review session with details for each card.
    """
    choose_next, reject_card = fetch_cards(cards, now, max_reviews, max_new, randomize)
    log = []

    while True:
        current = choose_next()
        if current is None:
            break  # No more cards to review

        # Review the current card and update its state
        quality = review_card(current)
        current.repeat(quality, now)
        log.append({
            "Card": current.top,
            "Quality": quality,
            "Next Review": current.next_time.strftime(time_fmt),
        })

    return log


def load_cards_from_csv(file_path):
    """
    Load flashcards from a CSV file.
    Parameters:
        - file_path: Path to the CSV file containing card data.
    Returns:
        - cards: List of Card objects.
    """
    cards = []
    now = datetime.datetime.now()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) < 2:
                continue  # Skip invalid rows
            # Adjusted to assume the first column is `bot` (answer) and the second is `top` (question)
            bot, top = row[0].strip(), row[1].strip()
            cards.append(Card(top, bot, now))

    return cards
