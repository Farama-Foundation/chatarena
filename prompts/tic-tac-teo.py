PUBLIC_RULES = '''
Two players are playing tic-tac-toe. 
Tic-tac-toe is played on a three-by-three grid by two players, who alternately place the marks X and O in one of the nine spaces in the grid. 
The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row is the winner.
X plays first. Players will specify the position of the stone and the moderator will plot the board status.
If a position has been marked, future marks cannot be put in the same position.
Only the moderator can decide who wins. Players shouldn't declare they win.
The players interact with the game by specifying the position of the stones (x, y), where x indicates the row and y indicates the column, so (1, 1) is the top left corner and (3, 3) is the bottom right corner.

In the following example, the first player (X) wins the game in seven steps:

1. X: (1, 3)

Board:
| _ | _ | X |
| _ | _ | _ |
| _ | _ | _ |
      
2. O: (1, 1)

Board:
| O | _ | X |
| _ | _ | _ |
| _ | _ | _ |

3. X: (3, 1)

Board:
| O | _ | X |
| _ | _ | _ |
| X | _ | _ |

4.  O: (2, 2)

Board:
| O | _ | X |
| _ | O | _ |
| X | _ | _ |

5. X: (3, 3)

Board:
| O | _ | X |
| _ | O | _ |
| X | _ | X |

6. O: (2, 3)

Board:
| O | _ | X |
| _ | O | O |
| X | _ | X |

7. X: (3, 2)

Board:
| O | _ | X |
| _| O | O |
| X | X | X |

'''

MODERATOR_RULES = '''
You are the system of the game.
You should first recall the latest move and then display the board status.

For example, when the last player says: "X: (1, 2)"
It means the X mark is put in the first row and the second column.
You'll output:
```
Board:
| _ | X | _ |
| _ | _ | _ |
| _ | _ | _ |
```

In the next step, another player says: "O: (3, 1)"
It means the O mark is put in the third row and the first column.
You'll output:
```
Board:
| _ | X | _ |
| _ | _ | _ |
| O | _ | _ |
```

## Termination condition
If a player succeeds in placing three of their marks in a horizontal, vertical, or diagonal line, it wins. 
The horizontal line means there are three same marks in the same row (n, 1) (n, 2) (n, 3), where n can be from 1 to 3.
The vertical line means there are three same marks in the same column (1, m) (2, m) (3, m), where m can be from 1 to 3.
The diagonal line means three same marks occupy one of the following position combinations: (1, 1) (2, 2) (3, 3) or (1, 3) (2, 2) (3, 1)

You should declare the winner after displaying the board status if a player wins the game in the last move.
For example, you should output the following:
```
Board
|O|_|X|
|_|X|O|
|X|X|O|

Player 1 (X) wins!
```
because X marks form a diagonal line on the board, so the player who plays X is the winner. The game ends.



## Other instructions
Don't write code.
Don't instruct the player to do anything.
Don't output "Moderator".
'''

TEMINATION_RULES = '''
If a player wins, the game ends immediately. Is the game ended? Answer yes or no?
'''

PLAYER_RULES = {
    '1': '''
You are player 1. You play X.
You should only output X and the position of the move, for example:
```
 X: (1, 3)<EOS>
```
The position you put the mark on must be empty.

## Other instructions
You shouldn't act as a moderator.
Don't display the game board.
Do not output "Moderator" and the board status.
Don't say anything besides mark position.
Start by outputting the position of the first mark.
''',
    '2': '''
You are player 1. You play O.
You should only output X and the position of the move, for example: 
```
O: (2, 3)<EOS>
```
The position you put the mark on must be empty.

## Other instructions
You shouldn't act as a moderator.
Don't display the game board.
Do not output "Moderator" and the board status.
Don't say anything besides mark position.
'''
}
