import cv2
import numpy as np
from utils import *
from chessboard import *
from ai import *
from comm import comm_agent
import copy
import threading
from rotate import rotate_image

if __name__ == "__main__":
    current_turn = 0
    HUMAN_TURN = 1
    AI_TURN = -1
    recover_op = False
    fore_board = [[" "]*3 for _ in range(3)]

    # 加载已有 HSV 设置
    cb_lower, cb_upper = get_cb_settings()
    white_lower, white_upper = get_white_settings()
    black_lower, black_upper = get_black_settings()
    roi_x, roi_y, roi_length = load_roi_settings()
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    # 创建用于显示画面和掩膜拼接的窗口
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    now_board = [[" "]*3 for _ in range(3)]

    current_turn = AI_TURN

    agent = comm_agent()
    # agent_thread = threading.Thread(target=agent.rcv)
    # agent_thread.setDaemon(True)
    # agent_thread.start()
        
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = frame[:, 80: 560]
        frame = rotate_image(frame, agent.board_rotate_deg)
        cb_mask = get_hsv_mask(frame, cb_lower, cb_upper)
    
        # 将 mask 转为 BGR 并调整大小与原图一致
        mask_bgr = cv2.cvtColor(cb_mask, cv2.COLOR_GRAY2BGR)
    
        # 显示
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('s'):
            agent.start_detect = True
        elif key == ord('c'):
            agent.first_move *= -1
            if agent.first_move == AI_TURN:
                print("AI 先行")
            else:
                print("玩家先行")
        elif key == ord('r'):
            now_board = [[" "]*3 for _ in range(3)]
            fore_board = [[" "]*3 for _ in range(3)]
            print_board(now_board)

        if not agent.start_detect:
            continue
        
        now_board, black_count, white_count = get_cb_state(frame, roi_x, roi_y, roi_length)
        print_board(now_board)

        legal, illegal_coords = legal_judge(now_board, fore_board)
        if not legal:
            start_illegal_x, start_illegal_y, end_illegal_x, end_illegal_y = illegal_coords
            print(f"落子{start_illegal_x}, {start_illegal_y}不合法！请归位到{end_illegal_x}, {end_illegal_y}")
            # agent.sned(2, start_illegal_x, start_illegal_y)
            recover_op = True
            agent.start_detect = False #需要下位机告知恢复棋局完毕
            continue
        if recover_op:
            recover_op = False
            print("归位操作完成")
            agent.start_detect = False
            continue
        
        if white_count == black_count :
            current_turn = HUMAN_TURN if agent.first_move == AI_TURN else AI_TURN
        elif white_count < black_count:
            current_turn = AI_TURN if agent.first_move == AI_TURN else HUMAN_TURN
        else:
            print("棋盘状态异常！")
        AI_chess = "X" if agent.first_move == AI_TURN else "O"
        HUMAN_chess = "O" if agent.first_move == AI_TURN else "X"

        if current_turn == AI_TURN:
            if is_winner(now_board, AI_chess):
                print("AI 赢了！")
            if is_full(now_board):
                print("平局！")
        elif current_turn == HUMAN_TURN:
            if is_winner(now_board, HUMAN_chess):
                print("玩家赢了！")
            if is_full(now_board):
                print("平局！")
                
            ai_x, ai_y = best_move(now_board, AI_chess)
            print("AI 落子：", ai_x, ai_y)
            case = 0 if AI_chess == "X" else 1
            # agent.send(case, ai_x, ai_y)

        fore_board = copy.deepcopy(now_board)
        agent.start_detect = False
        
    cap.release()
    cv2.destroyAllWindows()
