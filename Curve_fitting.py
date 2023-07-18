# 文件名：Curve_fitting.py
# 作者名：DaftJun
# 最后一次修改的日期：2022/11/7 14:06
# 最后修改内容：增加了计时器用于衡量算法效率，删除了类中无用的clean操作，直接调用初始化方法即可；
#               调整了拉格朗日多项式中部分代码的顺序
# 本文件是程序的后端，用于进行数据处理与算法运算
import time
import numpy as np
import sympy as sp

# Curve_info()类封装了整个程序的数据处理相关的操作
# 利用了Python面对对象的特性，所有数据处理的部分都必须在这个类中完成，更加方便管理
# Curve_info()类主要包括下列数据变量：
# X，Y: 列表，用于存储输入的坐标
# Text: 列表，内部元素为"(x,y)"形式，用于显示在主窗体的listbox中
# x: symbols符号变量，在计算拉格朗日内插多项式时用到
# Out_x,Out_y: np.array(),用于存储一批点集，供绘图函数直接调用
# Output: string，用于存储输出到拟合结果中的字符串
class Curve_info():
    def __init__(self):
        self.X = []
        self.Y = []
        self.Text = []
        self.x = sp.symbols('x')
        self.Out_x = np.array([])
        self.Out_y = np.array([])
        self.Output = ""

    # refresh() 方法将直接刷新X与Y
    # 注意，refresh() 方法将不会保留原来的数值
    def refresh(self,x,y):
        self.X = x.tolist()
        self.Y = y.tolist()
        self.Text = []
        for i in range(len(self.X)):
            self.Text.append(['(',str(self.X[i]),',',str(self.Y[i]),')'])
    
    # add() 方法向X和Y中添加一个点
    def add(self,x,y):
        self.X.append(x)
        self.Y.append(y)
        self.Text.append(['(',str(x),',',str(y),')'])

    # delete() 方法从 X 与 Y 中删除对应下标的点
    def delete(self,i):
        del self.X[i]
        del self.Y[i]
        del self.Text[i]

    # change() 方法改变X，Y中对应下标的点的值
    def change(self,x,y,i):
        self.X[i] = x
        self.Y[i] = y
        self.Text[i] = ['(',str(x),',',str(y),')']

    # Lagrange_polynomials() 拉格朗日多项式计算
    # 由于并不是计算某一个点的数值，而是直接计算整个多项式
    # 直接通过sympy的符号变量生成拉格朗日多项式
    # 输出说明：
    # self.Output()：将返回输出字符串
    def Lagrange_polynomials(self):
        # 计算拉格朗日多项式
        T1 = time.perf_counter() # 开始计时
        Px = 0
        for i in range(len(self.X)):
            fx = self.Y[i]
            for j in range(len(self.X)):
                if(i != j):fx = fx*(self.x-self.X[j])/(self.X[i]-self.X[j])
            Px = Px+fx
        T2 = time.perf_counter() # 算法结束计时
        print('算法运行时间:%s毫秒' % ((T2 - T1)*1000))
        # 由于 sympy 直接对公式进行带入数值运算的算法花费时间非常长
        # 这里通过for循环提取系数自己算速度更快
        # 原计算公式 y.append(Px.evalf(subs ={'x':i}))
        
        # 首先得到系数，存入a这一列表中
        a =[]
        Px = sp.expand(Px)
        for i in range(len(self.X)):
            a.append(Px.coeff(self.x**i))
        a[0] = Px.evalf(subs ={'x':0})
        # 然后，通过for循环完成数值的计算
        x = []
        y = []
        for i in np.arange(min(self.X),max(self.X)+1e-4,5e-3):
            x.append(i)
            fx = 0
            for j in range(len(self.X)):
                fx += a[j]*i**j
            y.append(fx)
        # 最终存入Out_x与Out_y中
        self.Out_x = np.array(x)
        self.Out_y = np.array(y)

        # 生成输出的文本
        self.Output = "Lagrange_polynomials:\n"+"    P(x)="
        for i in range(len(a)):
            if(i == 0 ):self.Output += "a0"
            else: self.Output += ("+a"+str(i)+"*x**"+str(i))
        # 生成输出系数相关的文本
        self.Output += "\n\nThe solution of each coefficient is as follows:"
        for i in range(len(a)):
            self.Output += ("\n        a"+str(i)+" = "+str(a[i]))
        
        T3 = time.perf_counter() # 整体流程结束计时
        print('总流程运行时间:%s毫秒' % ((T3 - T1)*1000))

        return self.Output

    # Cubic_Spline_Interpolation() 三次样条插值计算
    # 由于输入只有几个样本点，因而我们只能计算 Natural Splines
    # 输出说明：
    # self.Output()：将返回输出字符串
    # 算法参考书本 Theorem 3.11 完成
    def Cubic_Spline_Interpolation(self):
        self.Output = "Cubic_Spline_Interpolation:\n"+"P(x) = a[i] + b[i](x-x[i]) + c[i](x-x[i])**2 + d[i](x-x[i])**3"
        n = len(self.X)

        # 考虑到输入可能是无序的情况
        # 首先利用sorted函数将坐标重新排序，存入临时变量X与Y中
        X_sorted = sorted(enumerate(self.X), key=lambda x:x[1])
        sorted_inds = [m[0] for m in X_sorted]
        X = [m[1] for m in X_sorted]
        Y = []
        for i in range(n):
            Y.append(self.Y[sorted_inds[i]])

        T1 = time.perf_counter() # 开始计时

        # 可以直接计算h与a        
        h = np.zeros([n-1,])
        a = np.zeros([n,])
        
        # 计算矩阵并通过高斯赛德法求解出c序列
        A = np.zeros([n,n])
        b_m = np.zeros([n,1])
        x = np.zeros([n,1])
        for i in range(n):
            if(i < n-1):h[i] = X[i+1]-X[i]
            a[i] = Y[i]
        for i in range(n):
            if(i == 0 or (i == n-1)):
                A[i,i] = 1
                b_m[i] = 0
            else:
                A[i,i-1] = h[i-1]
                A[i,i] = 2*(h[i]+h[i-1])
                A[i,i+1] = h[i]
                b_m[i] = 3/h[i]*(a[i+1]-a[i])-3/h[i-1]*(a[i]-a[i-1])
        # 得到c系数的序列
        x = Gauss_Seidel_Iterative(A,b_m,x) 
        
        # 返回计算b与d对应的值
        x = x.reshape([n,])
        b = np.zeros([n-1,])
        d = np.zeros([n-1,])
        for i in range(n-1):
            b[i] = 1/h[i]*(a[i+1]-a[i])-h[i]/3*(2*x[i]+x[i+1])
            d[i] = (x[i+1]-x[i])/(3*h[i])
        # 到此步解出所有的系数

        T2 = time.perf_counter() # 算法结束计时
        print('算法运行时间:%s毫秒' % ((T2 - T1)*1000))

        # 生成输出的文本
        for i in range(n-1):
            str1 = "\n  ("+str(X[i])+"<x<"+str(X[i+1])+")  i="+str(i)+\
                "\n        a["+str(i)+"]="+str(a[i])+\
                "\n        b["+str(i)+"]="+str(b[i])+\
                "\n        c["+str(i)+"]="+str(x[i])+\
                "\n        d["+str(i)+"]="+str(d[i])
            self.Output = self.Output + str1

        # 计算点集给后续绘图函数调用
        x1 = []
        y1 = []
        for i in np.arange(X[0],X[n-1],1e-4):
            x1.append(i)
            for j in range(n-1):
                if(X[j+1] >= i >= X[j]):
                    fx = a[j]+b[j]*(i-X[j])+x[j]*(i-X[j])**2+d[j]*(i-X[j])**3
            y1.append(fx)            
        self.Out_x = np.array(x1)
        self.Out_y = np.array(y1)

        T3 = time.perf_counter() # 整体流程结束计时
        print('总流程运行时间:%s毫秒' % ((T3 - T1)*1000))

        return self.Output

    # Least_Square_Approximation(n)方法 用于计算n阶最小二乘近似
    # 形参说明：
    # n: 多项式拟合的阶数
    # 输出说明：
    # self.Output()：将返回输出字符串
    # 算法参考：Chapter 8.1
    def Least_Square_Approximation(self,n):

        T1 = time.perf_counter() # 开始计时

        A = np.zeros([n+1,n+1])
        b = np.zeros([n+1,1])
        x = np.zeros([n+1,1])
        
        # 各偏导等于0在最终可以得到一组线性方程组
        # 计算各个系数，并通过高斯-塞德法求解
        for i in range(2*n+1):
            tmp_A = 0
            tmp_b = 0
            for j in range(len(self.X)):
                tmp_A += self.X[j]**i
                if(i <= n):tmp_b += self.Y[j]*(self.X[j]**i)
            if(i <= n):b[i] = tmp_b
            for j,k in zip(range(0,i+1),range(i,-1,-1)):
                if(n >= j >= 0 and n >= k >= 0):A[k,j]=tmp_A
        x = Gauss_Seidel_Iterative(A,b,x)
        x = x.reshape([len(x),])
        
        T2 = time.perf_counter() # 算法结束计时
        print('算法运行时间:%s毫秒' % ((T2 - T1)*1000))

        # 生成点集用于绘图
        x1 = []
        y1 = []
        for i in np.arange(min(self.X),max(self.X),1e-4):
            x1.append(i)
            fx = 0
            for j in range(n+1):
                fx += x[j]*i**j
            y1.append(fx)
        self.Out_x = np.array(x1)
        self.Out_y = np.array(y1)
        
        # 计算Error
        Error = 0
        for i in range(len(self.X)):
            y_hat = 0
            for j in range(n+1):
                y_hat += x[j]*self.X[i]**j
            Error += (self.Y[i]-y_hat)**2
        
        # 生成输出字符串
        self.Output = "Least_Square_Approximation:\nP(x)="
        for i in range(len(x)):
            if(i == 0 ):self.Output += "a0"
            else: self.Output += ("+a"+str(i)+"*x**"+str(i))
        self.Output += "\n\nThe solution of each coefficient is as follows:"
        for i in range(len(x)):
            self.Output += ("\n        a"+str(i)+" = "+str(x[i]))
            
        self.Output += ("\n\nError = " + str(Error))

        T3 = time.perf_counter() # 整体流程结束计时
        print('总流程运行时间:%s毫秒' % ((T3 - T1)*1000))

        return self.Output
    # Trigonometric_Polynomial_Approximation(n)方法，用于计算n阶三角多项式逼近
    # 形参说明：
    # n: 多项式拟合的阶数
    # 输出说明：
    # self.Output()：将返回输出字符串
    # 算法参考：Chapter 8.5 Theorem 8.13
    def Trigonometric_Polynomial_Approximation(self,n):

        T1 = time.perf_counter() # 开始计时

        a = np.zeros([n+1,])
        b = np.zeros([n-1,])
        for k in range(n+1):
            for j in range(len(self.X)):
                if(k > 0 and k < n):
                    b[k-1] += self.Y[j]*np.sin(self.X[j])
                a[k] += self.Y[j]*np.cos(k*self.X[j])
            a[k] /= (len(self.X)/2)
            if(k > 0 and k < n):
                b[k-1] /= (len(self.X)/2)
        
        T2 = time.perf_counter() # 算法结束计时
        print('算法运行时间:%s毫秒' % ((T2 - T1)*1000))

        # 生成点集用于绘图
        x1 = []
        y1 = []
        for i in np.arange(min(self.X),max(self.X),1e-4):
            x1.append(i)
            fx = a[0]+a[n]*np.cos(n*i)
            for k in range(1,n):
                fx += a[k]*np.cos(k*i)+b[k-1]*np.sin(k*i)
            y1.append(fx)
        self.Out_x = np.array(x1)
        self.Out_y = np.array(y1)

        # 计算 Error
        Error = 0
        for i in range(len(self.X)):
            y_hat = a[0]+a[n]*np.cos(n*self.X[i])
            for k in range(1,n):
                y_hat += a[k]*np.cos(k*self.X[i])+b[k-1]*np.sin(k*self.X[i])
            Error += (self.Y[i]-y_hat)**2    

        # 生成字符串
        self.Output = ("Trigonometric_Polynomial_Approximation:\nS"+str(n)+"(x)="\
            +"a[0]/2+a[n]*cos(n*x)+∑(a[k]*cos(k*x)+b[k]*sin(k*x))"+\
            "\n        (for each k in [1,"+str(n-1)+"])\n"\
            +"\nThe solution of each coefficient is as follows:\n")
        for k in range(len(a)):
            self.Output += ("a["+str(k)+"] = "+str(a[k])+"\n")
        for k in range(len(b)):
            self.Output += ("\nb["+str(k+1)+"] = "+str(b[k]))
        self.Output += ("\n\n\nError = "+str(Error))

        T3 = time.perf_counter() # 整体流程结束计时
        print('总流程运行时间:%s毫秒' % ((T3 - T1)*1000))

        return self.Output

# Gauss_Seidel_Iterative(A,b,x) 高斯-塞德迭代法
# 本函数用于通过迭代的方法求解线性方程组
# 形参说明：
# A：矩阵A
# b：输出向量b
# x：待求解向量x的迭代初始值
# 输出说明：
# x: 最终解向量
# 参考算法：ALGORITHM 7.2
def Gauss_Seidel_Iterative(A,b,x):
    n = len(b)
    N = 1000
    TOL = 0.001
    flag = 1

    # 计算对应的上三角，下三角矩阵并求逆
    T = np.zeros(A.shape)
    D_L = np.zeros(A.shape)
    U = np.zeros(A.shape)
    c = np.zeros(b.shape)
    for i in range(0,n):
        for j in range(0,n):
            if(i >= j): D_L[i,j] = A[i,j]
            else: U[i,j] = -A[i,j]
    T = np.dot(np.linalg.inv(D_L),U)
    c = np.dot(np.linalg.inv(D_L),b)

    # 迭代计算
    for k in range(0,N):
        x_next = np.dot(T,x)+c
        if(np.linalg.norm(x_next-x,ord=np.inf)<TOL): # 通过无穷范数判断是否找到符合要求的近似值
            # print('final result:')
            # print(x_next)
            print('Gauss Seidel Iterative Procedure completed successfully')
            flag = 0
            break
        x = x_next
    if(flag):
        print('Maximum number of iterations exceeded')
        # print(x)
    return x

# is_number(s)用于判定输入字符串s是否为数值
# 由于前端对控件的读取往往是一个字符串，通过本函数判定他们是否为数值
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False