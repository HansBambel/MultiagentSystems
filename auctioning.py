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
    for i, item in enumerate(itemStartingprice):
        print(f'Startingprice: {item}')
        print(f'bids: {bids[:, i]}')
        average = np.mean(bids[:, i])
        print(f'average: {average}')
        # belowAverage = np.where(bids[:, i] < average)[0]
        sortedBids = sorted(bids[:, i][bids[:, i] < average])
        print(sortedBids)
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winnerToPay = sortedBids[-2]
        # TODO winner pays only second highest
        # maybe sort and look at the highest two below average
        print(f'winner: {winnerInd} with bid: {winner},' +
              f'to Pay: {winnerToPay}, profit: {average - winnerToPay}')


def updateBiddingFactor(biddingFactor):
    """Standard bidding strategy update

    After each auction over item m offered by seller k where
    buyer n participated the value of the bidding factor is updated
    (standard bidding strategy)
    """

    # Calculate new biddingfactor
    return biddingFactor


def assignItemToSeller(S, M):
    """Every seller gets assigned a random itemtype

    There are M types of items to be auctioned. In the beginning of
    the simulation each of the sellers is randomly assigned with
    the item m element of M, which it will auction across all the rounds.
    Note that multiple sellers might sell item m of the same type.
    """
    mapping = []
    for i in range(M):
        mapping.append(np.random.uniform([0, M, 1]))
    return mapping


def computeMarketPrice(bids):
    """Calculate current market price.

    Once all the bids are placed, a market price is computed as
    an average of the placed bids (amount of buyers).

    Returns:
    For every item, over every seller of this item, the average value
    of the item (type).
    """
    pass


def initBiddingFactor(amountRounds, amountBuyers, amountSellers):
    """Generate initial bidding factor

    The initial bidding factor is not generated for every round
    because it persists between rounds. The updateBiddingFactor
    function handles the updating.
    """
    biddingFactorAlpha = np.random.uniform(1.0, 1.9,
                                           size=(R, N, K))  # I dont know how to use the thing but R wil not be needed
    return biddingFactorAlpha


def assignPriceToItem(S):
    """Every seller assigns a price to its item"""
    return None


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

    sellerItem = assignItemToSeller(S, M)
    valueItem = assignPriceToItem(S)

    # lowerDelta = np.random.uniform(0.5, 1.0, size=N)
    # higherDelta = np.random.uniform(1.0, 1.5, size=N)

    biddingFactor = initBiddingFactor(N, K)

    for auctionRound in range(R):
        print(auctionRound)
        biddingFactor = auctionItems(valueItem[auctionRound],
                                     biddingFactor)
