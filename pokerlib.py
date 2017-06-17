from random import shuffle

class Card:
    suits = ['s', 'h', 'd', 'c']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    def __init__(self, suit, rank):
        self.suit = suit  # suit of the card is stored as an integer that is the index of its real suit
        self.rank = rank  # rank of the card is stored as an integer that is the index of its real rank
    def __repr__(self):
        return Card.ranks[self.rank] + Card.suits[self.suit]

class Deck:
    def __init__(self):
        self.cards = []
        for sIndex in range(len(Card.suits)):
            for rIndex in range(len(Card.ranks)):
                self.cards.append(Card(sIndex, rIndex))
        shuffle(self.cards)
        self.cardsIter = iter(self.cards)
    def refresh(self):
        shuffle(self.cards)
        self.cardsIter = iter(self.cards)
    def draw(self):
        return next(self.cardsIter)

def sortCards(cards):
    return sorted(cards, key=lambda c: 10 * c.rank + c.suit)

def rateCards(cards):
    sortedCards = sortCards(cards)
    x = detectStraightFlush(sortedCards)
    if x >= 0:
        return 8 + x
    x = detectFourKind(sortedCards)
    if x >= 0:
        return 7 + x
    x = detectFullHouse(sortedCards)
    if x >= 0:
        return 6 + x
    x = detectFlush(sortedCards)
    if x >= 0:
        return 5 + x
    x = detectStraight(sortedCards)
    if x >= 0:
        return 4 + x
    x = detectThreeKind(sortedCards)
    if x >= 0:
        return 3 + x
    x = detectTwoPair(sortedCards)
    if x >= 0:
        return 2 + x
    x = detectPair(sortedCards)
    if x >= 0:
        return 1 + x
    return detectHigh(sortedCards)


#############################################################################
#############################################################################
#############################################################################

def detectStraightFlush(cards):
    lastCard = cards[0]
    count = 1
    for card in cards[1:]:
        if (card.rank-lastCard.rank==1) and (card.suit==lastCard.suit):
            count += 1
            if count == 5:
                return card.rank * 0.01
        else:
            count = 1
        lastCard = card
    return -1

def detectFourKind(cards):
    lastCard = cards[0]
    count = 1
    for card in cards[1:]:
        if card.rank==lastCard.rank:
            count += 1
            if count == 4:
                side = max([c.rank for c in cards if c.rank!=lastCard.rank])
                return card.rank * 0.01 + side * 0.0001
        else:
            count = 1
        lastCard = card
    return -1

def detectFullHouse(cards):
    ranks = [0]*len(Card.ranks)
    for card in cards:
        ranks[card.rank] += 1
    three = -1
    two = -1
    for i in range(len(ranks)):
        if ranks[i] >= 3:
            three = i
    for i in range(len(ranks)):
        if ranks[i] >= 2 and i != three:
            two = i
    if two >= 0 and three >= 0:
        return three * 0.01 + two * 0.0001
    return -1

def detectFlush(cards):
    suits = [0]*len(Card.suits)
    for card in cards:
        suits[card.suit] += 1
    if max(suits) >= 5:
        ofSuit = [c.rank for c in cards if c.suit == suits.index(max(suits))]
        retval = 0
        multiplier = 0.01
        for rank in ofSuit[-5:][::-1]:
            retval += rank * multiplier
            multiplier *= 0.01
        return retval
    return -1

def detectStraight(cards):
    lastCard = cards[0]
    count = 1
    for card in cards[1:]:
        if card.rank - lastCard.rank == 1:
            count += 1
            if count == 5:
                return card.rank * 0.01
        else:
            count = 1
        lastCard = card
    return -1

def detectThreeKind(cards):
    lastCard = cards[0]
    count = 1
    for card in cards[1:]:
        if card.rank == lastCard.rank:
            count += 1
            if count == 3:
                side1 = max([c.rank for c in cards if c.rank != card.rank])
                side2 = max([c.rank for c in cards if c.rank != card.rank and c.rank != side1])
                return card.rank * 0.01 + side1 * 0.0001 + side2 * 0.000001
        else:
            count = 1
        lastCard = card
    return -1

def detectTwoPair(cards):
    ranks = [0]*len(Card.ranks)
    for card in cards:
        ranks[card.rank] += 1
    pair1 = -1
    pair2 = -1
    for i in range(len(ranks)):
        if ranks[i] >= 2:
            pair1 = i
    for i in range(len(ranks)):
        if ranks[i] >= 2 and i != pair1:
            pair2 = i
    if pair1 >= 0 and pair2 >= 0:
        side = max([c.rank for c in cards if c.rank != pair1 and c.rank != pair2])
        return pair1 * 0.01 + pair2 * 0.0001 + side * 0.000001
    return -1

def detectPair(cards):
    lastCard = cards[0]
    for card in cards[1:]:
        if card.rank == lastCard.rank:
            side1 = max([c.rank for c in cards if c.rank != card.rank])
            side2 = max([c.rank for c in cards if c.rank != card.rank and c.rank != side1])
            side3 = max([c.rank for c in cards if c.rank != card.rank and c.rank != side1 and c.rank != side2])
            return card.rank * 0.01 + side1 * 0.0001 + side2 * 0.000001 + side3 * 0.00000001
        lastCard = card
    return -1

def detectHigh(cards):
    retval = 0
    multiplier = 0.01
    for card in cards[-5:][::-1]:
        retval += card.rank * multiplier
        multiplier *= 0.01
    return retval


#############################################################################
############################################################################# RUN
#############################################################################

# hand = [
#     Card(0, 2),
#     Card(1, 3),
#     Card(2, 5),
#     Card(3, 6),
#     Card(1, 6),
#     Card(2, 7),
#     Card(3, 8),
# ]
# print(rateCards(hand))

# d = Deck()
# for _ in range(10):
#     hand = []
#     for j in range(7):
#         hand.append(d.draw())
#     print(sortCards(hand), rateCards(hand))
#     d.refresh()
# print("--------------")
# d = Deck()
# while True:
#     hand = []
#     for j in range(7):
#         hand.append(d.draw())
#     x = rateCards(hand)
#     if x>=8:
#         print(sortCards(hand), x)
#         break
#     d.refresh()


