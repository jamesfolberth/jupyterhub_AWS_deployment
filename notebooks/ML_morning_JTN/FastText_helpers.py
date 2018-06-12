from typing import List, Tuple
import math
import vectors as v
from vectors import Vector


class Word:
    def __init__(self,text:str,vector:Vector) -> None:
        self.text = text
        self.vector = vector
        
def vector_len(v: Vector) -> float:
    return math.sqrt(sum([x*x for x in v]))

def dot_product(v1: Vector, v2: Vector) -> float:
    assert len(v1) == len(v2)
    return sum([x*y for (x,y) in zip(v1, v2)])

def cosine_similarity(v1: Vector, v2: Vector) -> float:
    #Returns the cosine of the angle between the two vectors.
    #Results range from -1 (very different) to 1 (very similar).
    return dot_product(v1, v2) / (vector_len(v1) * vector_len(v2))

def sorted_by_similarity(words: List[Word], base_vector: Vector) -> List[Tuple[float, Word]]:
    #Returns words sorted by cosine distance to a given vector, most similar 
    #first"""
    words_with_distance = [(cosine_similarity(base_vector,w.vector), w) for w in words]
    # We want cosine similarity to be as large as possible (close to 1)
    return sorted(words_with_distance, key=lambda t: t[0], reverse=True)

def print_related(words: List[Word], text: str) -> None:
    base_word = find_word(words,text)
    sorted_words = [
        word.text for (dist, word) in
            sorted_by_similarity(words, base_word.vector)
            if word.text.lower() != base_word.text.lower()
        ]
    print(', '.join(sorted_words[:7]))
    

def print_related_str(words: List[Word], text: str) -> str:
    base_word = find_word(words,text)
    sorted_words = [
        word.text for (dist, word) in
            sorted_by_similarity(words, base_word.vector)
            if word.text.lower() != base_word.text.lower()
        ]
    return ', '.join(sorted_words[:7])
    
#def find_word(words: List[Word], text: str) -> Word:
#    return next(w for w in words if text == w.text)
#### modified 5-25-18 by JTN
def find_word(words: List[Word], text: str) -> Word:
    a = next((w for w in words if text == w.text),"exhausted")
    if a == "exhausted":
        print(text + " was not found in the library. Please try another word")
        return None 
    else:
        return a

def closest_analogies(
    left2: str, left1: str, right2: str, words: List[Word]
) -> List[Tuple[float, Word]]:
    word_left1 = find_word(words,left1)
    word_left2 = find_word(words,left2)
    word_right2 = find_word(words,right2)
    vector =  v.add(
        v.sub(word_left1.vector, word_left2.vector),
        word_right2.vector)
    closest = sorted_by_similarity(words, vector)[:10]
    def is_redundant(word: str) -> bool:
        #Sometimes the two left vectors are so close the answer is e.g.
        #"shirt-clothing is like phone-phones". Skip 'phones' and get the next
        #suggestion, which might be more interesting.
        return (
            left1.lower() in word.lower() or
            left2.lower() in word.lower() or
            right2.lower() in word.lower())
    return [(dist, w) for (dist, w) in closest if not is_redundant(w.text)]

def print_analogy(left2: str, left1: str, right2: str, words: List[Word]) -> None:
    analogies = closest_analogies(left2, left1, right2, words)
    if (len(analogies) == 0):
        print(f"{left2}-{left1} is like {right2}-?")
    else:
        (dist, w) = analogies[0]
        print(f"{left2} is to {left1} as {right2} is to {w.text}")
