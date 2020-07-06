from tkinter import *                           #tk,图形化,用于在画板中框选截图范围,图形化展示等,内置库
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from time import sleep                          #延时工具,避免鼠标造成的误触动作
import os                                       #系统库,用于删除临时文件与暂停
from pip._internal import main as pipinstall    #pip安装库,自动安装缺失组件
import ctypes                                   #由于涉及鼠标坐标拾取,因此需要禁用高DPI缩放,利用ctypes实现,solution comes from https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
try:
    from PIL import ImageGrab                       #pillow,图像处理工具,用于截图,安装方法:pip install Pillow(注意切换镜像源,可提升速度)
    from PIL import Image                           #pillow,图像处理工具,安装方法:pip install Pillow(注意切换镜像源,可提升速度)
    from PIL import ImageTk
except:
    print("正在安装缺失组件,请稍后...[1/4]")            #国内镜像源速度较快,遂采用
    pipinstall(['install','-i','https://pypi.tuna.tsinghua.edu.cn/simple','Pillow'])
    from PIL import ImageGrab
    from PIL import Image
    from PIL import ImageTk
try:
    from pyzbar.pyzbar import decode as qrdecode    #pyzbar,二维码解码外部库,安装方法:pip install pyzbar
except:
    print("正在安装缺失组件,请稍后...[2/4]")            #国内镜像源速度较快,遂采用
    pipinstall(['install','-i','https://pypi.tuna.tsinghua.edu.cn/simple','pyzbar'])
    from pyzbar.pyzbar import decode as qrdecode
try:
    import qrcode                                   #qrcode,二维码生成外部库,安装方法:pip install qrcode
except:
    print("正在安装缺失组件,请稍后...[3/4]")            #国内镜像源速度较快,遂采用
    pipinstall(['install','-i','https://pypi.tuna.tsinghua.edu.cn/simple','qrcode'])
    import qrcode
try:
    import chardet                                  #chardet,文本编码识别工具,安装方法:pip install chardet
except:
    print("正在安装缺失组件,请稍后...[4/4]")            #国内镜像源速度较快,遂采用
    pipinstall(['install','-i','https://pypi.tuna.tsinghua.edu.cn/simple','chardet'])
    import chardet

#截图识别
def ScreenDecode():
    
    lastx, lasty = 0, 0

    #高DPI兼容
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)         #获取缩放比例

    #生成选择界面
    root = Toplevel()
    root.overrideredirect(True)                 #目前会导致左上两边出现1像素的条条
    root.attributes('-topmost',1)               #窗口置顶

    #截取全屏
    global fullscreen                           #全屏截图
    fullscreen = ImageGrab.grab()
    global fullscreentk                         #兼容TK的全屏截图
    fullscreentk = ImageTk.PhotoImage(image=fullscreen)

    #定义触发函数
    def mousePress(event):
        global lastx, lasty
        lastx, lasty = event.x, event.y

    def mouseMove(event):
        global lastdraw
        global lastx, lasty
        try:
            #删除刚画完的图形，防止各个图形重叠影响观感
            canvas.delete(lastdraw)
        except Exception as e:
            pass
        lastdraw = canvas.create_rectangle(lastx, lasty, event.x, event.y, outline='cornflowerblue', width=3)

    def mouseRelease(event):
        global lastx, lasty
        global fullscreen, pic
        try:
            canvas.delete(lastDraw)
        except Exception as e:
            pass
        sleep(0.1)
        #考虑鼠标左键从右下方按下而从左上方抬起的截图
        myleft, myright = sorted([lastx, event.x])
        mytop, mybottom = sorted([lasty, event.y])

        #关闭当前窗口
        root.destroy()
    
        size=(myleft,mytop,myright,mybottom)

        #截取图像
        if (myleft==myright or mytop==mybottom):
            pic = fullscreen
        else:
            pic = fullscreen.crop(size)

        #解码
        global outmessage
        outmessage = None
        piccode = qrdecode(pic)
        if(piccode == []):
            outmessage = 1
        else:
            outmessage = piccode
        #pic.close()                #为了后续展示,暂时不关闭

    def mouseExitWindow(event):
        global outmessage
        global pic
        pic = None
        sleep(0.3)
        outmessage = 0
        root.destroy()
    
    def escExitWindow(event):
        if event.keysym == "Escape":
            global outmessage
            global pic
            pic = None
            outmessage = 0
            root.destroy()

    #生成页面元素
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()

    canvas = Canvas(root, bg='black', bd=0, width=screenWidth*(ScaleFactor/100), height=screenHeight*(ScaleFactor/100))
    canvas.grid(column=0, row=0, sticky=(N, W, E, S))
    canvas.create_image(0,0,anchor='nw',image=fullscreentk)        #canvas.create_image(screenWidth/2,screenHeight/2,image=fullscreentk)
    canvas.create_rectangle(0,0,360,20,fill='black',outline='white')
    canvas.create_text(180, 10, text='按住左键框选识别区域,点击左键选中全屏,点击右键或按ESC键取消',fill='white')
    canvas.bind("<Button-1>", mousePress)
    canvas.bind("<B1-Motion>", mouseMove)
    canvas.bind("<ButtonRelease-1>", mouseRelease)
    canvas.bind("<Button-3>",mouseExitWindow)
    root.bind("<Key>",escExitWindow)

    #模态窗口
    root.grab_set()

    #设置焦点
    canvas.focus_set()

    root.wait_window()              #等待窗口关闭,solution comes from https://www.jb51.net/article/119817.htm
    return [outmessage,pic]

#识别结果展示
def showtext(showcode):

    #异常情况处理
    if showcode == 0:                                       #识别返回0:用户取消了操作
        return
    elif showcode == 1:
        messagebox.showinfo("提示","没有检测到二维码")          #识别返回1:没有检测到
        return

    root = Toplevel()
    root.title("识别结果")

    #初始窗口大小&位置
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = 500
    wh = 190
    x = (sw-ww) / 2
    y = (sh-wh) / 2
    root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))

    def watchdetail(event):
        item_text = treeview.item(treeview.selection(),"values")
        
        detailwin = Toplevel()
        detailwin.title("解析详情")

        ww = 500
        wh = 190
        x = (sw-ww) / 2
        y = (sh-wh) / 2
        detailwin.geometry("%dx%d+%d+%d" %(ww,wh,x,y))

        titlelabel = Label(detailwin,text='二维码解析详情')
        titlelabel.grid(column=0,row=0,columnspan=2,pady=8)

        typelabel = Label(detailwin,text='二维码类型')
        typelabel.grid(column=0,row=1,sticky=E,pady=6,ipadx=8)
        typetext = Entry(detailwin,width=10)
        typetext.grid(column=1,row=1,sticky=W,pady=6,ipadx=9)
        typetext.insert(0,item_text[0])

        codelabel = Label(detailwin,text='文本编码')
        codelabel.grid(column=0,row=2,sticky=E,pady=6,ipadx=8)
        codetext = Entry(detailwin,width=10)
        codetext.grid(column=1,row=2,sticky=W,pady=6,ipadx=9)
        codetext.insert(0,item_text[1])

        contlabel = Label(detailwin,text='解码内容')
        contlabel.grid(column=0,row=3,sticky=E,pady=6,ipadx=8)
        conttext = Entry(detailwin,width=55)
        conttext.grid(column=1,row=3,sticky=W,pady=6,ipadx=9)
        conttext.insert(0,item_text[2])

        if item_text[2].startswith("http://") or item_text[2].startswith("https://"):
            import webbrowser                               #用于调用浏览器打开网页
            netbutton = Button(detailwin,text="打开网页",width=8,command=lambda:webbrowser.open(item_text[2]),relief=GROOVE)
            netbutton.grid(column=0,row=4,columnspan=2,pady=8,sticky=E)
            quitbutton = Button(detailwin,text="关闭窗口",width=8,command=detailwin.destroy,relief=GROOVE)
            quitbutton.grid(column=0,row=4,columnspan=2,pady=8)
        else:
            quitbutton = Button(detailwin,text="关闭窗口",width=8,command=detailwin.destroy,relief=GROOVE)
            quitbutton.grid(column=0,row=4,columnspan=2,pady=8)

    piccount = len(showcode)
    if piccount <= 1:
        #重置窗口大小&位置
        ww = 500
        wh = 190
        x = (sw-ww) / 2
        y = (sh-wh) / 2
        root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))

        titlelabel = Label(root,text='识别到1个二维码')
        titlelabel.grid(column=0,row=0,columnspan=2,pady=8)

        typelabel = Label(root,text='二维码类型')
        typelabel.grid(column=0,row=1,sticky=E,pady=6,ipadx=8)
        typetext = Entry(root,width=10)
        typetext.grid(column=1,row=1,sticky=W,pady=6,ipadx=9)
        pictype = showcode[0][1]
        typetext.insert(0,pictype)

        codelabel = Label(root,text='文本编码')
        codelabel.grid(column=0,row=2,sticky=E,pady=6,ipadx=8)
        codetext = Entry(root,width=10)
        codetext.grid(column=1,row=2,sticky=W,pady=6,ipadx=9)
        codetype = chardet.detect(showcode[0][0])['encoding']
        codetext.insert(0,codetype)

        contlabel = Label(root,text='解码内容')
        contlabel.grid(column=0,row=3,sticky=E,pady=6,ipadx=8)
        conttext = Entry(root,width=55)
        conttext.grid(column=1,row=3,sticky=W,pady=6,ipadx=9)
        picstr = showcode[0][0].decode(encoding = codetype)
        conttext.insert(0,picstr)

        if picstr.startswith("http://") or picstr.startswith("https://"):
            import webbrowser                               #用于调用浏览器打开网页
            netbutton = Button(root,text="打开网页",width=8,command=lambda:webbrowser.open(picstr),relief=GROOVE)
            netbutton.grid(column=0,row=4,columnspan=2,pady=8,sticky=E)
            quitbutton = Button(root,text="关闭窗口",width=8,command=root.destroy,relief=GROOVE)
            quitbutton.grid(column=0,row=4,columnspan=2,pady=8)
        else:
            quitbutton = Button(root,text="关闭窗口",width=8,command=root.destroy,relief=GROOVE)
            quitbutton.grid(column=0,row=4,columnspan=2,pady=8)

    else:
        ww = 500
        wh = 300
        x = (sw-ww) / 2
        y = (sh-wh) / 2
        root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))

        titlelabel = Label(root,text='识别到' + str(piccount) + '个二维码,双击查看详情')
        titlelabel.grid(column=0,row=0,pady=8)

        treeview = ttk.Treeview(root, height=9, show="headings", columns=['type','code','content'])  # 表格
 
        treeview.column('type', width=80, anchor='w') # 表示列,不显示
        treeview.column('code', width=70, anchor='w')
        treeview.column('content', width=300, anchor='w')

        treeview.heading("type", text="二维码类型") # 显示表头
        treeview.heading('code', text='文本编码')
        treeview.heading("content", text="解码内容")
 
        treeview.grid(column=0,row=1,padx=24)
        
        for i in range(0,piccount):
            pictype = showcode[i][1]
            codetype = chardet.detect(showcode[i][0])['encoding']
            picstr = showcode[i][0].decode(encoding = codetype)
            treeview.insert('', 'end', values=(pictype,codetype,picstr))
        
        treeview.bind("<Double-Button-1>",watchdetail)

        quitbutton = Button(root,text="关闭窗口",width=8,command=root.destroy,relief=GROOVE)
        quitbutton.grid(column=0,row=4,columnspan=2,pady=8)


def function1():
    global btn1,btn2,btn3
    code = ScreenDecode()
    if code[0] != 0:
        btn1['state'] = DISABLED
        btn2['state'] = DISABLED
        btn3['state'] = DISABLED
        top = Toplevel()
        scrwid = top.winfo_screenwidth()
        scrhig = top.winfo_screenheight()
        top.geometry("+100+180")
        top.title("截图预览")

        newheight = code[1].height
        newwidth = code[1].width
        while newheight > scrhig*(2/3) or newwidth > scrwid*(2/3):
            newheight *= 2/3
            newwidth *= 2/3
        newheight = int(newheight)
        newwidth = int(newwidth)

        global tkpic
        tkpic = ImageTk.PhotoImage(code[1].resize(size=(newwidth,newheight)))

        cv=Canvas(top,bg='black',width=newwidth,height=newheight)
        cv.grid(column=0,row=0,columnspan=4)                            #读取和识别的图片
        cv.create_image(1,1,anchor='nw',image=tkpic)
        def btnact1():
            top.destroy()
            sleep(0.5)
            function1()
        def btnact2(image):
            fname = filedialog.asksaveasfilename(title=u'保存图片', defaultextension=".png", filetypes=[("PNG", "*.png"),("所有文件","*.*")])      #("JPEG", "*.jpg;*.jpeg;*.jpe"),("BMP", "*.bmp;*.rle;*.dib"),("GIF", "*.gif")
            if fname != "":
                image.save(fname)
        btn = Button(top,text="识别二维码",width=10,command=lambda:showtext(code[0]),relief=GROOVE,bg='lavender')
        btn.grid(column=0,row=1,sticky=E)
        btn = Button(top,text="重新截图",width=8,command=btnact1,relief=GROOVE)
        btn.grid(column=1,row=1)
        btn = Button(top,text="保存截图",width=8,command=lambda:btnact2(code[1]),relief=GROOVE)
        btn.grid(column=2,row=1)
        btn = Button(top,text="关闭窗口",width=8,command=top.destroy,relief=GROOVE)
        btn.grid(column=3,row=1,sticky=W)
        top.wait_window()
        code[1].close()
        btn1['state'] = NORMAL
        btn2['state'] = NORMAL
        btn3['state'] = NORMAL

def function2():
    global btn1,btn2,btn3
    picname = filedialog.askopenfilename(title=u'打开图片', filetypes=[("PNG", "*.png"),("JPEG", "*.jpg;*.jpeg;*.jpe"),("BMP", "*.bmp;*.rle;*.dib"),("GIF", "*.gif")])    #("所有文件", "*.*")
    if picname != "":
        btn1['state'] = DISABLED
        btn2['state'] = DISABLED
        btn3['state'] = DISABLED
        top = Toplevel()
        scrwid = top.winfo_screenwidth()
        scrhig = top.winfo_screenheight()

        pic = Image.open(picname)

        newheight = pic.height
        newwidth = pic.width
        while newheight > scrhig*(2/3) or newwidth > scrwid*(2/3):
            newheight *= 2/3
            newwidth *= 2/3
        newheight = int(newheight)
        newwidth = int(newwidth)

        global tkpic
        tkpic = ImageTk.PhotoImage(pic.resize(size=(newwidth,newheight)))

        top.geometry("+100+180")
        top.title("图片预览")
        cv=Canvas(top,bg='black',width=newwidth,height=newheight)
        cv.grid(column=0,row=0,columnspan=2)                            #读取和识别的图片
        cv.create_image(1,1,anchor='nw',image=tkpic)
        def btnact(image):
            code = qrdecode(image)
            if(code == []):
                code = 1
            showtext(code)
        btn = Button(top,text="识别二维码",width=10,command=lambda:btnact(pic),relief=GROOVE,bg='lavender')
        btn.grid(column=0,row=1,sticky=E)
        btn = Button(top,text="关闭窗口",width=8,command=top.destroy,relief=GROOVE)
        btn.grid(column=1,row=1,sticky=W)
        top.wait_window()
        pic.close()
        btn1['state'] = NORMAL
        btn2['state'] = NORMAL
        btn3['state'] = NORMAL

#生成二维码
def generate():
    global btn1,btn2,btn3
    btn1['state'] = DISABLED
    btn2['state'] = DISABLED
    btn3['state'] = DISABLED
    # 二维码内容
    def hit_me():
        # 二维码内容
        data = t1.get('0.0','end')
        # 生成二维码
        img= qrcode.make(data=data)
        
        # 直接显示二维码
        top = Toplevel()
        scrwid = top.winfo_screenwidth()
        scrhig = top.winfo_screenheight()
        top.geometry("+100+180")
        top.title("图片预览")

        newheight = img.height
        newwidth = img.height                                           #用原有的宽度会导致图像变得非常细长,原因未知

        global tkpic
        tkpic = ImageTk.PhotoImage(img.resize(size=(newwidth,newheight)))

        cv=Canvas(top,bg='black',width=newwidth,height=newheight)
        cv.grid(column=0,row=0,columnspan=2)                            #读取和识别的图片
        cv.create_image(1,1,anchor='nw',image=tkpic)
        def btnact(image):
            fname = filedialog.asksaveasfilename(title=u'保存图片', defaultextension=".png", filetypes=[("PNG", "*.png"),("所有文件","*.*")])       #("JPEG", "*.jpg;*.jpeg;*.jpe"),("BMP", "*.bmp;*.rle;*.dib"),("GIF", "*.gif")
            if fname != "":
                image.save(fname)
                gen.destroy()
                top.destroy()
        btn = Button(top,text="保存为文件",width=10,command=lambda:btnact(img),relief=GROOVE)
        btn.grid(column=0,row=1,sticky=E)
        btn = Button(top,text="关闭窗口",width=8,command=top.destroy,relief=GROOVE)
        btn.grid(column=1,row=1,sticky=W)
        gen.destroy()
        top.wait_window()
        img.close()

    gen = Toplevel()
    # 进入消息循环
    gen.title('二维码生成')
    gen.geometry('418x200+100+180')
    l1 = Label(gen, text='请输入二维码内容')
    l1.grid(column=0,row=0,columnspan=2)
    l2 = Label(gen, text='(网址,文本)')
    l2.grid(column=0,row=1,columnspan=2)
    t1=Text(gen,height=8,width=59)
    t1.grid(column=0,row=2,columnspan=2)
    b1=Button(gen,text='一键生成', width=10, height=1, command=hit_me, relief=GROOVE,bg='lavender')
    b1.grid(column=0,row=3)
    b2=Button(gen,text='关闭窗口', width=10, height=1, command=gen.destroy, relief=GROOVE)
    b2.grid(column=1,row=3)
    gen.wait_window()
    btn1['state'] = NORMAL
    btn2['state'] = NORMAL
    btn3['state'] = NORMAL

root = Tk()

#高DPI兼容
ctypes.windll.shcore.SetProcessDpiAwareness(2)                      #设置不缩放

root.attributes('-topmost',1)               #窗口置顶
root.title("二维码解析&生成实用工具")
root.geometry("320x30+100+100")
root.resizable(width=False, height=False)
btn1 = Button(root,text="截图解析",width=8,command=function1,relief=GROOVE)
btn1.pack(side=LEFT)
btn2 = Button(root,text="图片文件解析",width=13,command=function2,relief=GROOVE)
btn2.pack(side=LEFT)
btn3 = Button(root,text="生成二维码",width=11,command=generate,relief=GROOVE)
btn3.pack(side=LEFT)
btn4 = Button(root,text="退出程序",width=8,command=root.destroy,relief=GROOVE)
btn4.pack(side=LEFT)
root.mainloop()