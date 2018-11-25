import numpy as np
from collections import Counter
import itertools
import copy

OUTPUT = ''
strategic_distr = {}


def _risk_exp_helper(prefs, voting=['VfO']):
    prefMatrix = np.array(prefs)
    votingSchemes = voting
    global strategic_distr
    # votingSchemes = ["VfT"]
    for scheme in votingSchemes:
        winner = votingResults(prefMatrix, scheme)
        happiness = calcHappiness(winner, prefMatrix)
        numLyingVoters = 0
        for i, voter in enumerate(prefMatrix):
            voterLies, sVotingOptions, winners, voterHappinesses, totalHappinesses = howShouldVoterLie(i, prefMatrix, scheme)
            if voterLies != 0:
                numLyingVoters += 1
        strategic_voting_val = numLyingVoters/prefMatrix.shape[0]
        if strategic_voting_val in strategic_distr.keys():
            strategic_distr[strategic_voting_val] += 1
        else:
            strategic_distr[strategic_voting_val] = 1


def risk_experiment(amount_voters, amount_options, scheme=['VfO']):
    global strategic_distr
    for m in generatePrefMatrix(amount_voters, amount_options):
        _risk_exp_helper(m, scheme)
    print('DISTRIBUTION', strategic_distr)
    strategic_distr = {}


def overall_happiness_experiment(amount_voters, amountoptions):
    # for every matrix
    # for every scheme
    # max{scheme}(happiness)
    schemes = ['VfO', 'VfT', 'Veto', 'Borda']
    scheme_stats = {}
    for s in schemes:
        scheme_stats[s] = 0

    for m in generatePrefMatrix(amount_voters, amount_options):
        m = np.array(m)
        max_happiness = 0
        for scheme in schemes:
            winner = votingResults(m, scheme)
            happiness = np.sum(calcHappiness(winner, m))
            if happiness >= max_happiness:
                max_happiness = happiness
                winner_scheme = scheme
        scheme_stats[winner_scheme] += 1
    print(scheme_stats)


def generatePrefMatrix(amount_voters, amount_options):
    full_options = [a for a in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    current_options = full_options[:amount_options]
    perms = [list(i) for i in itertools.permutations(current_options)]
    tuplematrix = [list(i) for i in itertools.combinations_with_replacement(perms, amount_voters)]
    return tuplematrix


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
    lies = 0
    happinessVoter = happiness[voter]
    sVotingOptions = []
    winners = []
    voterHappinesses = []
    totalHappinesses = []
    # print(happinessVoter)
    if happinessVoter == len(prefMatrix[0]) - 1:
        return 0, [prefMatrix[voter]], [winnerBefore], [happinessVoter], [np.sum(happiness)]
    # bestPrefs = prefMatrix[voter]
    for prefs in itertools.permutations(prefMatrix[voter]):
        newPrefMatrix = copy.copy(prefMatrix)
        newPrefMatrix[voter] = prefs
        winnerNew = votingResults(newPrefMatrix, scheme)
        # calc happiness with old prefmatrix (just the winner changed)
        newHappiness = calcHappiness(winnerNew, prefMatrix)
        newHappinessVoter = newHappiness[voter]
        if newHappinessVoter > happinessVoter:
            # happinessVoter = newHappinessVoter
            lies += 1
            # bestPrefs = prefs
            sVotingOptions.append(prefs)
            # savedWinner = winnerNew
            winners.append(winnerNew)
            # savedTotalHappiness = np.sum(newHappiness)
            voterHappinesses.append(newHappinessVoter)
            totalHappinesses.append(np.sum(newHappiness))
    if lies != 0:
        return lies, sVotingOptions, winners, voterHappinesses, totalHappinesses
    else:
        return lies, [prefMatrix[voter]], [winnerBefore], [happinessVoter], [np.sum(happiness)]


def main():
    # example of a preference matrix
    ##### ENTER YOUR PREFERENCEMATRIX HERE #####
    prefMatrix = np.array([['B', 'F', 'A', 'C', 'E', 'D'],
                           ['A', 'F', 'C', 'D', 'E', 'B'],
                           ['D', 'A', 'F', 'C', 'E', 'B'],
                           ['B', 'F', 'C', 'D', 'E', 'A'],
                           ['E', 'B', 'F', 'D', 'C', 'A']])
    # possible voting schemes
    ##### SELECT YOUR VOTING SCHEME HERE ######
    votingSchemes = ["VfO", "VfT", "Veto", "Borda"]
    # votingSchemes = ["VfO", "Veto"]
    printf(f"Non Strategic Outcome: ")
    for scheme in votingSchemes:
        printf(f'Scheme: {scheme}')
        winner = votingResults(prefMatrix, scheme)
        happiness = calcHappiness(winner, prefMatrix)
        printf(f'Winner: {winner}')
        printf(f'Overall Happiness: {np.sum(happiness)}')
        numLyingVoters = 0
        numLyingOptions = 0
        for i, voter in enumerate(prefMatrix):
            voterLies, sVotingOptions, winners, voterHappinesses, totalHappinesses = howShouldVoterLie(i, prefMatrix, scheme)
            if voterLies != 0:
                numLyingVoters += 1
                numLyingOptions += voterLies
                printf(f'\nVoter {i} real preferences {prefMatrix[i]}')
                for x in range(voterLies):
                    printf(f'Voter {i} modified prefList: {sVotingOptions[x]},'
                           + f' new Winner: {winners[x]}, new overall Happiness: {totalHappinesses[x]},'
                           + f' Reason: happiness increase: {happiness[i]} --> {voterHappinesses[x]}')
                    if winners[x] in sVotingOptions[x][:np.where(prefMatrix[i] == winners[x])[0][0]]:
                        printf('Compromise')
                    if winner in sVotingOptions[x][np.where(prefMatrix[i] == winner)[0][0]+1:]:
                        printf('Burying')

        printf(f'Risk of strategic voting (taken from assignment): {numLyingOptions/prefMatrix.shape[0]}')
        printf(f'Our definition of strategic voting: {numLyingVoters/prefMatrix.shape[0]}')
        printf()

    writeOutToFile(votingSchemes)

# Possibly empty set of strategic-voting options 𝑆={𝑠𝑖},𝑖∈𝑛.
# A strategic-voting option for voter 𝑖 is a tuple 𝑠𝑖=(𝑣,𝑂̃,𝐻̃,𝑧),
# where 𝑣 – is a tactically modified preference list of this voter,
# 𝑂̃ – a voting outcome resulting from applying 𝑣,
# 𝐻̃ – an overall voter happiness level resulting from applying 𝑣, and
# 𝑧 – briefly states why 𝑖 prefers 𝑂̃ over 𝑂 (i.e., what the advantage is for 𝑖);

# Overall risk of strategic voting for this voting situation
# 𝑅=|𝑆|𝑛⁄ (size of strategic-voting options set over the number of voters).

# print(calcHappiness('B', prefMatrix))


def printf(string='\n'):
    global OUTPUT
    OUTPUT += string + '\n'


def writeOutToFile(scheme):
    global OUTPUT
    name = ''.join(scheme)
    with open(f'{name}.txt', 'w') as f:
        f.write(OUTPUT)
    OUTPUT = ''


main()
