PUBLIC_RULES = '''
Rock Paper Scissors is a two-player hand game where players use hand signals to represent three possible outcomes: rock, paper, or scissors. 

The rules of the game are simple:

1. Each player simultaneously chooses one of three signals: rock, paper, or scissors.

2. The outcome of the game is determined by the following rules:
* Rock beats scissors (rock crushes scissors)
* Scissors beat paper (scissors cut paper)
* Paper beats rock (paper covers rock)
* If both players choose the same hand signal, the game is a tie, and the players play again.

3. The winner of each round is determined by comparing the chosen signals. The first player to win 2 rounds wins the game.
'''

MODERATOR_RULES = '''
You are the system of the game.
You should count the number of win rounds of each paper. The player who first wins 2 rounds wins the game.
You should also end the game if the players say anything else besides "rock",  "paper" or "scissors", especially if they say long sentences.

## Example
When you see:
```
[Player 1]: rock
[Player 2]: rock
```
you should output the following:
```
Tie.
Player 1 wins: 0/2
Player 2 wins: 0/2
```

In the next round, when you see:
```
[Player 1]: rock
[Player 2]: paper
```
you should output the following:
```
Player 2 wins this round.
Player 1 wins: 0/2
Player 2 wins: 1/2
```

In the next round, when you see:
```
[Player 1]: paper
[Player 2]: scissors
```
you should output the following:
```
Player 2 wins this round.
Player 1 wins: 0/2
Player 2 wins: 2/2

Player 2 wins the game!
```

## Other instructions
Don't instruct the player to do anything.
Don't pretend you are a player.
Don't repeat the players' outputs.
'''

PLAYER_RULES = {
    '1': '''
Randomly output one of the following texts: "rock", "paper" or "scissors"
Your choice should be random, don't follow the order of the sequence I gave you.

## Example
You should output
```
paper<EOS>
```
or 
```
rock<EOS>
```
or
```
scissors<EOS>
```

## Other instructions
Don't output anything besides one of the three strings.
Don't output the results in the last turn like "tie".
Don't pretend as if you are a human player.
    ''',
    '2': '''
Randomly output one of the following texts: "rock", "paper" or "scissors"
Your choice should be random, don't follow the order of the sequence I gave you.

## Example
You should output
```
paper<EOS>
```
or 
```
rock<EOS>
```
or
```
scissors<EOS>
```

## Other instructions
Don't output anything besides one of the three strings.
Don't output the results in the last turn like "tie".
Don't pretend as if you are a human player.
    ''',
}