import cv2
import numpy as np
import time
from utils import *
from chessboard import *
from ai import *
from comm import comm_agent
import copy
import threading
from rotate import rotate_image

if __name__ == "__main__":
    current_turn = 0
    now_board_count = 0
    HUMAN_TURN = 1
    AI_TURN = -1
    recover_op = False
    steady_det = False
    fore_board = [[" "]*3 for _ in range(3)]

    # 加载已有 HSV 设置
    cb_lower, cb_upper = get_cb_settings()
    white_lower, white_upper = get_white_settings()
    black_lower, black_upper = get_black_settings()
    roi_x, roi_y, roi_length = load_roi_settings()
    map1, map2 = mono_correct()
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    # 创建用于显示画面和掩膜拼接的窗口
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.namedWindow('ori_frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('ori_frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    now_board = [[" "]*3 for _ in range(3)]
    now_board_list = []

    current_turn = AI_TURN

    agent = comm_agent()
    agent_thread = threading.Thread(target=agent.rcv)
    agent_thread.setDaemon(True)
    agent_thread.start()
        
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        time.sleep(0.01)
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = get_roi_frame(roi_x, roi_y, roi_length, frame)
        frame = rotate_image(frame, agent.board_rotate_deg)
        ori_frame = frame.copy()
        hc, wc = ori_frame.shape[:2]
        new_x = (wc - roi_length) // 2
        new_y = (hc - roi_length) // 2
        # ori_frame = cv2.circle(ori_frame, (ori_frame.shape[1]//2, ori_frame.shape[0]//2), 3, (0,0,255), -1)
        # ori_frame = draw_board(ori_frame, new_x, new_y, roi_length)
        # frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
    
        # 显示
        board_img = draw_virtual_board(now_board, frame.shape[0])
        combined = np.hstack((frame, board_img))
        # cv2.putText(combined, "test", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2 )
        cv2.imshow('frame', combined)
        # cv2.imshow('ori_frame', ori_frame)
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
        elif key == ord('r') or agent.clear_board:
            if agent.clear_board: agent.clear_board = False
            now_board = [[" "]*3 for _ in range(3)]
            fore_board = [[" "]*3 for _ in range(3)]

        if not agent.start_detect:
            continue
        
        now_board_tmp, black_count, white_count = get_cb_state(ori_frame, new_x, new_y, roi_length)
        print_board(now_board_tmp)
        now_board_list.append(now_board_tmp)
        if len(now_board_list) == 3:
            # print("33333")
            first = now_board_list[0]
            if all(first == board for board in now_board_list):
                now_board = copy.deepcopy(first)
                steady_det = True
            else:
                print("检测不稳定，重新检测")
                steady_det = False
            now_board_list = []
            
        if not steady_det:
            continue
        steady_det = False
        print_board(now_board)

        legal, illegal_coords = legal_judge(now_board, fore_board)
        if not legal:
            start_illegal_x, start_illegal_y, end_illegal_x, end_illegal_y = illegal_coords
            print(f"落子{start_illegal_x}, {start_illegal_y}不合法！请归位到{end_illegal_x}, {end_illegal_y}")
            agent.recover(start_illegal_x, start_illegal_y, end_illegal_x, end_illegal_y)
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
            print("当前回合：AI")
            if is_winner(now_board, AI_chess):
                print("AI 赢了！")
            if is_full(now_board):
                print("平局！")
                agent.start_detect = False
                continue
        elif current_turn == HUMAN_TURN:
            print("当前回合：人类")
            if is_winner(now_board, HUMAN_chess):
                print("玩家赢了！")
            if is_full(now_board):
                print("平局！")
                agent.start_detect = False
                continue
                
            ai_x, ai_y = best_move(now_board, AI_chess)
            print("AI 落子：", ai_x, ai_y)
            case = 0 if AI_chess == "X" else 1
            agent.send_xy(case, ai_x, ai_y)

        fore_board = copy.deepcopy(now_board)
        agent.start_detect = False
        
    cap.release()
    cv2.destroyAllWindows()
