import numpy as np


def auctionItems(itemStartingprice, biddingFactorAlpha):
    """A round of auctions

    It needs to return after every iteration (round) the values needed
    to return or are persisted between rounds as they are fed in back
    into the function.

    Parameters:
    itemStartingprice -- array of itemprices for every seller
    biddingFactorAlpha --

    Returns:
    (new starting price, new bidding factors,
     total buyer profit, total seller profit, market history)

    """
    bids = biddingFactorAlpha * itemStartingprice
    # NOTE auctions take place one item at a time
    winners = []
    for i, item in enumerate(itemStartingprice):
        print(f'Startingprice: {item}')
        print(f'bids: {bids[:, i]}')
        average = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < average])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        # winner pays only second highest
        winnerToPay = sortedBids[-2]
        # TODO update biddingfactor for all buyers (for now moved out of this function)
        # NOTE: in "pure" auctions update only if buyer has not won yet
        # --> (because if a buyer has won he does not bid anymore)
        # TODO check whether buyer wants to revoke previous won item (need penalty here)
        # --> seller gets penalty (profit + penalty), but profit of previous sell needs to be deducted
        print(f'winner: {winnerInd} with bid: {winner},' +
              f'to Pay: {winnerToPay}, profit: {average - winnerToPay}')
    return winners


def updateBiddingFactor(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta):
    """Standard bidding strategy update

    After each auction over item m offered by seller k where
    buyer n participated the value of the bidding factor is updated
    (standard bidding strategy)
    After each auction over item m offered by seller k where buyer n
    participated value of the bidding factor is updated:
    where ∆ n – a bid decrease factor of buyer n (∆ n ≤ 1), and ∆ n – is a bid increase factor of buyer n (∆ n ≥ 1). The bid
    factors are set per buyer once per simulation. This way the bids of the buyer n are going to adapt to results of
    auctions organized by seller k for a particular item m.
    """

    # Calculate new biddingfactor
    # if won: use lowerDelta, else: higherDelta
    return biddingFactor


def assignItemToSeller(S, M):
    """Every seller gets assigned a random itemtype

    There are M types of items to be auctioned. In the beginning of
    the simulation each of the sellers is randomly assigned with
    the item m element of M, which it will auction across all the rounds.
    Note that multiple sellers might sell item m of the same type.
    """
    return np.random.randint(low=0, high=M, size=S)


def computeMarketPrice(bids, i):
    """Calculate current market price.

    Once all the bids are placed, a market price is computed as
    an average of the placed bids (amount of buyers).

    Returns:
    For every item, over every seller of this item, the average value
    of the item (type).
    """
    return np.mean(bids[:, i])


def initBiddingFactor(amountBuyers, amountSellers):
    """Generate initial bidding factor

    The initial bidding factor is not generated for every round
    because it persists between rounds. The updateBiddingFactor
    function handles the updating.
    """
    # biddingfactor is 2 dimensional
    biddingFactorAlpha = np.random.uniform(low=1.0, high=1.9,
                                           size=(amountBuyers, amountSellers))  # I dont know how to use the thing but R wil not be needed
    return biddingFactorAlpha


def assignPriceToItem(sellerItems, numRounds, maxPrice):
    """Every seller assigns a price to its item"""
    itemPrices = np.random.uniform(size=(numRounds, len(sellerItems)), low=0, high=maxPrice)
    return np.round(itemPrices, decimals=2)


def rearangeArray(array, indices):
    return [array[i] for i in indices]


def restoreOriginalOrder(array, orderedInd):
    out = []
    for i in range(len(array)):
        ind = np.where(orderedInd == i)[0][0]
        out.append(array[ind])
    return out


btypes = ['default']


def auctionSimulation(M, K, N, R, Smax, penalty,
                      pure=True, biddingtype=btypes[0]):
    """Full auction simulation function

    Parameters:
    M -- The amount of types of items
    K -- The amount of sellers
    N -- The amount of buyers
    R -- The amount of bidding rounds
    Smax -- Maximum starting price
    penalty -- Penalty factor for calculating penalties when selling back
    pure -- Boolean if the auction allows selling back
    biddingtype -- Set the type of bidding factor calculation

    Returns:
    A three tuple containing
    rStats -- Statistics of market price development
    rSellerProfit -- Profits for every seller
    rBuyersProfit -- Profits for every buyer
    """
    if N < K:
        print('Error: must be more buyers than sellers')

    np.random.seed(42)
    rStats = []
    rSellerProfit = []
    rBuyersProfit = []

    seller2Items = assignItemToSeller(K, M)
    valueItems = assignPriceToItem(seller2Items, R, Smax)
    lowerDelta = np.random.uniform(0.5, 1.0, size=N)
    higherDelta = np.random.uniform(1.0, 1.5, size=N)

    biddingFactorHistory = []
    biddingFactor = initBiddingFactor(N, K)
    biddingFactorHistory.append(biddingFactor)
    for auctionRound in range(R):
        print(auctionRound)
        print(f'biddingFactor: {biddingFactor}')
        print(f'valueItems: {valueItems[auctionRound]}')
        # randomize order of sold items
        auctionItemOrderInd = np.random.permutation(np.arange(K))
        print(auctionItemOrderInd)
        auctionItemOrder = rearangeArray(valueItems[auctionRound], auctionItemOrderInd)
        # adapt to the biddingFactors to the order the items are sold
        biddingFactorOrder = np.array([rearangeArray(i, auctionItemOrderInd) for i in biddingFactor])
        # print(biddingFactor)
        # print(f'{biddingFactorOrder}')
        winners = auctionItems(auctionItemOrder,
                               biddingFactorOrder)

        updateBiddingFactor(biddingFactor, winners, auctionItemOrderInd, lowerDelta, higherDelta)
        biddingFactorHistory.append(biddingFactor)


auctionSimulation(6, 3, 10, 8, 100, 5)
