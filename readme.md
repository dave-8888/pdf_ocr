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
 

## 其他
### 导出配置文件
pip list --format=freeze > requirements.txt