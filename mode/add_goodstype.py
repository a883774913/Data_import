import json
import os

import xlrd

from Data_import.common.Common import Common
from Data_import.mode.login import Login
from Data_import.mysql.mysql import Mysql


class Add_GoodsType:
    def __init__(self):
        info = Login().login()
        self.sess = info[0]
        self.token = info[1]
        self.header = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '614',
                       'Accept': 'application/json,text/plain,*/*',
                       'X-TIMESTAMP': '20220222134727', 'X-Sign': '49E05B356F062A652820197CA172C44B', 'tenant-id': '0',
                       'X-Access-Token': f'{self.token}',
                       'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/98.0.4758.80Safari/537.36Edg/98.0.1108.50',
                       'Content-Type': f'application/json;charset=UTF-8', 'Origin': 'http://18.118.13.94', 'Referer': 'http://18.118.13.94/',
                       'Accept-Encoding': 'gzip,deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}

    def add_goodstype(self, typeone, desctext, weight, url_key, meta_title, meta_keywords, meta_description, filePath):
        """
        新增类型到后台数据
        :param file_path: 图片地址
        :param typeone: 类型名称
        :param desctext: 类型描述
        :param weight: 权重
        :param url_key:
        :param meta_title:
        :param meta_keywords:
        :param meta_description:
        :return:
        """

        url = 'http://18.118.13.94:8080/jeecg-boot/sys/api/goodsType/add'
        data = {"typeone": typeone, "desctext": desctext, "weights": weight, "urlKey": url_key, "metaTitle": meta_title,
                "metaKeywords": meta_keywords, "metaDescription": meta_description, "filePath": filePath}
        data = json.dumps(data)
        res = self.sess.post(url=url, headers=self.header, data=data)
        print(res.json())
        return res.json()

    def clear_goodstype(self):
        # 删除类型表中的数据
        Mysql().drop_table(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306,
                           sql='TRUNCATE TABLE goods_type')

    def getFlist(self, file_path):
        for root, dirs, files in os.walk(file_path):
            print('root_dir:', root)  # 获取当前目录地址
            print('sub_dirs:', dirs)  # 获取目录
            print('files:', files)  # 获取文件名
        return files

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

    def main(self):
        try:
            os.remove('../log/add_type_log')  # 删除先前日志文件
        except FileNotFoundError:
            pass
        con, cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        infos = Mysql().dql(cur, sql="""select * FROM catalog_category_flat_store_1 where `level`='2';""")
        print(f'存在{len(infos)}条数据')
        success = 0  # 计算成功数量
        erro = 0  # 计算失败数量
        n = 0  # 计算测试所在位置
        for info in infos:
            n += 1
            try:
                typename = info['name']  # 数据库中类型表中的类型名称
                print(f'类型为{typename}')
                pic_name = self.get_pic_name(typeone=typename)
                pic_path = self.get_file_path(pic_name=pic_name)
                pic_url = self.uplod_file(name=typename, file_path=pic_path, token=self.token, sess=self.sess)
                print(pic_url)
                res = self.add_goodstype(typeone=typename, desctext=info['description'], weight=0, url_key=info['url_key'],
                                         meta_title=info['meta_title'], meta_keywords=info['meta_keywords'], meta_description=info['meta_description'],
                                         filePath=pic_url)
                assert '操作成功' in res['message']
                success += 1
            except:
                erro_info = f'商品类型添加模块，第{n} 条数据错误，类型名称为{typename},错误信息为: {res["message"]} \n'
                print(erro_info)
                Common().erro_log(log_path=r'../log/add_type_log', erro_info=erro_info)
                erro += 1
            finally:
                print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
                print('分割线'.center(60, '-'))
        Mysql().close(con, cur)
        n, erro, success = self.add_type2(typeone='Servo Motor', erro=erro, n=n, success=success)  # 单独加入伺服类产品
        n, erro, success = self.add_type2(typeone='Servo Drive', erro=erro, n=n, success=success)
        n, erro, success = self.add_type2(typeone='Servo Valve', erro=erro, n=n, success=success)

    def get_pic_name(self, typeone):
        """
        通过 typeone 获取 图片简称名称
        :param typeone:
        :return:
        """
        book = xlrd.open_workbook(filename=rf"{os.getcwd()}\..\data\class_pic.xls")
        table = book.sheet_by_name('Sheet1')
        rows = table.nrows  # 获取行数
        for row in range(1, rows):
            excle_typeone = table.row_values(row)[0]
            # print(f'typeone为{excle_typeone}')  #获取excle中的typeone ， 如果excle中的typeone为相同，则使用该pic_name
            pic_name = table.row_values(row)[2]
            if excle_typeone == typeone:
                print(f'图片简略名称为{pic_name}')
                return pic_name

    def get_file_path(self, pic_name):
        """
        通过简略名称获取图片地址
        :param pic_name:
        :return:
        """
        file_path = f'{os.getcwd()}\..\data\图标'
        file_list = self.getFlist(file_path)  # 获取目录下的所有文件名
        for file in file_list:
            path = fr'C:\Users\admin\Desktop\图标\{file}'  # 获取文件地址
            name = file.replace('icon_icon_', '').split('（')[0].split('(')[0]  # 获取图片名字方便区分记住
            # print(f'优化后名称为{name}')
            if name == pic_name:
                print(f'图片地址为{path}')
                return path

    def add_type2(self, typeone, erro, n, success):
        """
        单独添加类型专用
        :param typeone: 类型名称
        :param erro:   错误次数
        :param n:   运行次数
        :param success: 成功次数
        :return: n, erro, success
        """
        n += 1
        try:
            pic_name = self.get_pic_name(typeone=typeone)
            pic_path = self.get_file_path(pic_name=pic_name)
            pic_url = self.uplod_file(name=typeone, file_path=pic_path, token=self.token, sess=self.sess)
            res = self.add_goodstype(typeone=typeone, desctext=typeone, weight=0, url_key='',
                                     meta_title='', meta_keywords='', meta_description='',
                                     filePath=pic_url)
            assert '操作成功' in res['message']
            success += 1
        except:
            erro_info = f'商品类型添加模块，第{n} 条数据错误,错误名称为{typeone}，错误信息为: {res["message"]} \n'
            print(erro_info)
            Common().erro_log(log_path=r'../log/add_type_log', erro_info=erro_info)
            erro += 1
        finally:
            print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
            print('分割线'.center(60, '-'))
            return n, erro, success


if __name__ == '__main__':
    a = Add_GoodsType()
    a.clear_goodstype()
    a.main()
