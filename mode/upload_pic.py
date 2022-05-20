import os

import xlrd

from Data_import.mode.login import Login
from Data_import.mysql.mysql import Mysql


class Upload_pic:

    def uplod_file(self, name: str, file_path: str, token, sess):
        """
        :param sess:  会话
        :param token:  token
        :param name: 文件别名
        :param file_path: 文件地址
        :return: 返回图片地址
        """
        url = 'http://18.118.13.94:80/jeecg-boot/sys/common/upload'
        headers = {'Connection': 'keep-alive', 'Content-Length': '14846',
                   'X-Requested-With': 'XMLHttpRequest',
                   'X-Access-Token': f'{token}',
                   'Accept-Encoding': 'gzip,deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6', 'sec-gpc': '1'}

        file = {'file': (f'{name}', open(fr"{file_path}", 'rb'), "image/png")}
        data = {"size": "1"}
        res = sess.post(url=url, headers=headers, files=file, data=data)
        print(res.json())
        try:
            assert res.json()['success'] is True
            pic_url = res.json()['message']
        except AssertionError:
            print('图片上传失败')
            pic_url = None
        return pic_url


    def delete_file(self):
        resDir = r'C:\Users\admin\Desktop\图标'  # 目录地址
        file_list = self.getFlist(resDir)  # 获取目录下的所有文件名
        for file in file_list:  # 遍历文件
            if "nor" in file:  # 条件
                print(file)
                file_path = fr'C:\Users\admin\Desktop\图标\{file}'  # 拼接地址
                os.remove(file_path)  # 删除符合条件的文件




if __name__ == '__main__':
    a = Upload_pic()
    a.main()
