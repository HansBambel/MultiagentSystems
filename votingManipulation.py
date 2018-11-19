import numpy as np
from collections import Counter
import itertools
import copy


# calc the number of candidates - index where the first preference of voter is
def calcHappiness(winner, prefMatrix):
    return len(prefMatrix[0]) - np.where(prefMatrix == winner)[1] - 1


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
    return winner


def howShouldVoterLie(voter, prefMatrix, scheme):
    winnerBefore = votingResults(prefMatrix, scheme)
    happiness = calcHappiness(winnerBefore, prefMatrix)
    lying = False
    happinessVoter = happiness[voter]
    # print(happinessVoter)
    if happinessVoter == len(prefMatrix[0])-1:
        return False, prefMatrix[voter], winnerBefore, happinessVoter, np.sum(happiness)
    else:
        bestPrefs = prefMatrix[voter]
        for prefs in itertools.permutations(prefMatrix[voter]):
            newPrefMatrix = copy.copy(prefMatrix)
            newPrefMatrix[voter] = prefs
            winnerNew = votingResults(newPrefMatrix, scheme)
            # calc happiness with old prefmatrix (just the winner changed)
            newHappiness = calcHappiness(winnerNew, prefMatrix)
            newHappinessVoter = newHappiness[voter]
            if newHappinessVoter > happinessVoter:
                happinessVoter = newHappinessVoter
                lying = True
                bestPrefs = prefs
                savedWinner = winnerNew
                savedTotalHappiness = np.sum(newHappiness)
        if lying:
            return True, bestPrefs, savedWinner, happinessVoter, savedTotalHappiness
        else:
            return False, prefMatrix[voter], winnerBefore, happinessVoter, np.sum(happiness)


def main():
    # example of a preference matrix
    prefMatrix = np.array([['B', 'F', 'A', 'C', 'E', 'D'],
                           ['A', 'F', 'C', 'D', 'E', 'B'],
                           ['B', 'F', 'E', 'D', 'C', 'A']])
    # print(f'Should be 10: {np.sum(calcHappiness("B", prefMatrix))}')
    # print(f'Should be 12: {np.sum(calcHappiness("F", prefMatrix))}')
    # print(f'Should be 4: {np.sum(calcHappiness("D", prefMatrix))}')
    # possible voting schemes
    votingSchemes = ["VfO", "VfT", "Veto", "Borda"]
    print(f"Non Strategic Outcome: ")
    for scheme in votingSchemes:
        print(f'Scheme: {scheme}')
        winner = votingResults(prefMatrix, scheme)
        happiness = calcHappiness(winner, prefMatrix)
        print(f'Winner: {winner}')
        print(f'Overall Happiness: {np.sum(happiness)}')
        numLyingVoters = 0
        for i, voter in enumerate(prefMatrix):
            voterLies, bestPrefs, newWinner, newHappiness, newTotalHappiness = howShouldVoterLie(i, prefMatrix, scheme)

            if voterLies:
                numLyingVoters += 1
                # print(f'Voter {i} happiness before: {happiness[i]}, after: {newHappiness}, new Winner: {newWinner}, true intention: {prefMatrix[i]}, voted: {bestPrefs}')
                print(f'Voter {i} modified prefList: {bestPrefs}, new Winner: {newWinner}, new overall Happiness: {newTotalHappiness}, Reason for Voter {i}: happiness increase: {happiness[i]} --> {newHappiness}')
        print(f'Risk of strategic voting: {numLyingVoters/prefMatrix.shape[0]}')
        print()
    # print(howShouldVoterLie(1, prefMatrix, "VfO"))
# Possibly empty set of strategic-voting options 𝑆={𝑠𝑖},𝑖∈𝑛.
# A strategic-voting option for voter 𝑖 is a tuple 𝑠𝑖=(𝑣,𝑂̃,𝐻̃,𝑧),
# where 𝑣 – is a tactically modified preference list of this voter,
# 𝑂̃ – a voting outcome resulting from applying 𝑣,
# 𝐻̃ – an overall voter happiness level resulting from applying 𝑣, and
# 𝑧 – briefly states why 𝑖 prefers 𝑂̃ over 𝑂 (i.e., what the advantage is for 𝑖);

# Overall risk of strategic voting for this voting situation
# 𝑅=|𝑆|𝑛⁄ (size of strategic-voting options set over the number of voters).

# print(calcHappiness('B', prefMatrix))


main()
