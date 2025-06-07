import math

#单位 mm
l1 = 100 #机械臂第一节 100
l2 = 100 #机械臂第二节 100
d0 = 125#机械臂距离棋盘中心的距离 125
dx = -7 # -7
d1 = 30 #棋盘每格宽
d2 = 2  #棋盘线宽

def cal_degree_ver1(tar_id, rotate_angle):
    #初始化9个中心点
    target_point_list = [[], []]
    for i in range(9):
        target_point_list[0].append((i%3-1)*(d1+d2))
        target_point_list[1].append((i//3-1)*(d1+d2))

    #旋转棋盘（逆时针）
    for i in range(9):
        temp0 = target_point_list[0][i]
        temp1 = target_point_list[1][i]
        target_point_list[0][i] = math.cos(rotate_angle)*temp0  -  math.sin(rotate_angle)*temp1
        target_point_list[1][i] = math.sin(rotate_angle)*temp0  +  math.cos(rotate_angle)*temp1


    #解算机械臂的两个角度
    #step1目标点
    s_tar_x = target_point_list[0][tar_id-1]
    s_tar_y = target_point_list[1][tar_id-1]

    #step2:OP
    OP = ((s_tar_x)**2 + (s_tar_y + d0)**2)**0.5

    #step3:解三角形
    cos_theta = (l1**2+l2**2-OP**2)/(2*l1*l2)
    theta = math.acos(cos_theta)

    cos_gama = (l1**2+OP**2-l2**2)/(2*l1*OP)
    gama = math.acos(cos_gama)

    p_a = gama+math.atan2(s_tar_y+d0,s_tar_x)

    # #输出
    # print(math.degrees(p_a))   #第一个角度
    # print(math.degrees(theta)) #第二个角度
    return p_a, theta

def cal_degree(tar_id, rotate_angle):
    # 角度转弧度
    rotate_angle = math.radians(rotate_angle)

    #初始化9个中心点
    target_point_list = [[], []]
    for i in range(9):
        target_point_list[0].append((i%3-1)*(d1+d2))
        target_point_list[1].append((i//3-1)*(d1+d2))

    #旋转棋盘（逆时针）
    for i in range(9):
        temp0 = target_point_list[0][i]
        temp1 = target_point_list[1][i]
        target_point_list[0][i] = math.cos(rotate_angle)*temp0  -  math.sin(rotate_angle)*temp1
        target_point_list[1][i] = math.sin(rotate_angle)*temp0  +  math.cos(rotate_angle)*temp1


    #解算机械臂的两个角度
    #step1目标点
    s_tar_x = target_point_list[0][tar_id-1]
    s_tar_y = target_point_list[1][tar_id-1]

    #step2:OP
    OP = ((s_tar_x + dx)**2 + (s_tar_y + d0)**2)**0.5

    #step3:解三角形
    cos_theta = (l1**2+l2**2-OP**2)/(2*l1*l2)
    theta = math.acos(cos_theta)

    cos_gama = (l1**2+OP**2-l2**2)/(2*l1*OP)
    gama = math.acos(cos_gama)

    p_a = gama+math.atan2(s_tar_y+d0,s_tar_x + dx)
    return p_a, theta


if __name__ == "__main__":
    #输入：棋盘旋转角度
    rotate_angle = math.radians(30)
    tar_id = 1
    cal_degree(tar_id, rotate_angle)






