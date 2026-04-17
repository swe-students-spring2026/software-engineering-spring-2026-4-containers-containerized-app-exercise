import re
from collections import Counter
import analysisDB


def count_filler_words (speech : str):
    count = 0
    for filler_word in analysisDB.FILLER_WORDS:
        count += speech.lower().count(filler_word)
    return count

def speech_speed_rating (speech : str, time_sec : int):
    word_count = len(speech.split(" ")) - count_filler_words(speech) # Excludes filler words
    speed = word_count / time_sec * 60
    rating = ""
    match speed:
        case num if num < analysisDB.WORDS_PER_MINUTE_THRESHOLD[0]:
            rating = "Too slow"
        case num if num < analysisDB.WORDS_PER_MINUTE_THRESHOLD[1]:
            rating = "Slow"
        case num if num < analysisDB.WORDS_PER_MINUTE_THRESHOLD[2]:
            rating = "Average"
        case num if num < analysisDB.WORDS_PER_MINUTE_THRESHOLD[3]:
            rating = "Fast"
        case _:
            rating = "Too fast"
    return rating

def sentence_length_rating (speech : str):
    word_count = len(speech.split(" "))
    sentence_count = len(re.split(r"[.?!]", speech))
    speed = word_count / sentence_count
    rating = ""
    match speed:
        case num if num < analysisDB.SENTENCE_LENGTH_THRESHOLD[0]:
            rating = "Slow"
        case num if num < analysisDB.SENTENCE_LENGTH_THRESHOLD[1]:
            rating = "Average"
        case _:
            rating = "Fast"
    return rating

def clause_length_rating (speech : str):
    word_count = len(speech.split(" "))
    clause_count = len(re.split(r"[,.;?!]", speech))
    speed = word_count / clause_count
    rating = ""
    match speed:
        case num if num < analysisDB.CLAUSE_LENGTH_THRESHOLD[0]:
            rating = "Slow"
        case num if num < analysisDB.CLAUSE_LENGTH_THRESHOLD[1]:
            rating = "Average"
        case _:
            rating = "Fast"
    return rating


def word_frequency (speech : str, top_n : int = 10,
                    min_word_length : int = 3,
                    phrase_lengths : list[int] = [2,3],
                    threshold : int = 3):
    cleaned = re.sub(r"[^\w\s]", "", speech.lower())
    tokens = cleaned.split()
    filtered_tokens = [
        t for t in tokens
        if t not in analysisDB.STOP_WORDS and len(t) >= min_word_length
    ]
    word_counts = Counter(filtered_tokens)
    overused_words = [
        (word, count)
        for word, count in word_counts.most_common(top_n)
        if count >= threshold
    ]
    raw_tokens = cleaned.split()

    overused_phrases: dict[int, list[tuple[str, int]]] = {}
    for n in phrase_lengths:
        ngrams = [
            " ".join(raw_tokens[i : i + n])
            for i in range(len(raw_tokens) - n + 1)
        ]

        # This only keeps phrases that are not entirely stop words
        meaningful_n_grams = [
            phrase for phrase in ngrams
            if any(
                w not in analysisDB.STOP_WORDS and len(w) >= min_word_length
                for w in phrase.split()
            )
        ]
        phrase_counts = Counter(meaningful_n_grams)
        top_phrases = [
            (phrase, count)
            for phrase, count in phrase_counts.most_common(top_n)
            if count >= threshold
        ]

        if top_phrases:
            overused_phrases[n] = top_phrases

    return {
        "overused_words": overused_words,
        "overused_phrases": overused_phrases,
    }
