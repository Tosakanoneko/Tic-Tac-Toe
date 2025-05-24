import cv2
import numpy as np
from utils import get_hsv_mask, get_cb_settings, get_white_settings, get_black_settings, load_roi_settings

white_lower, white_upper = get_white_settings()
black_lower, black_upper = get_black_settings()

def get_cb_state(frame, roi_x, roi_y, roi_length):
    """获取棋盘状态"""
    black_count, white_count = 0, 0
    board = [[" "]*3 for _ in range(3)]
    for x in range(3):
        for y in range(3):
            piece = frame[roi_y+x*roi_length//3:roi_y+x*roi_length//3+roi_length//3, roi_x+y*roi_length//3:roi_x+y*roi_length//3+roi_length//3]
            white_mask = get_hsv_mask(piece, white_lower, white_upper)
            white_pix = cv2.countNonZero(white_mask)
            print(f"white_count: {white_pix}")
            if white_pix > 600:
                board[x][y] = "O"
                white_count += 1
                continue
            black_mask = get_hsv_mask(piece, black_lower, black_upper)
            black_pix = cv2.countNonZero(black_mask)
            print(f"black_count: {black_pix}")
            if black_pix > 600:
                board[x][y] = "X"
                black_count += 1
    return board, black_count, white_count

def print_board(board):
    for row in board:
        print("\n".join([" | ".join(row)]))
        print("——|———|———")

def draw_virtual_board(board, size):
    """
    输入：
        board: 3×3 的二维列表，每个元素是 "X"、"O" 或者 " "
    输出：
        返回一张 480×480×3 的 BGR 图像，显示棋盘和棋子
    """
    # 参数
    cell = size // 3         # 每格大小 160
    line_color = (0, 0, 0)   # 网格线颜色：黑
    thickness_line = 2       # 网格线粗细
    color_X = (0, 0, 0)    # X：红色 (BGR)
    color_O = (255, 255, 255)    # O：蓝色 (BGR)
    margin = 20              # 棋子与格子边缘的间距
    bg_color = (209, 60, 129)
    
    # 创建白色背景
    img = np.ones((size, size, 3), dtype=np.uint8)
    img[:] = bg_color

    # 画网格线
    for i in range(1, 3):
        # 横线
        cv2.line(img, (0, i*cell), (size, i*cell), line_color, thickness_line)
        # 竖线
        cv2.line(img, (i*cell, 0), (i*cell, size), line_color, thickness_line)

    # 画棋子
    for i in range(3):
        for j in range(3):
            piece = board[i][j]
            x0 = j * cell
            y0 = i * cell
            cx = x0 + cell // 2
            cy = y0 + cell // 2

            if piece == "O":
                # 画圆
                radius = (cell - 2*margin) // 2
                cv2.circle(img, (cx, cy), radius, color_O, -1)
            elif piece == "X":
                radius = (cell - 2*margin) // 2
                cv2.circle(img, (cx, cy), radius, color_X, -1)

    return img

if __name__ == "__main__":
    board = [
        ["O", " ", " "],
        ["O", "X", " "],
        ["X", " ", " "]
    ]
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.imshow("frame", draw_virtual_board(board))
    # cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # # 加载已有 HSV 设置
    # cb_lower, cb_upper = get_cb_settings()
    # white_lower, white_upper = get_white_settings()
    # black_lower, black_upper = get_black_settings()
    # roi_x, roi_y, roi_length = load_roi_settings()
    
    # # 打开摄像头
    # cap = cv2.VideoCapture(0)
    
    # # 创建用于显示画面和掩膜拼接的窗口
    # cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        
    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
    #     frame = frame[:, 80: 560]
    #     cb_mask = get_hsv_mask(frame, cb_lower, cb_upper)
    #     white_mask = get_hsv_mask(frame, white_lower, white_upper)
    #     black_mask = get_hsv_mask(frame, black_lower, black_upper)
    #     cb_mask_all = cv2.bitwise_or(cb_mask[roi_y:roi_y+roi_length, roi_x:roi_x+roi_length], white_mask[roi_y:roi_y+roi_length, roi_x:roi_x+roi_length])
    #     cb_mask_all = cv2.bitwise_or(cb_mask_all, black_mask[roi_y:roi_y+roi_length, roi_x:roi_x+roi_length])
    #     board_mask = np.zeros(cb_mask.shape, dtype=np.uint8)
    #     board_mask[roi_y:roi_y+roi_length, roi_x:roi_x+roi_length] = cb_mask_all
    
    #     # 将 mask 转为 BGR 并调整大小与原图一致
    #     mask_bgr = cv2.cvtColor(board_mask, cv2.COLOR_GRAY2BGR)
    
    #     # 显示
    #     cv2.imshow('frame', mask_bgr)
    
    #     key = cv2.waitKey(1) & 0xFF
    #     if key == 27:
    #         break
    #     elif key == ord('s'):
    #         now_board, _, _ = get_cb_state(frame, roi_x, roi_y, roi_length)
    #         print_board(now_board)
        
    # cap.release()
    # cv2.destroyAllWindows()
