import json
import os
import random
import re

import xlrd
from faker import Faker

from Data_import.common.Common import Common
from Data_import.mode.login import Login
from Data_import.mode.upload_pic import Upload_pic
from Data_import.mode.userAgent import UserAgent
from Data_import.mysql.mysql import Mysql


class Add_Goodstype_And_Brand:

    def __init__(self):  # 每次运行前删除上一次错误日志
        info = Login().login()
        self.sess = info[0]
        self.token = info[1]
        useragent = random.choice(UserAgent().useragent_list())
        self.header = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '614',
                       'Accept': 'application/json,text/plain,*/*',
                       'X-TIMESTAMP': '20220222134727', 'X-Sign': '49E05B356F062A652820197CA172C44B', 'tenant-id': '0',
                       'X-Access-Token': f'{self.token}',
                       'User-Agent': f'{useragent}',
                       'Content-Type': f'application/json;charset=UTF-8', 'Origin': 'http://18.118.13.94', 'Referer': 'http://18.118.13.94/',
                       'Accept-Encoding': 'gzip,deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}

        try:
            os.remove('../log/add_type_log')  # 删除先前类型添加日志文件
        except FileNotFoundError:
            pass
        try:
            os.remove('../log/add_brand_log')  # 删除先前品牌添加日志文件
        except FileNotFoundError:
            pass


    def main(self):
        """
        品牌添加、类型添加 或者检测使用
        :return:
        """
        local_con, local_cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con, cur = Mysql().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)
        sql = f'select * from catalog_category_flat_store_1'
        infos = Mysql().dql(local_cur, sql)

       # 第一次添加需要添加
        self.add_type(typeone='Servo Motor',desctext='',meta_title='',meta_keywords='',meta_description='')  # 单独加入伺服类产品
        self.add_type(typeone='Servo Drive',desctext='',meta_title='',meta_keywords='',meta_description='')
        self.add_type(typeone='Servo Valve',desctext='',meta_title='',meta_keywords='',meta_description='')

        for info in infos:
            is_Repeat = 0
            faker = Faker()
            level = info['level']  # 级别 用于区分类别和品牌 2为类型  3、4为品牌
            name = info['name']  # 类型或者品牌名称
            description = info['description']
            if description is None:
                description = ''
            url_key = info['url_key']
            meta_title = info['meta_title']
            meta_keywords = info['meta_keywords']
            meta_description = info['meta_description']
            logo = self.get_logo(description=description)
            if level == 2:
                print(name)
                typeone_count = self.select_typeone_count(name, cur)[0]['count(typeone)']
                if typeone_count < 1:
                    print(f'类型{name}不存在，可以添加')
                    self.add_type(typeone=name,desctext=description,meta_title=meta_title,meta_keywords=meta_keywords,meta_description=meta_description)
                print('类型分割线'.center(60, '-'))
            elif level == 3:
                print(f'品牌名称为{name}')  # 这里获取的name为添加表中的name
                typeone = self.select_typeone_by_parent_id(info['parent_id'], local_cur)[0]["name"]
                print(f'父级名称为{typeone}')
                try:
                    typeid = self.select_typeid_by_typeone(typeone, cur)[0]['id']
                    print(f'父级ID为{typeid}')
                    brand_count = self.select_brand_count(name, typeid, cur)[0]['count(name)']
                    print(f'类型 ：{typeone} 下 品牌：{name} 有 {brand_count} 个')
                    if brand_count < 1:
                        print(f'品牌{name}数据库不存在，可添加！！')
                        res = self.add_goodsbrand(logo=logo, name=name, desctext=description, weights=0, productionplace=faker.country(),
                                                  goodstypeid=typeid,
                                                  url_key=url_key, meta_title=meta_title, meta_keywords=meta_keywords, meta_description=meta_description)
                        try:
                            assert '操作成功' in res['message']
                            print(f'品牌{name}添加成功')
                        except AssertionError:
                            erro_info = f'商品品牌{name}添加失败，所属类型为{typeone},错误信息为: {res["message"]}  \n'
                            print(erro_info)
                            Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)
                except:
                    erro_info = f'添加品牌{name}失败 ,请检查是否存在类型{typeone} \n'
                    print(erro_info)
                    Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)

                print('品牌分割线'.center(60, '-'))
            elif level == 4:
                try:
                    sql = """select typeone,id from goods_type where typeone='Servo Motor';"""
                    Servo_Motors_id = Mysql().dql(cur, sql)[0]['id']  # 获取伺服电机类型ID
                    sql1 = """select typeone,id from goods_type where typeone='Servo Drive';"""
                    Servo_Drive_id = Mysql().dql(cur, sql1)[0]['id']  # 获取伺服驱动类型ID
                    sql3 = """select typeone,id from goods_type where typeone='Servo Valve';"""
                    Servo_Value_id = Mysql().dql(cur, sql3)[0]['id']  # 获取伺服驱动类型ID

                    if "Servo Drive" in name:
                        goodstype_id = Servo_Drive_id
                    elif "Servo Motor" in name:
                        goodstype_id = Servo_Motors_id
                    else:
                        goodstype_id = Servo_Value_id

                    brand_count = self.select_brand_count(name, goodstype_id, cur)[0]['count(name)']
                    print(f'类型 ：{goodstype_id} 下 品牌：{name} 有 {brand_count} 个')
                    if brand_count < 1:
                        print(f'品牌{name}数据库不存在，可添加！！')
                        res = self.add_goodsbrand(logo=logo, name=name, desctext=description, weights=0,
                                                  productionplace=faker.country(), goodstypeid=goodstype_id,
                                                  url_key=url_key, meta_title=meta_title,
                                                  meta_keywords=meta_keywords, meta_description=meta_description)
                        try:
                            assert '操作成功' in res['message']
                        except AssertionError:
                            erro_info = f'商品品牌{name}添加失败，所属类型为{goodstype_id},错误信息为: {res["message"]}  \n'
                            print(erro_info)
                            Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)
                except IndexError:
                    print('未找到相关类型，请检查类型是否存在！！')
                    erro_info = f'添加品牌{name}失败 \n'
                    print(erro_info)
                    Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)
        Mysql().close(con, cur)
        Mysql().close(local_con, local_cur)

    def select_typeone_count(self, name, cur):
        """
        通过类型名称查询类型个数
        :param name:    类型名称
        :param cur: 线上游标
        :return:
        """

        sql = f'select count(typeone) from goods_type where typeone="{name}"'
        info = Mysql().dql(cur, sql)
        return info

    def select_brand_count(self, name, goodstypeid, cur):
        """
        检测某个类型下指定名称品牌的个数
        :param goodstypeid: 所属类型ID
        :param name: 品牌名称
        :param cur: 线上游标
        :return:
        """
        sql = f'select count(name) from goods_brand where name="{name}" and goodstypeid = "{goodstypeid}"'  # 查询品牌名称中名为{name}的品牌个数
        info = Mysql().dql(cur, sql)
        return info

    def select_typeone_by_parent_id(self, parent_id, local_cur):
        """
        通过ID查询父类类别名称
        :param parent_id: parent ID
        :param local_cur: 游标， 本地
        :return:
        """
        sql = f'select name from catalog_category_flat_store_1 where entity_id = {parent_id}'
        info = Mysql().dql(local_cur, sql)
        return info

    def select_typeid_by_typeone(self, typeone, cur):
        """
        通过类型名称查询类型ID
        :param typeone: 类型名称
        :param cur: 线上游标
        :return:
        """
        sql = f'select id from goods_type where typeone = "{typeone}" '
        info = Mysql().dql(cur, sql)
        return info

    def get_logo(self, description):
        """
        通过品牌描述过滤图片URL地址
        :param description: 品牌描述
        :return: logo   图片URL地址
        """
        try:
            urls = re.findall(pattern='<img src="{{media url="(.*?)"}}"', string=description)  # 第一次筛选图片
            if urls == []:
                urls2 = re.findall(pattern='<img src="(.*?)"', string=description)  # 二次筛选图片
                if urls2 == []:
                    logo = ''
                else:
                    logo = urls2[0]
            else:
                logo = 'https://okmarts.com/pub/media/' + urls[0]
        except:
            logo = ''
        return logo

    def add_type(self, typeone,desctext,meta_title,meta_keywords,meta_description):
        """
        单独添加类型专用
        :param meta_description:
        :param meta_keywords:
        :param meta_title:
        :param desctext: 描述
        :param typeone: 类型名称
        :return:
        """
        pic_name = self.get_pic_name(typeone=typeone)  # 通过类型名称定位到图标名字
        pic_path = self.get_file_path(pic_name=pic_name)  # 通过图标名字定位到图标地址
        pic_url = Upload_pic().uplod_file(name=typeone, file_path=pic_path, token=self.token, sess=self.sess)  # 上传图片获取图片URL
        res = self.add_goodstype(typeone=typeone, desctext=desctext, weight=0, url_key='',
                                 meta_title=meta_title, meta_keywords=meta_keywords, meta_description=meta_description,
                                 filePath=pic_url)
        try:
            assert '操作成功' in res.json()['message']
            print(f'类型：{typeone}添加成功')
        except AssertionError:
            erro_info = f'类型:{typeone} 添加失败 , {res.json()["message"]} \n'
            print(erro_info)
            Common().erro_log(log_path=r'../log/add_type_log', erro_info=erro_info)
        finally:
            print('分割线'.center(60, '-'))

    def get_pic_name(self, typeone):
        """
        通过 typeone 获取 图片简称名称 ，前提需要class_pic.xls 表中有此类型的记录
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
            path = fr'{file_path}\{file}'  # 获取文件地址
            name = file.replace('icon_icon_', '').split('（')[0].split('(')[0]  # 获取图片名字方便区分记住
            # print(f'优化后名称为{name}')
            if name == pic_name:
                print(f'图片地址为{path}')
                return path

    def add_goodstype(self, typeone, desctext, weight, url_key, meta_title, meta_keywords, meta_description, filePath):
        """
        新增类型到后台数据
        :param filePath: 图片地址
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
        # print(res.json())
        return res

    def getFlist(self, file_path):
        for root, dirs, files in os.walk(file_path):
            print('files:', files)  # 获取文件名
        return files

    def add_goodsbrand(self, logo, name, desctext, weights, productionplace, goodstypeid, url_key, meta_title, meta_keywords, meta_description):
        """
        接口添加商品品牌数据
        :param logo: LOGO url地址
        :param name: 品牌名称
        :param desctext: 品牌描述
        :param weights: 权重
        :param productionplace: 品牌产地
        :param goodstypeid: 品牌所属类型ID
        :param url_key:
        :param meta_title:
        :param meta_keywords:
        :param meta_description:
        :return:
        """
        url = 'http://18.118.13.94:8080/jeecg-boot/sys/api/goodsBrand/add'
        data = {"logo": logo,
                "name": name,
                "desctext": desctext,
                "weights": weights,
                "productionplace": productionplace,
                "goodstypeid": goodstypeid, "urlKey": url_key, "metaTitle": meta_title,
                "metaKeywords": meta_keywords, "metaDescription": meta_description}

        data = json.dumps(data)
        print(f'data为{data}')
        res = self.sess.post(url=url, headers=self.header, data=data)
        print(res.json())
        return res.json()


if __name__ == '__main__':
    a = Add_Goodstype_And_Brand()
    a.main()
