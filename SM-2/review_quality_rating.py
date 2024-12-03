from Levenshtein import distance

def word_accuracy(original_word, entered_word):
    """
    Calculate the accuracy score between two words.

    Parameters:
    - original_word (str): The correct word.
    - entered_word (str): The word entered by the user.

    Returns:
    - int: Accuracy score between 0 (worst) and 5 (best).
    """
    
    # Normalize the words by converting to lowercase
    original_word = original_word.lower()
    entered_word = entered_word.lower()

    # Calculate Levenshtein distance
    max_length = max(len(original_word), len(entered_word))
    if max_length == 0:  # Handle edge case where both strings are empty
        return 5

    edit_distance = distance(original_word, entered_word)

    # Calculate similarity percentage
    similarity = (max_length - edit_distance) / max_length

    # Scale the similarity to a score between 0 and 5
    scaled_score = round(similarity * 5)

    return max(0, min(scaled_score, 5))  # Ensure score is within bounds

# Example usage
original = "biology"
entered = ""
accuracy = word_accuracy(original, entered)
print(f"Accuracy score: {accuracy}")
