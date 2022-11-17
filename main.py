# Untitled - By: STM32 -  5月 19 2021

import pyb
import sensor, image,time,lcd
from pyb import UART,Timer,LED

sensor.reset() #初始化摄像头
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#320*240

sensor.skip_frames()
sensor.set_auto_whitebal(False)      #关闭白平衡
sensor.set_auto_gain(False)          #关闭自动增益
clock = time.clock()
lcd.init()                           #Initialize the lcd screen.
uart = UART(3,115200,8,None,1)       #创建串口对象


# 红色阈值
pink_threshold =(41, 80, 24, 77, -8, 44)
# 黄色阈值
yellow_threshold = (80, 100, -10, 10, -9, 40)
# 绿色阈值
green_threshold   = (50, 95, -128, -30, -30, 55)

LED_Red = LED(1)
LED_Green = LED(2)
LED_Blue = LED(3)

show_numTab = ["0","1","2","3","4","5","6","7","8","9"]
returnData  = [0x55,0x02,0x92,0x02,0x02,0x00,0x00,0xBB]  #识别失败



#串口发送函数
def USART_Send(src,length):
    for i in range(length):
        uart.writechar(src[i])

# 路灯识别
def test(data):
    msg = 0x01#默认识别红色
    color_rgb = [0x55,0x02,0x91,0x03,0x00,0x00,0x00,0xBB] #交通灯识别数据
    rgb_return  = [0x55,0x02,0x91,0x05,0x00,0x00,0x00,0xBB]  #交通灯正在识别
    if (data[3] == 0x01):  # 启动识别
        num = 9
        while(num > 0):
            num-=1
            img = sensor.snapshot()
            blobs = img.find_blobs([pink_threshold, yellow_threshold, green_threshold], area_threshold=100,pixels_threshold=200)  # 二值图片
            if blobs:
                for b in blobs:
                    img.draw_circle(b[5], b[6], b[5] - b[0])  # rect
                    # 用矩形标记出目标颜色区域
                    img.draw_cross(b[5], b[6])
                    if (b.code() == 1):
                        msg = 0x01  # 红
                        print('红')
                    elif (b.code() == 2):
                        msg = 0x03  # 黄
                        print('黄')
                    elif (b.code() == 4):
                        msg = 0x02  # 绿
                        print('绿')

                    color_rgb[3] = msg
                    print(color_rgb)
                    for i in color_rgb: #发送结果
                        uart.writechar(i)
                    return
            for rrgb in rgb_return:#正在识别回传
                uart.writechar(rrgb)
                print('正在识别')
            pyb.delay(1000)
        for rdata in returnData:#识别失败回传
            uart.writechar(rdata)
# 二维码识别
def test1(data):
    runData = [0x55,0x02,0x92,0x03,0x02,0x00,0x00,0xBB]  #二维码正在识别
    if (data[3] == 0x01):  # 启动识别
        num1 = 9
        while (num1 > 0):
            num1 -= 1
            img1 = sensor.snapshot()
            img1.draw_string(100, 180, "open", color=[255, 0, 0])
            for code in img1.find_qrcodes():
                if (code):
                    tim.deinit()
                    qr_Tab = code.payload()
                    qr_Tab = qr_Tab[qr_Tab.rfind('/') + 1:]
                    uart.writechar(0x55)
                    uart.writechar(0x02)
                    uart.writechar(0x92)
                    uart.writechar(0x01)
                    uart.writechar(len(qr_Tab))
                    for qrdata in qr_Tab:
                        uart.writechar(ord(qrdata))
                    uart.writechar(0xBB)
                    print("识别成功")
                    print(code)
                    img1.draw_string(110, 40,"qr_CodeV1.0",color=[0,0,255])
                    lcd.display(img1)#打印识别图片
                    return
            for rdata in runData:#正在识别回传
                uart.writechar(rdata)
            print('正在识别')
            pyb.delay(1000)
        for rdata in returnData:#回传识别失败
            uart.writechar(rdata)
# 串口数据接收函数
def test2():
    data = uart.read(8)
    if( len(data) >= 8):
        if((data[0] == 0x55)&(data[1] == 0x02)&(data[7] == 0xBB)):
            if (data[2] == 0x92):#二维码识别
                test1(data)
            if(data[2] == 0x91):#路灯识别
                test(data)
                

while(1):
    if(uart.any()):#判断串口是否有数据
       test2() 



