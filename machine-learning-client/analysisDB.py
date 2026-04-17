FILLER_WORDS = ["uh", "oh", "like", "other", "you know"]
WORDS_PER_MINUTE_THRESHOLD = [100, 120, 170, 240] # Intervals: Too slow, slow, average, fast, too fast
SENTENCE_LENGTH_THRESHOLD = [10, 25] # Intervals: Short, average, long
CLAUSE_LENGTH_THRESHOLD = [5, 10] # Intervals: Short, average, long
STOP_WORDS = [
  "a", "an", "the", "this", "that", "these", "those",

  "and", "but", "or", "for", "nor", "so", "yet", "at", "in", "on", "to", "from", "by", "of",

  "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",

  "is", "was", "were", "are", "am", "be", "been", "being", "do", "does", "did", "has", "have", "had"
]