import serial
import time

def main():
    # 串口参数设置
    port = '/dev/ttyUSB0'         # 请修改为你的串口号，例如 '/dev/ttyUSB0'
    baudrate = 115200
    timeout = 0.1

    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"✅ 串口 {port} 已打开，开始接收数据...\n按 Ctrl+C 退出")

        while True:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                hex_str = data.hex(' ')
                ascii_str = ''.join([chr(b) if 32 <= b < 127 else '.' for b in data])
                print(f"[{time.strftime('%H:%M:%S')}] HEX: {hex_str}  | ASCII: {ascii_str}")
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n❎ 接收中断，程序退出")
    except Exception as e:
        print("❌ 串口打开或接收失败：", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 串口已关闭")

if __name__ == '__main__':
    main()
