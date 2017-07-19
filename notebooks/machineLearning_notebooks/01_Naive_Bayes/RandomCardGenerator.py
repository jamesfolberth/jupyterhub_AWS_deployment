import random


class Card():

    def __init__(self):
        
        faces = {11: "Jack", 12: "Queen", 13: "King"}
        suits = {1: "Spades", 2: "Hearts", 3: "Diamonds", 4: "Clubs"}

        cardnum = random.randint(1,13)
        suitnum = random.randint(1,4)
        
        self.number = faces.get(cardnum, cardnum)
        self.suit   = suits[suitnum]
        
    def getColor(self):
        
        colors = {"Spades" : "Black", "Clubs" : "Black", "Diamonds" : "Red", "Hearts" : "Red"}
        
        return colors.get(self.suit)
    
    
class Hand():

    def __init__(self,size):
        
        self.size  = size
        self.cards = []
        
        i = 0
        
        while i < size:

            c = Card()
            self.cards.append(c)
            i = i+1
            
            for j in range(i-1):
                if self.cards[j].number == self.cards[i-1].number:
                    if self.cards[j].suit == self.cards[i-1].suit:
                        self.cards.remove(self.cards[i-1])
                        i = i-1
    

def HandTuple( hand ):
    
    handList = []
    
    for card in hand.cards:
        tup = (card.number,card.suit)
        handList.append(tup)
        
    return handList

        
c = Card()

print(c.number)
print(c.getColor())
print(c.suit)

H = Hand(40)

print( HandTuple( H ) )

