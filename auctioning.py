import numpy as np
import matplotlib.pyplot as plt
import sys

####################
# DEFAULT SETTINGS #
####################
numItems = 10
numSellers = 10
numBuyers = 20
numRounds = 20
maxStartingPrice = 100
penalty = 0.05
pure = False


#################################
# SIMULATION CORE FUNCTIONALITY #
#################################

def auctionSimulation(M, K, N, R, Smax, penalty=0.05,
                      pure=False):
    """Full auction simulation function

    Parameters:
    M -- The amount of types of items
    K -- The amount of sellers
    N -- The amount of buyers
    R -- The amount of bidding rounds
    Smax -- Maximum starting price
    penalty -- Penalty factor for calculating penalties when selling back
    pure -- Boolean if the auction allows selling back

    Returns:
    A three tuple containing
    rStats -- Statistics of market price development over rounds
    rSellerProfit -- Profits for every seller over rounds
    rBuyersProfit -- Profits for every buyer over rounds
    """
    if N <= K:
        raise ValueError(
            'Error: Number of Buyers needs to be bigger than number of Sellers')

    rMarketprices = [np.zeros(K)]
    rSellerProfit = [np.zeros(K)]
    rBuyerProfit = [np.zeros(N)]

    seller2Items = assignItemToSeller(K, M)
    valueItems = assignPriceToItem(seller2Items, R, Smax)
    lowerDelta = np.random.uniform(0.7, 1.0, size=N)
    higherDelta = np.random.uniform(1.0, 1.3, size=N)

    biddingFactorHistory = []
    biddingFactor = initBiddingFactor(N, K)
    biddingFactorHistory.append(biddingFactor)
    for auctionRound in range(R):
        # randomize order of sold items
        auctionItemOrderInd = np.random.permutation(np.arange(K))
        auctionItemOrder = rearangeArray(
            valueItems[auctionRound], auctionItemOrderInd)
        # adapt to the biddingFactors to the order the items are sold
        biddingFactorOrder = np.array(
            [rearangeArray(i, auctionItemOrderInd) for i in biddingFactor])
        if not pure:
            winners, profitsBuyer, profitsSeller, marketPrices = auctionItemsImpure(auctionItemOrder,
                                                                                    biddingFactorOrder, penalty)
            # BiddingFactors get updated for all buyers in every round
            biddingFactor = updateBiddingFactorImpure(
                biddingFactor, winners, auctionItemOrderInd, lowerDelta, higherDelta)
        else:
            winners, profitsBuyer, profitsSeller, marketPrices = auctionItemsPure(auctionItemOrder,
                                                                                  biddingFactorOrder)
            biddingFactor = updateBiddingFactorPure(
                biddingFactor, winners, auctionItemOrderInd, lowerDelta, higherDelta)

        rMarketprices.append(marketPrices)
        rSellerProfit.append(rSellerProfit[-1]+profitsSeller)
        rBuyerProfit.append(rBuyerProfit[-1]+profitsBuyer)

        biddingFactorHistory.append(biddingFactor)
    return rBuyerProfit, rSellerProfit, rMarketprices


def auctionItemsImpure(itemStartingprice, biddingFactorAlpha, penalty=0.05):
    """One round of impure auctions

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
    auctionRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    winners = []
    for i, item in enumerate(itemStartingprice):
        for winnerInd, marketPrice, winningBid in auctionRounds:
            bids[winnerInd, i] = max(
                bids[winnerInd, i], item + (marketPrice - winningBid) + winningBid*penalty)
        marketPrice = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < marketPrice])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        if len(sortedBids) > 1:
            winnerToPay = sortedBids[-2]
        else:
            winnerToPay = item

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])

    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1]


def auctionItemsPure(itemStartingprice, biddingFactorAlpha):
    """One round of pure auctions

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
    auctionRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    winners = []
    for i, item in enumerate(itemStartingprice):
        bidsNonWinners = np.array(
            [b for i, b in enumerate(bids) if i not in winners])
        marketPrice = computeMarketPrice(bidsNonWinners, i)
        sortedBids = sorted(
            bidsNonWinners[:, i][bidsNonWinners[:, i] < marketPrice])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        if len(sortedBids) > 1:
            winnerToPay = sortedBids[-2]
        else:
            winnerToPay = item

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])
    # after auction ends: calculate profits
    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1]


def calculateProfits(auctionRounds, numBuyers, numSellers, penalty):
    """Calculate profits for buyers and sellers"""
    profitBuyer = np.zeros(numBuyers)
    profitSeller = np.zeros(numSellers)
    for seller, [winnerInd, marketPrice, winningBid] in enumerate(auctionRounds):
        if profitBuyer[winnerInd] == 0:
            profitSeller[seller] += winningBid
            profitBuyer[winnerInd] = marketPrice - winningBid
        else:
            profitSeller[seller] += winningBid
            oldWinningBid = 0
            oldSeller = 0
            for oldS, r in enumerate(auctionRounds[:seller]):
                if r[0] == winnerInd:
                    oldWinningBid = r[2]
                    oldSeller = oldS
            fee = oldWinningBid*penalty
            profitBuyer[winnerInd] = marketPrice - winningBid - fee
            profitSeller[oldSeller] += fee - oldWinningBid
    return profitBuyer, profitSeller


def updateBiddingFactorImpure(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta):
    """Standard bidding strategy update

    After each auction over item m offered by seller k where
    buyer n participated the value of the bidding factor is updated
    (standard bidding strategy)
    After each auction over item m offered by seller k where buyer n
    participated value of the bidding factor is updated:
    where ∆ n – a bid decrease factor of buyer n (∆ n ≤ 1), and ∆ n – is a bid increase factor of buyer n (∆ n ≥ 1). The bid
    factors are set per buyer once per simulation. This way the bids of the buyer n are going to adapt to results of
    auctions organized by seller k for a particular item m.

    # NOTE: in "pure" auctions update only if buyer has not won yet
    # --> (because if a buyer has won he does not bid anymore)
    """
    for winner, seller in enumerate(sellerIDs):
        nonWinners = [i for i in range(
            len(biddingFactor)) if i != winnerIDs[winner]]
        biddingFactor[winnerIDs[winner],
                      seller] *= lowerDelta[winnerIDs[winner]]
        biddingFactor[nonWinners, seller] *= higherDelta[nonWinners]

    return biddingFactor


def updateBiddingFactorPure(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta):
    """Bidding factor update for pure auction"""
    for winner, seller in enumerate(sellerIDs):
        currentWinner = winnerIDs[winner]
        # update winner
        biddingFactor[currentWinner, seller] *= lowerDelta[currentWinner]
        # update all who have not won yet
        nonWinners = [i for i in range(
            len(biddingFactor)) if i != winnerIDs[winner] or i in winnerIDs[:winner]]
        biddingFactor[nonWinners, seller] *= higherDelta[nonWinners]

    return biddingFactor


##################################
# ALTERNATIVE STRATEGY FUNCTIONS #
##################################


def auctionSimulationStrats(M, K, N, R, Smax, penalty=0.05, one=False):
    """Full auction simulation function using alternate strategies

    Parameters:
    M -- The amount of types of items
    K -- The amount of sellers
    N -- The amount of buyers
    R -- The amount of bidding rounds
    Smax -- Maximum starting price
    penalty -- Penalty factor for calculating penalties when selling back
    one -- should use alternative strat one or two

    Returns:
    A three tuple containing
    rStats -- Statistics of market price development over rounds
    rSellerProfit -- Profits for every seller over rounds
    rBuyersProfit -- Profits for every buyer over rounds
    """
    if N < K:
        raise ValueError(
            'Error: Number of Buyers needs to be bigger than number of Sellers')

    rMarketprices = [np.zeros(K)]
    rSellerProfit = [np.zeros(K)]
    rBuyerProfit = [np.zeros(N)]

    seller2Items = assignItemToSeller(K, M)
    valueItems = assignPriceToItem(seller2Items, R, Smax)
    lowerDelta = np.random.uniform(0.7, 1.0, size=N)
    higherDelta = np.random.uniform(1.0, 1.3, size=N)

    biddingFactorHistory = []
    biddingFactor = initBiddingFactor(N, K)
    biddingFactorHistory.append(biddingFactor)
    for auctionRound in range(R):
        # randomize order of sold items
        auctionItemOrderInd = np.random.permutation(np.arange(K))
        auctionItemOrder = rearangeArray(
            valueItems[auctionRound], auctionItemOrderInd)
        # adapt to the biddingFactors to the order the items are sold
        biddingFactorOrder = np.array(
            [rearangeArray(i, auctionItemOrderInd) for i in biddingFactor])
        if one:
            winners, profitsBuyer, profitsSeller, marketPrices = auctionItemsStratOne(auctionItemOrder,
                                                                                      biddingFactorOrder, penalty)
            # BiddingFactors get updated for all buyers in every round
            biddingFactor = updateBiddingFactorImpure(
                biddingFactor, winners, auctionItemOrderInd, lowerDelta, higherDelta)
        else:
            winners, profitsBuyer, profitsSeller, marketPrices, overBidsRounds = auctionItemsStratTwo(auctionItemOrder,
                                                                                                      biddingFactorOrder)
            biddingFactor = updateBiddingFactorStratTwo(
                biddingFactor, winners, auctionItemOrderInd, lowerDelta, higherDelta, overBidsRounds)

        rMarketprices.append(marketPrices)
        rSellerProfit.append(rSellerProfit[-1]+profitsSeller)
        rBuyerProfit.append(rBuyerProfit[-1]+profitsBuyer)

        biddingFactorHistory.append(biddingFactor)
    return rBuyerProfit, rSellerProfit, rMarketprices


def auctionItemsStratOne(itemStartingprice, biddingFactorAlpha, penalty=0.05):
    """Aution round for strategy 1"""
    auctionRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    winners = []
    for i, item in enumerate(itemStartingprice):
        for winnerInd, marketPrice, winningBid in auctionRounds:
            bids[winnerInd, i] = bids[winnerInd, i] - \
                (marketPrice - winningBid) - winningBid*penalty
        marketPrice = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < marketPrice])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        if len(sortedBids) > 1:
            winnerToPay = sortedBids[-2]
        else:
            winnerToPay = item

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])

    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1]


def auctionItemsStratTwo(itemStartingprice, biddingFactorAlpha, penalty=0.05):
    """Auction round for strategy 2"""
    auctionRounds = []
    overBidsRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    winners = []
    for i, item in enumerate(itemStartingprice):
        for winnerInd, marketPrice, winningBid in auctionRounds:
            bids[winnerInd, i] = bids[winnerInd, i] - \
                (marketPrice - winningBid) - winningBid*penalty
        marketPrice = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < marketPrice])
        overBids = [j for j, bid in enumerate(bids[i]) if bid >= marketPrice]
        overBidsRounds.append(overBids)
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        if len(sortedBids) > 1:
            winnerToPay = sortedBids[-2]
        else:
            winnerToPay = item

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])

    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1], overBidsRounds


def updateBiddingFactorStratTwo(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta, overBidsRounds):
    """Bidding factor update for strategy 2"""
    for winner, seller in enumerate(sellerIDs):
        nonWinners = [i for i in range(
            len(biddingFactor)) if i != winnerIDs[winner]]
        biddingFactor[winnerIDs[winner],
                      seller] *= lowerDelta[winnerIDs[winner]]
        biddingFactor[nonWinners, seller] *= higherDelta[nonWinners]
        for nw in nonWinners:
            if nw in overBidsRounds[seller]:
                biddingFactor[nw, seller] = np.random.uniform(
                    low=1.0, high=biddingFactor[nw, seller])
    print(biddingFactor)
    return biddingFactor


####################
# HELPER FUNCTIONS #
####################

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
                                           size=(amountBuyers, amountSellers))
    return biddingFactorAlpha


def assignPriceToItem(sellerItems, numRounds, maxPrice):
    """Every seller assigns a price to its item"""
    itemPrices = np.random.uniform(
        size=(numRounds, len(sellerItems)), low=0, high=maxPrice)
    return np.round(itemPrices, decimals=2)


def rearangeArray(array, indices):
    """Rearrange array to indices"""
    return [array[i] for i in indices]


def visualize(N, K, buyerprofit, sellerprofit, marketprices, pure, pen=-1, save=False):
    """Visualize simulation results

    Parameters:
    N -- Number of buyers
    K -- Number of sellers
    buyerprofit -- simulation outcome buyers
    sellerprofit -- simulation outcome sellers
    marketprices -- simulation outcome market prices
    pure -- was it a pure auction?
    pen -- penalty
    save -- should save picture to figures folder
    """
    global penalty
    if pen == -1:
        pen = penalty

    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(10, 14))
    if pure:
        fig.suptitle(f'Pure auction', fontsize=16)
    else:
        fig.suptitle(f'Impure auction, penalty: {pen}', fontsize=16)
    ax1.plot(buyerprofit)
    ax1.plot(np.mean(buyerprofit, axis=1), '--',
             color='red', label='Mean', linewidth=3)
    ax1.plot(np.median(buyerprofit, axis=1), '--',
             color='purple', label='Median', linewidth=2.5)
    ax1.set_title(f'Buyerprofit, numBuyers: {N}')
    # ax1.set_xlabel('Auctionrounds')
    # ax1.set_ylim(0, 14000)
    ax1.set_ylabel('Profit')
    ax1.legend()

    ax2.plot(sellerprofit)
    ax2.plot(np.mean(sellerprofit, axis=1), '--',
             color='red', label='Mean', linewidth=3)
    ax2.plot(np.median(sellerprofit, axis=1), '--',
             color='purple', label='Median', linewidth=2.5)
    ax2.set_title(f'Sellerprofit, numSellers: {K}')
    # ax2.set_xlabel('Auctionrounds')
    # ax2.set_ylim(0, 6000)
    ax2.set_ylabel('Profit')
    ax2.legend()

    ax3.plot(marketprices)
    ax3.plot(np.mean(marketprices, axis=1), '--',
             color='red', label='Mean', linewidth=3)
    ax3.plot(np.median(marketprices, axis=1), '--',
             color='purple', label='Median', linewidth=2.5)
    ax3.set_title('Marketprices')
    ax3.set_xlabel('Auctionrounds')
    ax3.set_ylabel('Price')
    ax3.legend()
    if save:
        figname = ""
        if pure:
            figname = f'figures/stats_pure_sellers{K}_buyers{N}_rounds{len(sellerprofit)-1}.png'
        else:
            figname = f'figures/stats_impure_sellers{K}_buyers{N}_rounds{len(sellerprofit)-1}_penalty{round(pen, 2)}.png'
        fig.savefig(figname)
        plt.close()
    else:
        plt.show()


def main():
    """Some cmd input handling and executing simulation"""
    global numItems
    global numBuyers
    global numRounds
    global numSellers
    global maxStartingPrice
    global penalty
    global pure

    if len(sys.argv) == 8:
        try:
            numItems = int(sys.argv[1])
            numBuyers = int(sys.argv[2])
            numSellers = int(sys.argv[3])
            numRounds = int(sys.argv[4])
            maxStartingPrice = int(sys.argv[5])
            penalty = float(sys.argv[6])
            pure = bool(int(sys.argv[7]))
        except ValueError:
            print('Illegal arguments')
            exit()
    else:
        print('Using default arguments')

    b, s, m = auctionSimulation(numItems, numSellers, numBuyers, numRounds,
                                maxStartingPrice, penalty, pure)
    print(f'Results after {"pure" if pure else "impure"} auction:')

    print(f'Profit of buyers: \n {b[-1]}')
    print(f'Profit of sellers: \n {s[-1]}')
    print(f'Mean of buyers profit:  {np.mean(b[-1]):8.2f} Median: {np.median(b[-1]):8.2f}')
    print(f'Mean of sellers profit: {np.mean(s[-1]):8.2f} Median: {np.median(s[-1]):8.2f}')
    visualize(numBuyers, numSellers, b, s, m, pure, save=False)


def experiment():
    buyerincrease = 10
    sellerincrease = 10
    step = 5

    penalty_start = 0
    penalty_step = 0.01
    penalty_max = 1
    pure = False
    # for ns in range(1, sellerincrease):
    #    for nb in range(ns+1, ns+buyerincrease):
    #        b, s, m = auctionSimulation(
    #            ns*step, ns*step, nb*step, 20, 100, pure=pure)
    #        visualize(nb*step, ns*step, b, s, m, pure, save=True)
    current_penalty = penalty_start
    # while current_penalty <= penalty_max:
    #    print('penalty ', current_penalty)
    #    b, s, m = auctionSimulation(
    #       5, 5, 20, 20, 100, pure=pure, penalty=current_penalty)
    #    visualize(20, 5, b, s, m, pure, pen=current_penalty, save=True)
    #    current_penalty += penalty_step


if __name__ == '__main__':
    main()
    # experiment()
