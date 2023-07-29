# 引用包管理工具setuptools，其中find_packages可以幫我們便捷的找到自己代碼中編寫的庫
from setuptools import setup, find_packages
VERSION = "0.0.1"

setup(
    name='ixBrowser',  # 包名稱，之後如果上傳到了pypi，則需要通過該名稱下載
    version=VERSION,  # version只能是數字，還有其他字符則會報錯
    description='Unofficial ixBrowser Python SDK',
    long_description='',
    license='MIT',  # 遵循的協議
    install_requires=[],  # 這里面填寫項目用到的第三方依賴
    author='LYFX',
    author_email='lyfxme@gmail.com',
    packages=find_packages(),  # 項目內所有自己編寫的庫
    platforms='windows',
    url='https://github.com/ontisme/ixBrowser',  # 項目鏈接,
    include_package_data=True,
)
