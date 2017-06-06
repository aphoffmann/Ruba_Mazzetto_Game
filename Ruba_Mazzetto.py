# CS1210 HW5
# Alex Hoffmann

from random import randint

######################################################################
# createDeck() produces a new, cannonically ordered, 40 card deck.
# Uses a nested comprehension; deviates a bit from the specification
# because it allows one to specify a different size deck. In other
# words, createDeck(13) would create a standard 52-card deck (with J,
# Q, K denoted 11, 12, 13).
def createDeck(N=10, S=('spades', 'hearts', 'clubs', 'diamonds')):
    return([ (v, s) for s in S for v in range(1, N+1) ])

# Fisher-Yates-Knuth fair shuffle. Faster and fairer than riffle(), so
# we may as well use this one! Corrected so as not to create a default
# deck D, which would otherwise be built once and then consumed,
# making it unavailable for subsequent games.
def shuffle(D):
    i = len(D)-1
    while i > 0:
        j = randint(0, i)
        D[i], D[j] = D[j], D[i]
        i = i-1
    return(D)
    
######################################################################
# Construct the representation of a given card using special unicode
# characters for hearts, diamonds, clubs, and spades.
def displayCard(c):
    suits = {'spades':'\u2660', 'hearts':'\u2661', 'diamonds':'\u2662', 'clubs':'\u2663'}
    return(''.join( [ str(c[0]), suits[c[1]] ] ))

######################################################################
# Print out an indexed list of the cards in input list H, representing
# a hand.
def showHand(H):
    print('\nMy hand: {}'.format(', '.join([ "[{}] {}".format(i, displayCard(H[i])) for i in range(len(H)) ] )))

# Print out an indexed representation of the state of the table,
# including any player stashes and the cards laid on the table. Uses a
# nested set of string format expressions, with the outer one joining
# individual sets of format expressions.
def showTable(N, T, P):
    print('Stash: {}\nTable: {}'.format(', '.join([ "[Player {}] {} (*{})".format(j, displayCard(P[j][-1]), len(P[j])) for j in sorted(P.keys()) ] ),
                                        ', '.join([ "[{}] {}".format(j+N, displayCard(T[j])) for j in range(len(T)) ] )))

######################################################################
# Deal 3 cards, or as many as you can, to each of the N players from
# the deck. Also, update the table so that it has 4 cards if it
# currently has fewer. We'll use try/except to catch the condition
# when we try to pop from an empty deck so we can exit gracefully.
def deal(N, D, T, H):
    try:
        # Three cards...
        for j in range(3):
            # ...to each player...
            for i in range(N):
                H[i].append(D.pop())
        # ...plus a few more to the table, as necessary.
        while len(T) < 4:
            T.append(D.pop())
    except:
        print("Ooops! ran out of cards.")
    return (D, T, H)

######################################################################
# Return (c, M) where c is an index into H[i] and M is either [] (in
# which case we discard c to table), or a list of indexes in range(0,
# N+len(T)) except for i.
def getMove(i, N, H, T, P):
    # Recursive helper function that explores the combinatorial space
    # of possible moves. Let c be the card you are seeking to match,
    # and v represent the remaining value you need to match
    # (initially, the value on card c), j represent the index (into
    # stashes and/or table) of the card you are currently considering
    # adding to the move, M represent the move under construction, and
    # L the collection of legal moves found so far.
    
    #collect cards from stash and table into one list.
    #(P[j][-1][0], j) == (card value, stash index)
    #(T[j][0], j+N) == (card value, table index)
    cards = [(P[j][-1][0], j) for j in P.keys() if j != i]
    cards.extend([(T[j][0], j+N) for j in range(len(T))])
    def helper(c, v, j, M, L):
        '''Explores tree from left to right trying to find legal mooves'''
        # if v == 0 append legal moves to L
        if v == 0:
            L.append((c, M))
            return(L)
        # if j == maxDepth, take step back in recursion
        elif j >= len(cards):
            return(L)
        #traverse left and right searching for legal mooves
        else:            
            #go left
            L = helper(c, v, j+1, M, L)
            #go right if legal
            if v >= cards[j][0] and cards[j][1] not in M:
                L = helper(c, v - cards[j][0], j, M+[cards[j][1]], L)
        return(L)
        # Done. Return legal moves found so far.
            
            
    # Human player; solicit move interactively.
    if i == 0: 
        return(pickMove(i, N, H, T, P))
    # Autplayer for player i. Search combinations for legal moves for
    # every card c in H[i].
    L = []
    for c in range(len(H[i])):
        L = helper(c, H[i][c][0], 0, [], L)
    
    # No legal moves?
    if not L:
        # L is still [] (no matches); discard a random card.
        return((randint(1, len(H[i]))-1, []))

    # Return the "largest" match. There could better heuristics here
    # that depend on, e.g., the sizes of the constituent piles.
    return( max(L, key=lambda x: len(x[1])) )

######################################################################
# Return (c, M) where c is an index into H[i] and M is either [] (in
# which case we discard c to table), or a list of indexes in range(0,
# N+len(T)) except for i.
def pickMove(i, N, H, T, P):
    '''interprets human move and checks legality'''
    # Human player gets to see his/her hand.
    showHand(H[i])

    # Prompt player i for card to play from H[i].
    while True:
        # Capture any errors from non-integer inputs.
        try:
            #takes input c and converts to int
            #checks if c is and index in Hand i
            c = int(input('Play which card? '))
            if c in range(len(H[i])):
                break


        except:
            pass

    # Prompt player i for list of indeces to match.
    while True:
        # Capture any errors from non-integer inputs.
        try:
            #take input
            userInput = input('Select matching indices separated by spaces (blank to discard): ')
            #discard c
            if userInput == '':
                M = []
                break
            
            #convert input to list of indices
            M = [int(j) for j in userInput.split(' ')]
            
            #Keep Player from choosing own stash
            if 0 in M:
                continue
            
            #collect card values into list of ints count1
            count1 = [T[j-N][0] for j in M if j >= N]
            count1.extend([P[j][-1][0] for j in M if j < N])
            
            #check if it's a legal move, continue if not
            if sum(count1) == H[i][c][0]:
                break
            else:
                continue
        
        #catch any user errors
        except:
            pass         
    # Done.
    return((c, M))

######################################################################
# Governs game play for N players (2 by default) using an K-card deck
# (40 by default). Refactored for simplicity from version of HW4.
def play(N=2, K=10):
    # Corrected so that we can play multiple games without resetting
    # the Python session. As originally written, shuffle() creates a
    # default deck as its argument which is consumed (and not reset)
    # the first time you play.
    D = shuffle(createDeck(K))     # Create a deck
    T = []                         # Table top
    H = [ [] for i in range(N) ]   # Player hands
    P = { }                        # Player piles i:(c, n)
    # Record last player to steal a stash or take a card from T
    last = None			   # Used at end of game.

    # Play a game.
    while D:
        # Deal cards and (re)populate the table.
        print("\n=========\nDealing...")
        D, T, H = deal(N, D, T, H)

        # While the first player has any cards...
        while H[0]:
            # For each player.
            for i in range(0, N):
                # We need to check to make sure player i has something
                # left to play in case there was an funny distribution
                # of cards. Because of how we dealt the card, as soon
                # as player i runs out of cards, the remaining players
                # >i will have done so as well.
                if not H[i]:
                    break
 
                # Good to go. Show the state of the game from player 0 perspective
                # (i.e., do not reveal player i's hand, because player 0 is watching).
                print("\n=========\nPlayer {}:".format(i))
                showTable(N, T, P)
              
                # Manage move selection.
                (c, M) = getMove(i, N, H, T, P)

                # Execute the move (c, M).
                if not M:
                    # M is []: discard card c.
                    print("Player {} adds {} to table".format(i, displayCard(H[i][c])))
                    T.append(H[i].pop(c))
                else:
                    # M is a list of indexes describing a combination
                    # of cards on table or other player's
                    # stashes.
                    print("Player {} plays {} and...".format(i, displayCard(H[i][c])))

                    # Player i is last to take a trick (for distribution
                    # of remaining table cards at end of game).
                    last = i

                    # Execute the move.
                    while M:
                        j = M.pop()
                        if j < N:
                            # Stealing player j's stash.
                            print("...steals Player {} stash {}".format(j, displayCard(P[j][-1])))
                            if i in P:
                                P[i].extend(P[j])
                            else:
                                P[i] = P[j]
                            # Clear player j's stash.
                            del P[j]
                        else:
                            # Add table card t to player i stash if it exists (else create it).
                            print("...takes {} from table".format(displayCard(T[j - N])))
                            if i in P:
                                P[i].append(T.pop(j - N))
                            else:
                                P[i] = [ T.pop(j - N) ]
                    # Append matching card from player i hand to top of stash.
                    P[i].append(H[i].pop(c))

    # Game over. Assign remaining cards from table to player who took
    # the last trick (= last).
    if ( T ):
        print("Done: awarding {} from table to Player {}".format(', '.join([ displayCard(c) for c in T ]), last))
        if last in P:
            P[last].extend(T)
        else:
            P[last] = T

    # Return player scores as dictionary.
    return({ p:sum( [ c[0] for c in P[p] ] ) for p in P })
