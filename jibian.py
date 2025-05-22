import cv2
import numpy as np

# 图像尺寸
width = 640
height = 480
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

# 打开摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# 获取矫正映射
new_K, _ = cv2.getOptimalNewCameraMatrix(K, D, (width, height), 0)
map1, map2 = cv2.initUndistortRectifyMap(K, D, None, new_K, (width, height), cv2.CV_32FC1)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 矫正图像
    undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
    combined = np.hstack((frame, undistorted))

    # 显示原图和矫正后图像
    cv2.imshow('frame', combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
