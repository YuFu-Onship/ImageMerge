import traceback
from PIL import Image,ImageDraw, ImageFont
import os
import sys
import math

class ImageMerge:
    def __init__(self):
        self.A4_SIZE=[2480,3508]
        self.limit=1.2
        self.transformation=True
        
        self.main_dir=input("请输入主文件夹路径,例如:E:/test\n>")
        self.padding=float(input("请输入图片间隔,单位:mm\n>"))*12
        
        mode_description="请输入选择模式\n[1]自定义图片高度,单位:mm\n[2]自定义列数,图片高度为自动计算\n>"
        self.mode=input(mode_description)
        
        if self.mode=="1":
            self.ImageHeight=round(int(input("请输入图片高度,单位:mm\n>"))*12)
            self.cols=self.A4_SIZE[1]//self.ImageHeight-1
        elif self.mode=="2":
            self.cols=int(input("请输入行数:\n>"))
            self.ImageHeight=round((self.A4_SIZE[1]-60-self.padding*self.cols)/self.cols)
            
    
    def main(self):
        try:
            path_info=self.returnImages()
            num=len(path_info[0])
            result_canvas=[]

            for n in range(num):
                dir_name=path_info[0][n]
                images=path_info[1][n]
                rows=self.dealImageSet(images)
                canvas=(self.drawCanvas(rows,dir_name))

                for c in canvas:
                    result_canvas.append(c)
                
            result_pdf_path=self.main_dir+"/multi_page.pdf"
            if os.path.exists(result_pdf_path):
                os.remove(result_pdf_path)
            result_canvas[0].save(result_pdf_path, save_all=True, append_images=result_canvas[1:])
        
        except Exception as e:
            print(traceback.print_exc())
            if getattr(sys, 'frozen', False):
                file_path = os.path.abspath(sys.executable)
            else:
                file_path = os.path.abspath("main.py")
            dir_path = os.path.dirname(file_path)
            error_path=dir_path+"/error.txt"
            with open(error_path,mode="a+",encoding="utf-8")as f:
                f.write(e)
                f.write(traceback.print_exc())
    
    def returnImages(self):
        """返回文件夹名称与对应的图片路径"""
        dir_names=[]
        image_list=[]
        self.subdirs=[]
        for subdir in os.listdir(self.main_dir):
            subdir_path=self.main_dir+f"\\{subdir}"
            if not os.path.isdir(subdir_path):
                continue
            
            self.subdirs.append(subdir)
            if os.path.isdir(subdir_path):
                dir_names.append(subdir_path)
            
            images=[]
            for file in os.listdir(subdir_path):
                file_path=subdir_path+f"\\{file}"
                
                if file.lower().endswith(("png","jpg","jpeg")):
                    img=Image.open(file_path)
                    width,height=img.size
                    if self.transformation:
                        if width/height>self.limit:
                            img.rotate(-90,expand=True).save(file_path)
                    images.append([file_path,[width,height]])
            image_list.append(images)
        return [self.subdirs,image_list]
    
    def computeInterval(self,mm):
        """毫米数转化为像素数"""
        return mm*12
    
    def returnImageSize(self,imagePath):
        pass
    
    def drawCanvas(self,rows,info):
        """将rows中的信息绘制到若干canvas上"""
        # print(len(rows))
        
        pages=len(rows)//self.cols
        if len(rows)%self.cols>0:
            pages+=1
        
        canvas_es=[]
        for i in range(pages):
            canvas_es.append(rows[:self.cols])
            rows=rows[self.cols:]
        result_canvas=[]
        for canvas in canvas_es:
            af_canvas=Image.new("RGB", (self.A4_SIZE[0], self.A4_SIZE[1]), color="white")
            draw=ImageDraw.Draw(af_canvas)
            font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 60)
            draw.text((self.padding,self.A4_SIZE[1]-70),info,font=font,fill="black")
            
            # print(len(canvas))
            for r in range(len(canvas)):
                position_y=round(r*self.ImageHeight+(r+1)*self.padding)
                # print(position_y)
                
                position_x=round(self.padding)
                
                for i in range(len(canvas[r])):
                    Img=Image.open(canvas[r][i][0])
                    width,height=Img.size
                    scale=self.ImageHeight/height
    
                    # position_x+=round(self.padding+canvas[r][i][1]*(i))
                    new_width,new_height=round(width*scale),round(height*scale)
    
                    resized = Img.resize((new_width, new_height),Image.Resampling.LANCZOS)
                    af_canvas.paste(resized, (position_x, position_y))
                    
                    self.drawLine(af_canvas,position_x,position_y,new_width,new_height)
                    position_x+=round(self.padding+new_width)
                
            result_canvas.append(af_canvas)
        return result_canvas

    
    def drawLine(self,obj,position_x,position_y,new_width,new_height):
        """绘制十字线"""
        draw = ImageDraw.Draw(obj)
        half_pad = self.padding // 2
        # 图像右下角
        x1, y1 = position_x, position_y
        x2, y2 = position_x + new_width, position_y + new_height

        # 定义四角点（中心点）
        cp = [
            (x1 - half_pad, y1 - half_pad),  # 左上
            (x2 + half_pad, y1 - half_pad),  # 右上
            (x1 - half_pad, y2 + half_pad),  # 左下
            (x2 + half_pad, y2 + half_pad),  # 右下
        ]

        # 十字线长度
        line_len = half_pad
        way=[
            [[(cp[0][0],cp[0][1]),(cp[0][0]+line_len,cp[0][1])],[(cp[0][0], cp[0][1]), (cp[0][0], cp[0][1] + line_len)]],
            [[(cp[1][0],cp[1][1]),(cp[1][0]-line_len,cp[1][1])],[(cp[1][0], cp[1][1]), (cp[1][0], cp[1][1] + line_len)]],
            [[(cp[2][0],cp[2][1]),(cp[2][0]+line_len,cp[2][1])],[(cp[2][0], cp[2][1]), (cp[2][0], cp[2][1] - line_len)]],
            [[(cp[3][0],cp[3][1]),(cp[3][0]-line_len,cp[3][1])],[(cp[3][0], cp[3][1]), (cp[3][0], cp[3][1] - line_len)]]
        ]
        for i in range(len(cp)):
            draw.line(way[i][0],fill="black",width=2)
            draw.line(way[i][1],fill="black",width=2)
                
          
    def dealImageSet(self,images):
        """处理某一文件夹内的信息,返回地址与宽度信息"""
        
        # 计算等高缩放后的宽度
        width_list = []
        image_paths=images[0]
        
        for i, e in enumerate(images):
            scaled_width = round(e[1][0] * (self.ImageHeight/ e[1][1]))
            width_list.append((i, scaled_width))

        # 按宽度降序排序
        width_list.sort(key=lambda x: -x[1])

        rows = []

        while width_list:
            row = []
            row_width = self.padding*2

            i = 0
            while i < len(width_list):
                idx, w = width_list[i]
                if row_width + w <= self.A4_SIZE[0]:
                    row.append((images[idx][0], w))
                    row_width += w+self.padding
                    width_list.pop(i)  # 放入后移除
                else:
                    i += 1

            # 如果实在放不下任何一张（极宽图），就强行单独放入一行
            if not row and width_list:
                idx, w = width_list.pop(0)
                row = [(e[idx][0], w)]
            rows.append(row)
        return rows
        
        
def main():
    T=ImageMerge()
    T.main()

if __name__=="__main__":
    main()