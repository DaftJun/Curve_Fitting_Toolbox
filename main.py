# 文件名：main.py
# 作者名：吴嘉俊
# 最后一次修改的日期：2022/11/4 0:28
# 本文件是程序的主文件，并包含了所有前端GUI的代码

# 引入图像库 tkinter windnd
# 引入计算库 numpy sympy scipy
import tkinter as tk
from tkinter import END
from tkinter import ttk
from tkinter import filedialog
import windnd
from tkinter.messagebox import showinfo
import numpy as np
import scipy.io as scio

# 引入matplotlib的相关类，实现matplotlib在tkinter库中的嵌入
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# 引入自己编写的用于数据处理的类Curve_info()
from Curve_fitting import *

# 本程序中所有的数据相关的处理都将在Curve_info()类中实现
# 通过定义一个全局变量来完成整个程序的数据处理模块
Data = Curve_info()


# 自定义函数部分
# 主要是编写了前端GUI的交互函数

# center_window() 用于将GUI界面初始化在屏幕正中央，同时可以设置尺寸：
# 各形参说明如下：
# root: 函数作用的具体GUI窗体
# width：窗体宽度
# height：窗体高度
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


# refresh_listbox() 函数用于刷新listbox控件中的坐标
# 由于没有设置窗体与控件的循环刷新，每次修改数据后都需要调用
# 使GUI显示与后端数据相同步
def refresh_listbox():
    listbox1.delete(0, END)
    for item in Data.Text:
        listbox1.insert("end", item)


# add_item() 函数在单击‘增加’按钮后触发
# 将会读取输入的X与Y的数值，通过调用Curve_info().add(x,y)实现坐标点的增加
def add_item():
    x = text_x.get()
    y = text_y.get()
    if (is_number(x) == False):
        showinfo("错误", "请输入X的数值")
        return
    if (is_number(y) == False):
        showinfo("错误", "请输入Y的数值")
        return
    x = float(x)
    y = float(y)
    Data.add(x, y)
    refresh_listbox()


# delete_item() 函数由‘删除’按钮触发
# 通过调用Curve_info().delete(i)删除对应索引下的坐标
# 因为listbox()定义时默认单选，仅支持一次删除一个点
def delete_item():
    i = listbox1.curselection()
    # 由于 i 返回的是一个列表，这里通过for循环读取
    # 未来可以进一步适配多项的同时删除
    for k in i:
        Data.delete(k)
    refresh_listbox()


# change_item() 函数由‘修改’按钮触发
# 调用Curve_info().change(x,y,k)方法修改对应索引下的坐标
# 和删除一样，暂时只支持一次修改一个点
def change_item():
    i = listbox1.curselection()
    x = text_x.get()
    y = text_y.get()
    if (is_number(x) == False):
        showinfo("错误", "请输入X的数值")
        return
    if (is_number(y) == False):
        showinfo("错误", "请输入Y的数值")
        return
    x = float(x)
    y = float(y)
    # 由于 i 返回的是一个列表，这里通过for循环读取
    # 未来可以进一步适配多项的同时修改
    for k in i:
        Data.change(x, y, k)
    refresh_listbox()


# clean_Data() 函数由‘清空’按钮触发
# 调用Curve_info().__init__()方法对数据重新初始化
# 将会清空Data中的所有数据
def clean_Data():
    Data.__init__()
    refresh_listbox()


# browse() 函数由‘浏览’按钮触发
# 调用tkinter中的filedialog类，返回对应的文件路径，并刷新text控件
# 在最后调用read_file()函数完成后续的操作
def browse():
    # 通过方法askopenfilename()，限制选择单个文件
    filePath = filedialog.askopenfilename()
    # 刷新text控件的文本
    text.delete(0, END)
    text.insert(0, filePath)
    read_file()


# read_file() 函数是程序中读取文件的函数
# 为了减少重复的代码量，增加可读性与函数的独立性，read_file() 读取的文件路径来自text控件
# 外部函数可以通过将文件路径输入text控件的文本框后，调用本函数实现文件的读取
# 读取成功后，通过调用Curve_info().refresh()方法完成数据的更新
def read_file():
    msg = text.get()
    if (msg[-3:] == 'mat'):
        # 调用scio包来读取'.mat'文件
        data = scio.loadmat(msg)
        x = data['x'].transpose()
        y = data['y'].transpose()
        x = x.reshape(len(x), )
        y = y.reshape(len(x), )
        Data.refresh(x, y)
        showinfo("载入mat文件", ['成功载入', msg])

    # 调用numpy包来读取'.txt'与'.csv'文件
    elif (msg[-3:] == 'csv'):
        data = np.loadtxt(msg, delimiter=',')
        x = data[:, 0]
        y = data[:, 1]
        Data.refresh(x, y)
        showinfo("载入csv文件", ['成功载入', msg])
    elif (msg[-3:] == 'txt'):
        data = np.loadtxt(msg, delimiter=',')
        x = data[:, 0]
        y = data[:, 1]
        Data.refresh(x, y)
        showinfo("载入txt文件", ['成功载入', msg])

    # 异常情况的处理
    elif (msg == ""):
        info = "输入文件路径"
        text.delete(0, END)
        text.insert(0, info)
    else:
        showinfo("警告", ['无法读取!'])
    refresh_listbox()


# order_display() 函数用于控制‘阶数’文本与输入框的显示
# 当Combobox选中的是最小二乘近似等支持自定义阶数的算法时，将显示阶数的文本与输入框，反之将隐藏相关控件
def order_display(event):
    str = cbox.get()
    if (str == 'Least Square Approximation' or str == 'Trigonometric Polynomial Approximation'):
        label_order.place(x=1260, y=300, width=50)
        label4.place(x=1200, y=294)
    else:
        # place_forget()可以隐藏相关控件
        label_order.place_forget()
        label4.place_forget()


# dragged_files()函数将返回拖入的文件的路径
# 在刷新text控件后调用read_files()读取文件
def dragged_files(files):
    msg = '\n'.join((item.decode('gbk') for item in files))
    text.delete(0, END)
    text.insert(0, msg)
    read_file()


# calculate() 函数由‘计算’按钮触发
# 调用Curve_info()类中的对应算法函数完成计算，并将返回的计算结果刷新在text_output文本框控件中
def calculate():
    if (len(Data.X) < 2):
        showinfo("警告", ['点数过少'])
        return

    str = cbox.get()
    if (str == 'Lagrange Polymial'):
        str1 = Data.Lagrange_polynomials()
        text_output.delete('1.0', END)
        text_output.insert('1.0', str1)
    elif (str == 'Cubic Spline Interpolation'):
        str1 = Data.Cubic_Spline_Interpolation()
        text_output.delete('1.0', END)
        text_output.insert('1.0', str1)
    elif (str == 'Least Square Approximation'):
        s = label_order.get()
        if (s.isdigit()):
            str1 = Data.Least_Square_Approximation(int(s))
            text_output.delete('1.0', END)
            text_output.insert('1.0', str1)
        else:
            showinfo("警告", ['阶数必须为正整数'])
    elif (str == 'Trigonometric Polynomial Approximation'):
        s = label_order.get()
        if (s.isdigit()):
            str1 = Data.Trigonometric_Polynomial_Approximation(int(s))
            text_output.delete('1.0', END)
            text_output.insert('1.0', str1)
        else:
            showinfo("警告", ['阶数必须为正整数'])
    else:
        showinfo("警告", ['请选择算法'])


# draw_func() 函数由‘绘制’按钮触发
# 调用matplotlib库中的相关方法绘制函数
# 数据则从Curve_info()里的Out_x与Out_y读取
def draw_func():
    fig.clf()
    ax = fig.add_subplot(111)
    line1 = ax.scatter(Data.X, Data.Y, c='white', edgecolors="red")
    line2, = ax.plot(np.array(Data.Out_x), np.array(Data.Out_y))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid()
    canvas.draw()


# 主函数部分
# 本部分主要是定义了窗体的相关控件与对应的交互行为
if __name__ == "__main__":
    # 初始化主窗体
    # 限定窗体大小恒为1366x768
    # 所有控件将通过place()函数实现精确的定位，方便调整
    root = tk.Tk()
    root.iconphoto(True, tk.PhotoImage(file='Matlab_Logo.png'))
    center_window(root, 1366, 768)
    root.resizable(0, 0)
    root.title('Curve Fitting Toolbox')

    # 调用windnd包实现文件的拖入
    # 将调用dragged_files() 函数完成相关操作
    windnd.hook_dropfiles(root, func=dragged_files)

    # '浏览'按钮的位置
    btn2 = tk.Button(root, text='浏览', command=browse)
    btn2.config(font=("微软雅黑", 18))
    btn2.place(x=578, y=30, width=80, height=35)

    # '读取'按钮的位置
    btn3 = tk.Button(root, text='读取', command=read_file)
    btn3.config(font=("微软雅黑", 18))
    btn3.place(x=673, y=30, width=80, height=35)

    # 画布位置
    fig = Figure()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.place(x=20, y=718, width=738, height=40)
    canvas.get_tk_widget().place(x=20, y=90, width=738, height=628)

    # “读取文件” 文本框
    label = tk.Label(root, text="读取文件：", font=('微软雅黑', 18, 'bold italic'),
                     # 设置标签内容区大小
                     width=8, height=1)
    label.place(x=20, y=30)

    # 显示读取文件的路径的Text控件
    text = tk.Entry(root)
    text.configure(font=('微软雅黑', 18))
    text.place(x=140, y=30, width=428, height=35)
    text.insert(0, '输入文件路径')

    # 两个标签，分别用于提示输入 x 和 y
    label1 = tk.Label(root, text="X:", font=('微软雅黑', 18, 'bold italic'),
                      # 设置标签内容区大小
                      width=2, height=1,
                      # 设置填充区距离、边框宽度和其样式（凹陷式）
                      padx=1, pady=1)
    label1.place(x=830, y=30)

    label2 = tk.Label(root, text="Y:", font=('微软雅黑', 18, 'bold italic'),
                      width=2, height=1,
                      padx=1, pady=1)
    label2.place(x=1010, y=30)

    # 两个文本框用于输入坐标 X 与 Y
    text_x = tk.Entry(root)
    text_x.configure(font=('微软雅黑', 18))
    text_x.place(x=880, y=30, width=100, height=35)

    text_y = tk.Entry(root)
    text_y.configure(font=('微软雅黑', 18))
    text_y.place(x=1060, y=30, width=100, height=35)

    # '已有数据'文本
    label3 = tk.Label(root, text="已有数据:", font=('微软雅黑', 14, 'bold italic'),
                      width=7, height=1,
                      padx=1, pady=1)
    label3.place(x=830, y=90)

    # 显示已有坐标[x,y]的Listbox控件
    # 进一步要支持多选等操作，可以修改selectmode参数
    # 例：listbox1 = tk.Listbox(root,font=("Helvetica",14),selectmode = EXTENDED)
    listbox1 = tk.Listbox(root, font=("Helvetica", 14))
    listbox1.place(x=830, y=125, width=500, height=150)

    # ‘增加’按钮
    btn4 = tk.Button(root, text='增加', command=add_item)
    btn4.config(font=("微软雅黑", 17))
    btn4.place(x=1185, y=20, width=70, height=35)

    # ‘删除’按钮
    btn5 = tk.Button(root, text='删除', command=delete_item)
    btn5.config(font=("微软雅黑", 17))
    btn5.place(x=1275, y=20, width=70, height=35)

    # '修改'按钮
    btn7 = tk.Button(root, text='修改', command=change_item)
    btn7.config(font=("微软雅黑", 17))
    btn7.place(x=1185, y=65, width=70, height=35)

    # ‘清空’按钮
    btn6 = tk.Button(root, text='清空', command=clean_Data)
    btn6.config(font=("微软雅黑", 17))
    btn6.place(x=1275, y=65, width=70, height=35)

    # '拟合算法'文本
    label3 = tk.Label(root, text="拟合算法:", font=('微软雅黑', 14, 'bold italic'),
                      width=7, height=1,
                      padx=1, pady=1)
    label3.place(x=830, y=294)

    # 下拉菜单选择算法
    cbox = ttk.Combobox(root)
    cbox.place(x=930, y=300, width=250)
    cbox['value'] = ('Lagrange Polymial', 'Cubic Spline Interpolation', 'Least Square Approximation',
                     'Trigonometric Polynomial Approximation')
    # 通过cbox.bind()与对应的event实现每选中一项，都将调用一次order_display()函数
    cbox.bind("<<ComboboxSelected>>", func=order_display)

    # '阶数'文本 与 下拉框 ,这里不调用place()放置控件
    # 通过order_display()函数控制显示与否
    label4 = tk.Label(root, text="阶数:", font=('微软雅黑', 14, 'bold italic'),
                      width=4, height=1,
                      padx=1, pady=1)
    label_order = tk.Entry(root, font=("微软雅黑", 11))

    # ‘拟合结果’文本
    label5 = tk.Label(root, text="拟合结果:", font=('微软雅黑', 14, 'bold italic'),
                      width=7, height=1,
                      padx=1, pady=1)
    label5.place(x=830, y=334)

    # 输出拟合结果的文本框
    text_output = tk.Text(root, width=55, height=16, undo=True)
    text_output.place(x=830, y=370)
    text_output.configure(font=("微软雅黑", 11, "bold"))

    # '计算'按钮的位置
    btn1 = tk.Button(root, text='计算', command=calculate)
    btn1.config(font=("微软雅黑", 18, "bold"))
    btn1.place(x=920, y=698, width=100, height=40)

    # '绘制'按钮的位置
    btn9 = tk.Button(root, text='绘制', command=draw_func)
    btn9.config(font=("微软雅黑", 18, "bold"))
    btn9.place(x=1140, y=698, width=100, height=40)

    # 显示窗口
    root.mainloop()
