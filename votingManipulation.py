import numpy as np
from collections import Counter, OrderedDict

prefMatrix = np.array([['B', 'F', 'A', 'C', 'E', 'D'], ['A', 'F', 'C', 'D', 'E', 'B'], ['B', 'F', 'E', 'D', 'C', 'A']])

votingSchemes = ["VfO", "VfT", "Veto", "Borda"]

def calcHappiness(winner, prefMatrix):
    return len(prefMatrix[0]) - np.where(prefMatrix == winner)[1]

bordaPoints = np.arange(len(prefMatrix[0]))[::-1]
# TODO tiebreaker
for scheme in votingSchemes:
    print(f"Scheme: {scheme}")
    print(f"Non Strategic Outcome: ")
    if scheme == "Borda":
        candidateVotes = dict()
        for voter in prefMatrix:
            for i, cand in enumerate(voter):
                candidateVotes[cand] = candidateVotes.get(cand, 0) + bordaPoints[i]
        print(f'Bordapoints: {sorted(candidateVotes.items(), key=lambda t: t[1])[::-1]}')
        candidates = sorted(candidateVotes.items(), key=lambda t: t[1])[::-1]
        maxVotes = candidates[0][1]
    else:
        if scheme == "VfO":
            c = Counter(prefMatrix[:, 0])
        elif scheme == "VfT":
            c = Counter(prefMatrix[:, :2].reshape(-1))
        elif scheme == "Veto":
            c = Counter(prefMatrix[:, :-1].reshape(-1))

        print(c)
        # print(f'mostCommon: {c.most_common()}')
        candidates = c.most_common()
        maxVotes = c.most_common(1)[0][1]

    winners = []
    for (candidate, votes) in candidates:
        if votes < maxVotes:
            break
        winners.append(candidate)
    winner = sorted(winners)[0]
    print(f'Winner: {winner}')
    print(f'Overall Happiness: {np.sum(calcHappiness(winner, prefMatrix))}')
    print()
# print(calcHappiness('B', prefMatrix))
