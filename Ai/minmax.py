board = ["-"] * 9
def show():
    print(board[0], board[1], board[2])
    print(board[3], board[4], board[5])
    print(board[6], board[7], board[8])


def winner(p):
    w = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in w:
        if board[a] == board[b] == board[c] == p:
            return True
    return False
    
turn = "X"
for _ in range(9):
    show()
    move = int(input(f"{turn}'s turn (1-9): ")) - 1
    if board[move] == "-":
        board[move] = turn
        if winner(turn):
            show()
            print(turn, "wins!")
            break
        turn = "O" if turn == "X" else "X"
    else:
        print("Spot taken. Try again.")
else:
    show()
    print("It's a tie!")

