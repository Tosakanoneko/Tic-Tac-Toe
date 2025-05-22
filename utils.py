import cv2
import numpy as np
import json
import os
import argparse



def mono_correct():
    # 相机内参
    fx = 492.796460
    fy = 490.909300
    cx = 293.882125
    cy = 234.739797

    # 畸变参数
    k1 = 0.128403
    k2 = -0.150055
    p1 = -0.010989
    p2 = 0.001802


    # 相机矩阵
    K = np.array([[fx,  0, cx],
                  [ 0, fy, cy],
                  [ 0,  0,  1]], dtype=np.float32)

    # 畸变系数
    D = np.array([k1, k2, p1, p2], dtype=np.float32)
    new_K, _ = cv2.getOptimalNewCameraMatrix(K, D, (640, 480), 0)
    map1, map2 = cv2.initUndistortRectifyMap(K, D, None, new_K, (640, 480), cv2.CV_32FC1)
    return map1, map2

def nothing(x):
    pass

def save_hsv_settings(settings, filename='blackchess_hsv.json'):
    """保存HSV设置到JSON文件"""
    with open(filename, 'w') as f:
        json.dump(settings, f)

def save_roi_settings(settings, filename='roi.json'):
    """保存ROI设置到JSON文件"""
    with open(filename, 'w') as f:
        json.dump(settings, f)

def get_cb_settings():
    cb_h_min, cb_h_max, cb_s_min, cb_s_max, cb_v_min, cb_v_max = load_hsv_settings(filename='board_hsv.json')
    return np.array([cb_h_min, cb_s_min, cb_v_min]), np.array([cb_h_max, cb_s_max, cb_v_max])

def get_white_settings():
    white_h_min, white_h_max, white_s_min, white_s_max, white_v_min, white_v_max = load_hsv_settings(filename='white_hsv.json')
    return np.array([white_h_min, white_s_min, white_v_min]), np.array([white_h_max, white_s_max, white_v_max])
    
def get_black_settings():
    black_h_min, black_h_max, black_s_min, black_s_max, black_v_min, black_v_max = load_hsv_settings(filename='black_hsv.json')
    return np.array([black_h_min, black_s_min, black_v_min]), np.array([black_h_max, black_s_max, black_v_max])

def load_hsv_settings(filename='chessboard_hsv.json'):
    """从JSON文件加载HSV设置"""
    default_settings = {
        'H_min': 0, 'H_max': 255,
        'S_min': 0, 'S_max': 255,
        'V_min': 0, 'V_max': 255
    }
    if os.path.exists(filename):
        try:
            hsv_settings = json.load(open(filename, 'r'))
            return hsv_settings['H_min'], hsv_settings['H_max'], \
            hsv_settings['S_min'], hsv_settings['S_max'], \
            hsv_settings['V_min'], hsv_settings['V_max']
        except:
            return default_settings['H_min'], default_settings['H_max'], \
            default_settings['S_min'], default_settings['S_max'], \
            default_settings['V_min'], default_settings['V_max']
    return

def load_roi_settings(filename='roi.json'):
    """从JSON文件加载ROI设置"""
    default_settings = {
        'x': 0, 'y': 0,
        'length': 480
    }
    if os.path.exists(filename):
        try:
            roi_settings = json.load(open(filename, 'r'))
            return roi_settings['x'], roi_settings['y'], \
            roi_settings['length']
        except:
            return default_settings['x'], default_settings['y'], \
            default_settings['length']
    return default_settings['x'], default_settings['y'], \
           default_settings['length']

def get_HsvBar_value():
    # 读取滑块
    h_min = cv2.getTrackbarPos('H_min', 'HSV adjust')
    h_max = cv2.getTrackbarPos('H_max', 'HSV adjust')
    s_min = cv2.getTrackbarPos('S_min', 'HSV adjust')
    s_max = cv2.getTrackbarPos('S_max', 'HSV adjust')
    v_min = cv2.getTrackbarPos('V_min', 'HSV adjust')
    v_max = cv2.getTrackbarPos('V_max', 'HSV adjust')
    return h_min, h_max, s_min, s_max, v_min, v_max

def get_RoiBar_value():
    # 读取滑块
    x = cv2.getTrackbarPos('x', 'ROI adjust')
    y = cv2.getTrackbarPos('y', 'ROI adjust')
    length = cv2.getTrackbarPos('length', 'ROI adjust')
    return x, y, length

def get_hsv_mask(frame, lower, upper):
    # 生成 HSV 掩膜
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    # # 对掩膜进行形态学操作
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def draw_board(frame, x, y, length):
    cv2.line(frame, (x+length//3,y), (x+length//3,y+length), (255, 255, 0), thickness=2, lineType=cv2.LINE_8, shift=0)
    cv2.line(frame, (x+2*length//3,y), (x+2*length//3,y+length), (255, 255, 0), thickness=2, lineType=cv2.LINE_8, shift=0)
    cv2.line(frame, (x,y+length//3), (x+length,y+length//3), (255, 255, 0), thickness=2, lineType=cv2.LINE_8, shift=0)
    cv2.line(frame, (x,y+2*length//3), (x+length,y+2*length//3), (255, 255, 0), thickness=2, lineType=cv2.LINE_8, shift=0)
    cv2.rectangle(frame, (x, y), (x + length, y + length), (255, 255, 0), 2)
    return frame

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-hsv', type=str, help='HSV settings file')
    parser.add_argument('-roi', type=str, help='roi settings file')
    args = parser.parse_args()
    
    if args.hsv:
        h_min, h_max, s_min, s_max, v_min, v_max = load_hsv_settings(args.hsv)
        # 创建 HSV 调节滑块窗口
        cv2.namedWindow('HSV adjust')
        cv2.createTrackbar('H_min', 'HSV adjust', h_min, 255, nothing)
        cv2.createTrackbar('H_max', 'HSV adjust', h_max, 255, nothing)
        cv2.createTrackbar('S_min', 'HSV adjust', s_min, 255, nothing)
        cv2.createTrackbar('S_max', 'HSV adjust', s_max, 255, nothing)
        cv2.createTrackbar('V_min', 'HSV adjust', v_min, 255, nothing)
        cv2.createTrackbar('V_max', 'HSV adjust', v_max, 255, nothing)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
    elif args.roi:
        x, y, length = load_roi_settings(args.roi)
        # 创建 ROI 调节滑块窗口
        cv2.namedWindow('ROI adjust')
        cv2.createTrackbar('x', 'ROI adjust', x, 480, nothing)
        cv2.createTrackbar('y', 'ROI adjust', y, 480, nothing)
        cv2.createTrackbar('length', 'ROI adjust', length, 480, nothing)
    else:
        print("请提供 -hsv 或 -roi 参数")
        exit(1)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
       
    # 创建用于显示画面和掩膜拼接的窗口
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    
    print("按 's' 键保存当前设置；按 ESC 键退出")
    map1, map2 = mono_correct()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 获取矫正映射
        undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
        frame = frame[:, 80: 560]
        
        if args.hsv:
            h_min, h_max, s_min, s_max, v_min, v_max = get_HsvBar_value()
            new_settings = {
                'H_min': h_min, 'H_max': h_max,
                'S_min': s_min, 'S_max': s_max,
                'V_min': v_min, 'V_max': v_max
            }
            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])
            mask = get_hsv_mask(frame, lower, upper)
    
            # 将 mask 转为 BGR 并调整大小与原图一致
            mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            # 拼接
            combined = np.hstack((frame, mask_bgr))
            # 显示
            cv2.imshow('frame', combined)
        elif args.roi:
            x, y, length = get_RoiBar_value()

            new_settings = {
                'x': x, 'y': y,
                'length': length
            }
            frame = draw_board(frame, x, y, length)
            cv2.circle(frame, (240,240), 3, (0, 0, 255), -1)
            # 显示
            cv2.imshow('frame', frame)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            if args.hsv:
                save_hsv_settings(new_settings, filename=args.hsv)
                print(">> HSV 设置已保存！")
            elif args.roi:
                save_roi_settings(new_settings, filename=args.roi)
                print(">> ROI 设置已保存！")
        elif key == 27:
            break
        
    cap.release()
    cv2.destroyAllWindows()
