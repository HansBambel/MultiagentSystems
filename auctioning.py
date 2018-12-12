import numpy as np
import matplotlib.pyplot as plt
import sys
# import tqdm


def auctionItemsImpure(itemStartingprice, biddingFactorAlpha, penalty=0.05):
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
    auctionRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    # NOTE auctions take place one item at a time
    winners = []
    for i, item in enumerate(itemStartingprice):
        # print(f'Startingprice: {item}')
        # look at old bids and adapt bids with formula 4
        for winnerInd, marketPrice, winningBid in auctionRounds:
            bids[winnerInd, i] = max(
                bids[winnerInd, i], item + (marketPrice - winningBid) + winningBid*penalty)
        # print(f'bids: {bids[:, i]}')
        marketPrice = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < marketPrice])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        # winner pays only second highest
        winnerToPay = sortedBids[-2]
        # print(f'marketPrice {winnerToPay}, Winner: {winnerInd}, Profit: {marketPrice - winnerToPay}')

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])
    # after auction ends: calculate profits
    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    # print(np.array(auctionRounds)[:,1])
    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1]


def auctionItemsPure(itemStartingprice, biddingFactorAlpha):
    auctionRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    # NOTE auctions take place one item at a time
    winners = []
    for i, item in enumerate(itemStartingprice):
        # print(f'bids: {bids[:, i]}')
        # take the winner out of consideration for the rest of the auctionround
        bidsNonWinners = np.array(
            [b for i, b in enumerate(bids) if i not in winners])
        # print(f'bidsNonWinners: {bidsNonWinners[:, i]}')
        marketPrice = computeMarketPrice(bidsNonWinners, i)
        sortedBids = sorted(
            bidsNonWinners[:, i][bidsNonWinners[:, i] < marketPrice])
        winner = sortedBids[-1]
        winnerInd = np.where(bids[:, i] == winner)[0][0]
        winners.append(winnerInd)

        # winner pays only second highest
        winnerToPay = sortedBids[-2]
        # print(f'marketPrice {winnerToPay}, Winner: {winnerInd}, Profit: {marketPrice - winnerToPay}')

        auctionRounds.append([winnerInd, marketPrice, winnerToPay])
    # after auction ends: calculate profits
    profitBuyer, profitSeller = calculateProfits(auctionRounds, len(
        biddingFactorAlpha), len(biddingFactorAlpha[1]), penalty)

    # print(np.array(auctionRounds)[:,1])
    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1]


def calculateProfits(auctionRounds, numBuyers, numSellers, penalty):
    profitBuyer = np.zeros(numBuyers)
    profitSeller = np.zeros(numSellers)
    for seller, [winnerInd, marketPrice, winningBid] in enumerate(auctionRounds):
        if profitBuyer[winnerInd] == 0:
            profitSeller[seller] += winningBid
            profitBuyer[winnerInd] = marketPrice - winningBid
        # if buyer already auctioned another item: refund previous one
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
    # Update winner and all other "losers"
    for winner, seller in enumerate(sellerIDs):
        nonWinners = [i for i in range(
            len(biddingFactor)) if i != winnerIDs[winner]]
        biddingFactor[winnerIDs[winner],
                      seller] *= lowerDelta[winnerIDs[winner]]
        biddingFactor[nonWinners, seller] *= higherDelta[nonWinners]

    return biddingFactor


def updateBiddingFactorPure(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta):
    # if won: update and update all others who have not won yet
    for winner, seller in enumerate(sellerIDs):
        currentWinner = winnerIDs[winner]
        # update winner
        biddingFactor[currentWinner, seller] *= lowerDelta[currentWinner]
        # update all who have not won yet
        nonWinners = [i for i in range(
            len(biddingFactor)) if i != winnerIDs[winner] or i in winnerIDs[:winner]]
        biddingFactor[nonWinners, seller] *= higherDelta[nonWinners]

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
                                           size=(amountBuyers, amountSellers))
    return biddingFactorAlpha


def assignPriceToItem(sellerItems, numRounds, maxPrice):
    """Every seller assigns a price to its item"""
    itemPrices = np.random.uniform(
        size=(numRounds, len(sellerItems)), low=0, high=maxPrice)
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


def auctionSimulation(M, K, N, R, Smax, penalty=0.05,
                      pure=False, biddingtype=btypes[0]):
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
        raise ValueError('Error: lawl, learn english, fgt')

    np.random.seed(1337)
    # seed 80 has a negative profit
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
        # print(f'Auctionround: {auctionRound}')
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
        # print(f'profitsBuyer: \n {rBuyerProfit[-1]}')
        # print(f'profitsSeller: \n {rSellerProfit[-1]}')
    return rBuyerProfit, rSellerProfit, rMarketprices


def visualize(N, K, buyerprofit, sellerprofit, marketprices, pure):
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(10, 14))
    if pure:
        fig.suptitle('Pure auction', fontsize=16)
    else:
        fig.suptitle('Impure auction', fontsize=16)
    ax1.plot(buyerprofit)
    ax1.plot(np.mean(buyerprofit, axis=1), '--',
             color='red', label='Mean', linewidth=3)
    ax1.plot(np.median(buyerprofit, axis=1), '--',
             color='purple', label='Median', linewidth=2.5)
    ax1.set_title(f'Buyerprofit, numBuyers: {N}')
    # ax1.set_xlabel('Auctionrounds')
    ax1.set_ylabel('Profit')
    ax1.legend()

    ax2.plot(sellerprofit)
    ax2.plot(np.mean(sellerprofit, axis=1), '--',
             color='red', label='Mean', linewidth=3)
    ax2.plot(np.median(sellerprofit, axis=1), '--',
             color='purple', label='Median', linewidth=2.5)
    ax2.set_title(f'Sellerprofit, numSellers: {K}')
    # ax2.set_xlabel('Auctionrounds')
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
    plt.show()


def main():
    global numItems
    global numBuyers
    global numRounds
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
            pure = bool(sys.argv[7])
        except ValueError:
            print('Illegal arguments')
            exit()
    else:
        print('Using default arguments')

    b, s, m = auctionSimulation(numItems, numSellers, numBuyers, numRounds,
                                maxStartingPrice, penalty, pure=pure)
    print('Results after auction:')
    print(f'Profit of buyers: \n {b[-1]}')
    print(f'Profit of sellers: \n {s[-1]}')
    visualize(numBuyers, numSellers, b, s, m, pure)


def experiment():
    pass


numItems = 6
numBuyers = 40
numSellers = 20
numRounds = 20
maxStartingPrice = 100
penalty = 0.05
pure = False

if __name__ == '__main__':
    # main()
    experiment()
