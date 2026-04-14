import fillerWordsDB
import re

def countFillerWords (speech : str):
    count = 0
    for fillerWord in fillerWordsDB.FILLER_WORDS:
        count += speech.lower().count(fillerWord)
    return count

def speechSpeedRating (speech : str, timeSec : int):
    wordCount = speech.split(" ").len() - countFillerWords(speech) # Excludes filler words
    speed = wordCount / timeSec * 60
    rating = ""
    match speed:
        case num if num < fillerWordsDB.WORDS_PER_MINUTE_THRESHOLD[0]:
            rating = "Too slow"
        case num if num < fillerWordsDB.WORDS_PER_MINUTE_THRESHOLD[1]:
            rating = "Slow"
        case num if num < fillerWordsDB.WORDS_PER_MINUTE_THRESHOLD[2]:
            rating = "Average"
        case num if num < fillerWordsDB.WORDS_PER_MINUTE_THRESHOLD[3]:
            rating = "Fast"
        case _:
            rating = "Too fast"
    return rating

def sentenceLengthRating (speech : str):
    wordCount = speech.split(" ").len()
    sentenceCount = re.split(". | ? | !", speech).len()
    speed = wordCount / sentenceCount
    rating = ""
    match speed:
        case num if num < fillerWordsDB.SENTENCE_LENGTH_THRESHOLD[0]:
            rating = "Slow"
        case num if num < fillerWordsDB.SENTENCE_LENGTH_THRESHOLD[0]:
            rating = "Average"
        case _:
            rating = "Fast"
    return rating

def clauseLengthRating (speech : str):
    wordCount = speech.split(" ").len()
    clauseCount = re.split(", | . | ; | ? | !", speech).len()
    speed = wordCount / clauseCount
    rating = ""
    match speed:
        case num if num < fillerWordsDB.CLAUSE_LENGTH_THRESHOLD[0]:
            rating = "Slow"
        case num if num < fillerWordsDB.CLAUSE_LENGTH_THRESHOLD[0]:
            rating = "Average"
        case _:
            rating = "Fast"
    return rating


def wordFrequency (speech : str):