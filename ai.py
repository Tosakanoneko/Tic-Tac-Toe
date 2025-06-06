import math

def print_board(board):
    print("\n".join([" | ".join(row) for row in board]))
    print()

def is_winner(board, player):
    win_cond = [  # 横、竖、斜
        [(0,0), (0,1), (0,2)],
        [(1,0), (1,1), (1,2)],
        [(2,0), (2,1), (2,2)],
        [(0,0), (1,0), (2,0)],
        [(0,1), (1,1), (2,1)],
        [(0,2), (1,2), (2,2)],
        [(0,0), (1,1), (2,2)],
        [(0,2), (1,1), (2,0)],
    ]
    return any(all(board[x][y] == player for x, y in line) for line in win_cond)

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def get_available_moves(board):
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]

def minimax(board, depth, is_maximizing, player):
    """
    修改后的 minimax：考虑 depth，以便 AI 尽快获胜或拖延失败
    player：此次搜索中作为最大化一方的棋子 ("X" 或 "O")
    """
    opponent = "O" if player == "X" else "X"

    if is_winner(board, player):
        # 赢了：分数为 10 - depth（depth 越小，表示越快获胜，分数越高）
        return 10 - depth
    if is_winner(board, opponent):
        # 输了：分数为 depth - 10（depth 越小，表示越快被对方赢，分数越低）
        return depth - 10
    if is_full(board):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for r, c in get_available_moves(board):
            board[r][c] = player
            score = minimax(board, depth + 1, False, player)
            board[r][c] = " "
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = math.inf
        for r, c in get_available_moves(board):
            board[r][c] = opponent
            score = minimax(board, depth + 1, True, player)
            board[r][c] = " "
            best_score = min(best_score, score)
        return best_score

def best_move(board, player):
    """
    返回指定 player ("X" 或 "O") 的最佳行棋位置 (i, j)
    """
    best_score = -math.inf
    move = None
    for i, j in get_available_moves(board):
        board[i][j] = player
        score = minimax(board, 0, False, player)
        board[i][j] = " "
        if score > best_score:
            best_score = score
            move = (i, j)
    return move

def legal_judge(now_board, fore_board):
    legal = True
    start_illegal_x, start_illegal_y = None, None
    end_illegal_x, end_illegal_y = None, None
    for row in range(3):
        for col in range(3):
            if now_board[row][col] != fore_board[row][col]:
                if now_board[row][col] != " " and fore_board[row][col] == " ":
                    start_illegal_x, start_illegal_y = col, row
                    continue
                if fore_board[row][col] != " " and now_board[row][col] == " ":
                    legal = False
                    end_illegal_x, end_illegal_y = col, row
                    continue
    return legal, (start_illegal_x, start_illegal_y, end_illegal_x, end_illegal_y)

def main():
    board = [[" "]*3 for _ in range(3)]
    print("你是 X，AI 是 O\n")
    print_board(board)

    while True:
        # 玩家回合
        while True:
            try:
                move = input("请输入你的落子坐标 (行列，如 1 2): ")
                x, y = map(int, move.strip().split())
                if board[x][y] == " ":
                    board[x][y] = "X"
                    break
                else:
                    print("此处已有棋子，请重新输入")
            except:
                print("输入格式错误，请重新输入")
        print_board(board)

        if is_winner(board, "X"):
            print("你赢了！")
            break
        if is_full(board):
            print("平局！")
            break

        # AI 回合
        ai_x, ai_y = best_move(board)
        board[ai_x][ai_y] = "O"
        print("AI 落子：", ai_x, ai_y)
        print_board(board)

        if is_winner(board, "O"):
            print("AI 赢了！")
            break
        if is_full(board):
            print("平局！")
            break

def test_legal_judge():
    now_board = [["X", "O", " "], [" ", "X", "O"], [" ", " ", "X"]]
    fore_board = [["X", "O", "X"], [" ", " ", "O"], [" ", " ", "X"]]
    legal, illegal_coords = legal_judge(now_board, fore_board)
    print("合法:", legal)
    print("非法坐标:", illegal_coords)

if __name__ == "__main__":
    test_legal_judge()
