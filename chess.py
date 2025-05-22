import cv2
import numpy as np
import json
import os
from utils import get_hsv_mask, get_white_settings, get_black_settings


if __name__ == "__main__":
    # 加载已有 HSV 设置
    lower_white, upper_white = get_white_settings()
    lower_black, upper_black = get_black_settings()
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    # 创建用于显示画面和掩膜拼接的窗口
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    
    print("按 's' 键保存当前 HSV 设置；按 ESC 键退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        mask_white = get_hsv_mask(frame, lower_white, upper_white)
        mask_black = get_hsv_mask(frame, lower_black, upper_black)
    
        # 将 mask 转为 BGR 并调整大小与原图一致
        WhiteMask_bgr = cv2.cvtColor(mask_white, cv2.COLOR_GRAY2BGR)
        BlackMask_bgr = cv2.cvtColor(mask_black, cv2.COLOR_GRAY2BGR)
    
        # 拼接
        combined = np.hstack((frame, WhiteMask_bgr, BlackMask_bgr))
    
        # 显示
        cv2.imshow('frame', combined)
    
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        
    cap.release()
    cv2.destroyAllWindows()
