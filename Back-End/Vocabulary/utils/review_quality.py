from rapidfuzz.distance.Levenshtein import distance

def word_accuracy(original_word, entered_word):
    """
    Calculate the accuracy score between two words using Levenshtein distance.

    Parameters:
    - original_word (str): The correct word.
    - entered_word (str): The word entered by the user.

    Returns:
    - int: Accuracy score between 0 (worst) and 5 (best).
    """
    
    # Handle empty cases
    if not original_word or not entered_word:
        return 0  # If the answer is empty, give the lowest score
    
    # Normalize the words by converting to lowercase and stripping spaces
    original_word = original_word.lower().strip()
    entered_word = entered_word.lower().strip()

    # Calculate Levenshtein distance
    max_length = max(len(original_word), len(entered_word))

    # If both are empty after stripping, return max score
    if max_length == 0:
        return 5

    edit_distance = distance(original_word, entered_word)

    # Calculate similarity percentage
    similarity = (max_length - edit_distance) / max_length

    # Scale similarity to 0-5
    if similarity >= 0.95:
        return 5
    elif similarity >= 0.85:
        return 4
    elif similarity >= 0.70:
        return 3
    elif similarity >= 0.50:
        return 2
    elif similarity >= 0.30:
        return 1
    else:
        return 0  # Too different, return lowest score

# ✅ **Test Cases**
test_cases = [
    ("biology", "biology"),   # Expected: 5 (Exact match)
    ("biology", "biolog"),    # Expected: 4 (Small typo)
    ("biology", "biolgy"),    # Expected: 3 (One letter swap)
    ("biology", "bio"),       # Expected: 2 (Partial match)
    ("biology", "chemistry"), # Expected: 0 (Completely different)
    ("hello", ""),            # Expected: 0 (Empty answer)
    ("", ""),                 # Expected: 5 (Both empty)
]

for original, entered in test_cases:
    print(f"Original: {original}, Entered: {entered}, Score: {word_accuracy(original, entered)}")
