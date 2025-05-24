import serial
import time
import cal_deg
import struct
import math

xy_remap_id = [
    [7, 8, 9],
    [4, 5, 6],
    [1, 2, 3]
]

id_remap_xy = [(0,2),(1,2),(2,2),
                (0,1),(1,1),(2,1),
                (0,0),(1,0),(2,0)]

class comm_agent():
    def __init__(self):
        self.ser = None
        self.open_ser()
        self.start_detect = False
        self.current_turn = -1
        self.first_move = -1
        self.board_rotate_deg = 0.0

    def open_ser(self):
        while True:
            try:
                self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=0.01)
                print("\n串口0已打开")
                break
            except serial.serialutil.SerialException:
                print("\n串口0未打开")
                try:
                    print("切换到串口1")
                    self.ser = serial.Serial(port='/dev/ttyUSB1', baudrate=9600, timeout=0.01)
                    print("串口1已打开")
                    break
                except serial.serialutil.SerialException:
                    print("串口1未打开")
                    time.sleep(0.5)

    def rcv_ver1(self): #第一版：接受4字节浮点16进制
        try:
            # 从串口读取一整行数据
            data = self.ser.readline()
            if data:
                if data.startswith(b'@') and data.endswith(b'\r\n'):
                    # 提取中间的字节数据
                    chess_loc = data[1]  # 去掉 '@' 和 '\r\n'
                    chess_loc = format(chess_loc, "x")
                    chess_loc = int(chess_loc)
                    if chess_loc >= 1 and chess_loc <= 9:
                        print("指定模式")
                        case = 3
                        board_rotate_deg_hex = data[2:6]
                        self.board_rotate_deg = struct.unpack("<f", board_rotate_deg_hex)[0]
                        rotate1, rotate2 = cal_deg.cal_degree(chess_loc, self.board_rotate_deg)
                        # print(f"棋盘旋转角度: {self.board_rotate_deg}, 机械臂角度: {rotate1}, {rotate2}")
                        print(f"下位机send数据: {case}, {chess_loc}, {rotate1}, {rotate2}")
                        self.send(self, case, rotate1, rotate2)
                    elif chess_loc == 10:
                        print("自动模式")
                        self.start_detect = True
                    elif chess_loc == 20:
                        print("仅旋转")
                        board_rotate_deg_hex = data[2:6]
                        self.board_rotate_deg = struct.unpack("<f", board_rotate_deg_hex)[0]
                        print(f"棋盘旋转角度: {self.board_rotate_deg}")
                    else:
                        print("棋盘位置不合法")
                elif data.startswith(b'#') and data.endswith(b'\r\n'):
                    first_move_data = data[1]
                    self.first_move = 1 if first_move_data == 1 else -1
                else:
                    print("接收到的数据格式无效：",data)
                print("data:",data)
            
        except serial.SerialException as e:
            print(f"串口通信错误: {e}")
        except ValueError as e:
            print(f"数据解析错误: {e}")

    def rcv(self): #第二版：接受二字节整型16进制 0~800
        try:
            # 从串口读取一整行数据
            data = self.ser.readline()
            if data:
                if data.startswith(b'@') and data.endswith(b'\r\n'):
                    # 提取中间的字节数据
                    chess_loc = data[1]  # 去掉 '@' 和 '\r\n'
                    chess_loc = format(chess_loc, "x")
                    chess_loc = int(chess_loc)
                    if chess_loc >= 1 and chess_loc <= 9:
                        print("指定模式：仅根据编号解算大小臂角度")
                        case = 3
                        rotate1, rotate2 = cal_deg.cal_degree(chess_loc, self.board_rotate_deg)
                        # print(f"棋盘旋转角度: {self.board_rotate_deg}, 机械臂角度: {rotate1}, {rotate2}")
                        print("当前编号：", chess_loc, f"解算角度：{round(rotate1/math.pi, 2)}Π, {round(rotate2/math.pi,2)}Π")
                        self.send_deg(case, rotate1, rotate2)
                    elif chess_loc == 10:
                        print("自动模式")
                        self.start_detect = True
                    elif chess_loc == 20:
                        print("仅接受棋盘旋转角度")
                        board_rotate_deg_ori = data[2:4]  # 二字节整型16进制 0~800
                        board_rotate_deg = int.from_bytes(board_rotate_deg_ori, byteorder='little')
                        self.board_rotate_deg = (board_rotate_deg - 400) * 0.1125
                        print(f"原始数据：{board_rotate_deg_ori},棋盘旋转角度: {self.board_rotate_deg}°")
                    else:
                        print("棋盘位置不合法")
                elif data.startswith(b'#') and data.endswith(b'\r\n'):
                    first_move_data = data[1]
                    self.first_move = 1 if first_move_data == 1 else -1
                else:
                    print("接收到的数据格式无效：",data)
                print("data:",data)
            
        except serial.SerialException as e:
            print(f"串口通信错误: {e}")
        except ValueError as e:
            print(f"数据解析错误: {e}")

    def send_ver1(self, case, x, y): # 第一版：发送4字节浮点16进制
        id = xy_remap_id[y][x]
        rotate1, rotate2 = cal_deg.cal_degree(id, self.board_rotate_deg)

        case_bytes = case.to_bytes(1, byteorder='little')
        case_hex = case_bytes.hex()

        rotate1_bytes = struct.pack(">f", rotate1)  # 结果是 bytes 类型
        rotate1_hex = rotate1_bytes.hex()

        rotate2_bytes = struct.pack(">f", rotate2)  # 结果是 bytes 类型
        rotate2_hex = rotate2_bytes.hex()

        string = b'@'.hex()
        string += case_hex
        string += rotate1_hex
        string += rotate2_hex
        self.ser.write(bytes.fromhex(string))
        self.ser.write(bytes.fromhex(b'\r\n'.hex()))
        string += b'\r\n'.hex()
        print("case, x, y:", case, x, y)
        print(f"发送数据: {string}")
        
    def send_xy(self, case, x, y): # 第二版：发送2字节16进制.映射0~1000
        id = xy_remap_id[y][x]
        print("id:", id)
        rotate1, rotate2 = cal_deg.cal_degree(id, self.board_rotate_deg)
        print("ori:rotate1, rotate2, self.board_rotate_deg:", rotate1, rotate2, self.board_rotate_deg)

        # 旋转角度映射到0~1000
        rotate1 = int((rotate1) * 1000 / math.pi)
        rotate2 = int((rotate2) * 1000 / math.pi)
        print("remap:rotate1, rotate2:", rotate1, rotate2)

        case_bytes = case.to_bytes(1, byteorder='little')
        case_hex = case_bytes.hex()

        rotate1_bytes = rotate1.to_bytes(2, byteorder='little')
        rotate1_hex = rotate1_bytes.hex()

        rotate2_bytes = rotate2.to_bytes(2, byteorder='little')
        rotate2_hex = rotate2_bytes.hex()

        string = b'@'.hex()
        string += case_hex
        string += rotate1_hex
        string += rotate2_hex
        string += b'\r\n'.hex()
        self.ser.write(bytes.fromhex(string))
        print("case, x, y:", case, x, y)
        print(f"发送数据: {string}")

    def send_deg(self, case, rotate1, rotate2): # 第二版：发送2字节16进制.映射0~1000
        case_bytes = case.to_bytes(1, byteorder='little')
        case_hex = case_bytes.hex()

        # 旋转角度映射到0~1000
        rotate1 = int((rotate1) * 1000 / math.pi)
        rotate2 = int((rotate2) * 1000 / math.pi)
        print("remap:rotate1, rotate2:", rotate1, rotate2)

        rotate1_bytes = rotate1.to_bytes(2, byteorder='little')
        rotate1_hex = rotate1_bytes.hex()

        rotate2_bytes = rotate2.to_bytes(2, byteorder='little')
        rotate2_hex = rotate2_bytes.hex()

        string = b'@'.hex()
        string += case_hex
        string += rotate1_hex
        string += rotate2_hex
        string += b'\r\n'.hex()
        self.ser.write(bytes.fromhex(string))
        print(f"发送数据: {string}")

def test1():
    case = 1
    rotate1 = 30.0
    rotate2 = 45.0
    case_bytes = case.to_bytes(1, byteorder='little')
    case_hex = case_bytes.hex()

    rotate1_bytes = struct.pack("<f", rotate1)  # 结果是 bytes 类型
    rotate1_hex = rotate1_bytes.hex()

    rotate2_bytes = struct.pack("<f", rotate2)  # 结果是 bytes 类型
    rotate2_hex = rotate2_bytes.hex()

    string = b'@'.hex()
    string += case_hex
    string += rotate1_hex
    string += rotate2_hex
    string += b'\r\n'.hex()
    # self.ser.write(bytes.fromhex(string))
    print(f"发送数据: {string}")

    data = b'\x40\x05\x9A\x89\x7E\x44\x0D\x0A'
    board_rotate_deg_hex = data[2:6]
    print(board_rotate_deg_hex)
    board_rotate_deg = struct.unpack("<f", board_rotate_deg_hex)[0]
    print(board_rotate_deg)

def test2():
    agent = comm_agent()
    while True:
        agent.rcv()
        time.sleep(0.01)

def test3():
    agent = comm_agent()
    case = 3
    id = 5
    x, y = id_remap_xy[id-1]
    agent.send_xy(case, x, y)

if __name__ == "__main__":
    # print(xy_remap_id[1][0])
    test2()
    # test3()
