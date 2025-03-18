## 程序说明（重点）！！：
目前只兼容window系统，其他系统未进行适配！
需要配合tesseract 使用:
    地址：https://github.com/UB-Mannheim/tesseract/wiki
![img.png](sources/img.png)
默认安装即可，该版本安装过程中会自动注入环境变量，无需手动配置。

## 程序配置
### python版本 ：Python 3.12.3
### 安装依赖包
 pip install -r requirements.txt
 
## 程序预览
![img_1.png](sources/img_1.png)

## 快捷键说明：
ctrl - ➕ ：pdf 放大  <br>
ctrl - ➖ ：pdf 缩小  <br>
ctrl - 鼠标滚轮 ：pdf放大或缩小  <br>
ctrl - ←   ：pdf上一页  <br>
ctrl - →   ：pdf下一页  <br>
ctrl - shift - ←   ：当前pdf图片 左旋转90度  <br>
ctrl - shift - →   ：当前pdf图片 右旋转90度  <br>
ctrl - shift - S    ：保存修改后的pdf文件  <br>
ctrl - enter ：识别当前图片内容  <br>
ctrl - s ：保存右侧文本内容  <br>

## 其他
### 导出配置文件
pip list --format=freeze > requirements.txt