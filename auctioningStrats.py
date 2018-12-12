import numpy as np
import matplotlib.pyplot as plt
import sys

def auctionItemsStratOne(itemStartingprice, biddingFactorAlpha, penalty=0.05):
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
            bids[winnerInd, i] = bids[winnerInd, i] - (marketPrice - winningBid) - winningBid*penalty
            #max(bids[winnerInd, i], item + (marketPrice - winningBid) + winningBid*penalty)
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

def auctionItemsStratTwo(itemStartingprice, biddingFactorAlpha, penalty=0.05):
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
    overBidsRounds = []
    bids = biddingFactorAlpha * itemStartingprice
    # NOTE auctions take place one item at a time
    winners = []
    for i, item in enumerate(itemStartingprice):
        # print(f'Startingprice: {item}')
        # look at old bids and adapt bids with formula 4
        for winnerInd, marketPrice, winningBid in auctionRounds:
            bids[winnerInd, i] = bids[winnerInd, i] - (marketPrice - winningBid) - winningBid*penalty
            #max(bids[winnerInd, i], item + (marketPrice - winningBid) + winningBid*penalty)
        # print(f'bids: {bids[:, i]}')
        marketPrice = computeMarketPrice(bids, i)
        sortedBids = sorted(bids[:, i][bids[:, i] < marketPrice])
        overBids = [j for j, bid in enumerate(bids) if bid >= marketPrice]
        overBidsRounds.append(overBids)
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
    return winners, profitBuyer, profitSeller, np.array(auctionRounds)[:, 1], overBidsRounds

def updateBiddingFactorStratTwo(biddingFactor, winnerIDs, sellerIDs, lowerDelta, higherDelta, overBidsRounds):
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
        for nw in nonWinners:
            if nw in overBidsRounds[seller]:
                biddingFactor[nw, seller] = np.random.uniform(low=1.0, high=biddingFactor[nw, seller])

    return biddingFactor
