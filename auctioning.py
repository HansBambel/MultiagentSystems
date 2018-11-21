import numpy as np


def auctionItems(itemStartingprice, biddingFactorAlpha):
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
        print(f'winner: {winnerInd} with bid: {winner}, to Pay: {winnerToPay}, profit: {average - winnerToPay}')


def main():
    np.random.seed(42)
    maximumStartingprice = 100
    simulations = 10
    numSellers = 5
    numBuyers = 2*numSellers
    lowerDelta = np.random.uniform(0.5, 1.0, size=numBuyers)
    higherDelta = np.random.uniform(1.0, 1.5, size=numBuyers)

    itemStartingprice = np.random.uniform(0, maximumStartingprice, size=(simulations, numSellers))
    biddingFactorAlpha = np.random.uniform(1.0, 1.9, size=(simulations, numBuyers, numSellers))

    for i in range(simulations):
        print(i)
        auctionItems(itemStartingprice[i], biddingFactorAlpha[i])


main()
