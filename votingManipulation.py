import numpy as np
from collections import Counter
import itertools
import copy


# calc the number of candidates - index where the first preference of voter is
def calcHappiness(winner, prefMatrix):
    return len(prefMatrix[0]) - np.where(prefMatrix == winner)[1]


def votingResults(prefMatrix, scheme):
    bordaPoints = np.arange(len(prefMatrix[0]))[::-1]
    if scheme == "Borda":
        candidateVotes = dict()
        for voter in prefMatrix:
            for i, cand in enumerate(voter):
                candidateVotes[cand] = candidateVotes.get(cand, 0) + bordaPoints[i]
        # print(f'Bordapoints: {sorted(candidateVotes.items(), key=lambda t: t[1])[::-1]}')
        candidates = sorted(candidateVotes.items(), key=lambda t: t[1])[::-1]
        maxVotes = candidates[0][1]
    else:
        if scheme == "VfO":
            c = Counter(prefMatrix[:, 0])
        elif scheme == "VfT":
            c = Counter(prefMatrix[:, :2].reshape(-1))
        elif scheme == "Veto":
            c = Counter(prefMatrix[:, :-1].reshape(-1))

        # print(c)
        # print(f'mostCommon: {c.most_common()}')
        candidates = c.most_common()
        maxVotes = c.most_common(1)[0][1]

    # Tie-breaking: Sort winners by lexicographical order
    winners = []
    for (candidate, votes) in candidates:
        if votes < maxVotes:
            break
        winners.append(candidate)
    winner = sorted(winners)[0]
    return winner, calcHappiness(winner, prefMatrix)


def howShouldLie(voter, prefMatrix, scheme):
    winnerBefore, happiness = votingResults(prefMatrix, scheme)
    lying = False
    hapinessVoter = happiness[voter]
    if hapinessVoter == len(prefMatrix[0]):
        return False, prefMatrix[voter]
    else:
        bestPrefs = prefMatrix[voter]
        for prefs in itertools.permutations(prefMatrix[voter]):
            newPrefMatrix = copy.copy(prefMatrix)
            newPrefMatrix[voter] = prefs
            winnerNew, newHappiness = votingResults(newPrefMatrix, scheme)
            newHappinessVoter = newHappiness[voter]
            if newHappinessVoter > hapinessVoter:
                hapinessVoter = newHappinessVoter
                lying = True
                bestPrefs = prefs
        return lying, bestPrefs


def main():
    # example of a preference matrix
    prefMatrix = np.array([['B', 'F', 'A', 'C', 'E', 'D'], ['A', 'F', 'C', 'D', 'E', 'B'], ['B', 'F', 'E', 'D', 'C', 'A']])
    # possible voting schemes
    votingSchemes = ["VfO", "VfT", "Veto", "Borda"]
    print(f"Non Strategic Outcome: ")
    for scheme in votingSchemes:
        print(f'Scheme: {scheme}')
        winner, happiness = votingResults(prefMatrix, scheme)
        print(f'Winner: {winner}')
        print(f'Overall Happiness: {np.sum(happiness)}')
        print()
    print(howShouldLie(1, prefMatrix, "VfO"))
# TODO: Possibly empty set of strategic-voting options 𝑆={𝑠𝑖},𝑖∈𝑛.
# A strategic-voting option for voter 𝑖 is a tuple 𝑠𝑖=(𝑣,𝑂̃,𝐻̃,𝑧),
# where 𝑣 – is a tactically modified preference list of this voter,
# 𝑂̃ – a voting outcome resulting from applying 𝑣,
# 𝐻̃ – an overall voter happiness level resulting from applying 𝑣, and
# 𝑧 – briefly states why 𝑖 prefers 𝑂̃ over 𝑂 (i.e., what the advantage is for 𝑖);

# TODO: Overall risk of strategic voting for this voting situation
# 𝑅=|𝑆|𝑛⁄ (size of strategic-voting options set over the number of voters).

# print(calcHappiness('B', prefMatrix))


main()
