import cv2
from comm import comm_agent
from utils import draw_board

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    angle = float(angle)
    angle = -round(angle, 2)  # 保留两位小数
    
    # 计算旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # 执行仿射变换
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def main():
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    angle = 0  # 初始旋转角度

    print("按 'a' 增加角度，按 'd' 减少角度，按 'q' 退出程序")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头图像")
            break
        frame = frame[:, 80: 560]

        rotated_frame = rotate_image(frame, angle)

        # 显示图像
        cv2.imshow("frame", rotated_frame)

        # 等待按键
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # 退出
            break
        elif key == ord('a'):  # 增加角度
            angle += 5
        elif key == ord('d'):  # 减少角度
            angle -= 5

    cap.release()
    cv2.destroyAllWindows()

def comm_test():
    agent = comm_agent()
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    while True:
        agent.rcv()
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头图像")
            break
        frame = frame[:, 80: 560]

        rotated_frame = rotate_image(frame, agent.board_rotate_deg)
        rotated_frame = draw_board(rotated_frame, 157, 157, 166)
        # 显示图像
        cv2.imshow("frame", rotated_frame)

        # 等待按键
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # 退出
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # comm_test()
    main()
