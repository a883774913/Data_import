import json
import os
import random
import re

from Data_import.common.Common import Common
from Data_import.mode.login import Login
from Data_import.data.read_data import Read_data
from Data_import.mysql.mysql import Mysql
from pachong1.userAgent import UserAgent


class Add_Goodsbrand:

    def __init__(self):
        info = Login().login()
        self.sess = info[0]
        self.token = info[1]
        self.useragent = random.choice(UserAgent().useragent_list())

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
        header = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '614',
                  'Accept': 'application/json,text/plain,*/*',
                  'X-TIMESTAMP': '20220222134727', 'X-Sign': '49E05B356F062A652820197CA172C44B', 'tenant-id': '0',
                  'X-Access-Token': f'{self.token}',
                  'User-Agent': f'{self.useragent}',
                  'Content-Type': f'application/json;charset=UTF-8', 'Origin': 'http://18.118.13.94',
                  'Referer': 'http://18.118.13.94/',
                  'Accept-Encoding': 'gzip,deflate',
                  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
        data = {"logo": logo,
                "name": name,
                "desctext": desctext,
                "weights": weights,
                "productionplace": productionplace,
                "goodstypeid": goodstypeid, "urlKey": url_key, "metaTitle": meta_title,
                "metaKeywords": meta_keywords, "metaDescription": meta_description}

        data = json.dumps(data)
        print(f'data为{data}')
        res = self.sess.post(url=url, headers=header, data=data)
        print(res.json())
        return res.json()

    def main(self):
        try:
            os.remove('../log/add_brand_log')  # 删除先前日志文件
        except FileNotFoundError:
            pass
        con, cur = Read_data().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con1, cur1 = Read_data().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)
        sql = 'select name,description,parent_id,url_key,meta_title,meta_keywords,meta_description from catalog_category_flat_store_1 where level="3";'
        infos = Read_data().dql(cur, sql)  # 获取品牌数据
        print(len(infos))
        success = 0  # 计算成功数量
        erro = 0  # 计算失败数量
        n = 0  # 计算测试所在位置
        for info in infos:
            name = info['name']
            desctext = info['description']
            if desctext is None:
                desctext = ''
            logo = self.get_logo(desctext)
            weights = 0
            productionplace = "null"
            parent_id = info['parent_id']
            goodstype_id = self.get_goodstype_id(parent_id=parent_id, local_cur=cur, cur=cur1)
            url_key = info['url_key']
            meta_title = info['meta_title']
            meta_keywords = info['meta_keywords']
            meta_description = info['meta_description']
            try:
                n += 1
                res = self.add_goodsbrand(logo=logo, name=name, desctext=desctext, weights=weights,
                                          productionplace=productionplace, goodstypeid=goodstype_id,
                                          url_key=url_key, meta_title=meta_title,
                                          meta_keywords=meta_keywords, meta_description=meta_description)
                assert '操作成功' in res['message']
                success += 1
            except AssertionError:
                erro_info = f'商品品牌添加模块，第{n} 条数据错误，品牌名称为{info["name"]}，所属类型ID为{goodstype_id},错误信息为: {res["message"]}  \n'
                print(erro_info)
                Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)
                erro += 1
            finally:
                print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
                print(f'分割线'.center(60, '-'))

        Read_data().close(con, cur)
        Read_data().close(con1, cur1)

    def clear_goodsbrand(self):
        Mysql().drop_table(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306,
                           sql='TRUNCATE TABLE goods_brand')

    def get_goodstype_id(self, parent_id, local_cur, cur):
        """
        通过parent_id 查询现网站typeID
        :param cur: 线上数据库链接后的游标
        :param local_cur: 本地数据库链接后的游标
        :param parent_id:父类ID
        :return: type_id 类型ID
        """
        sql2 = f'select name from catalog_category_flat_store_1 where entity_id="{parent_id}";'
        type_infos = Read_data().dql(local_cur, sql2)
        typeone = type_infos[0]['name']  # 获取所属类型名称

        sql3 = f'select id from goods_type where typeone="{typeone}"'
        res = Read_data().dql(cur, sql3)
        type_id = res[0]['id']
        return type_id

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

    def insert_typeid(self):
        """
        添加类型后 将品牌所属类型ID ，以及类型图片加入到数据库中
        :return:
        """
        con, cur = Read_data().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con1, cur1 = Read_data().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)
        sql = 'select entity_id,description,parent_id from catalog_category_flat_store_1 where level="3";'
        infos = Read_data().dql(cur, sql)  # 获取品牌数据
        print(len(infos))
        for info in infos:

            try:
                entity_id = info['entity_id']  # 获取
                print(entity_id)

                desctext = info['description']
                logo = self.get_logo(desctext)
                print(logo)

                parent_id = info['parent_id']
                sql2 = f'select name from catalog_category_flat_store_1 where entity_id="{parent_id}";'
                type_infos = Read_data().dql(cur, sql2)
                typeone = type_infos[0]['name']  # 获取所属类型名称
                print(f'所属类型为{typeone}')
                sql3 = f'select id from goods_type where typeone="{typeone}"'
                res = Read_data().dql(cur1, sql3)
                goodstype_id = res[0]['id']
                print(f'类型ID为{goodstype_id}')

                sql1 = rf'UPDATE catalog_category_flat_store_1 set image="{logo}",typeid="{goodstype_id}" where entity_id="{entity_id}"'
                Read_data().dml(con, cur, sql1)
            except TypeError:
                pass
            finally:
                print('分割线'.center(60, '-'))
        Read_data().close(con1, cur1)
        Read_data().close(con, cur)

    def add_level_4(self):
        """
        Level 为 4 的品牌添加，统一添加到 Servo_Motors 或者 Servo_Drive 类型中
        :return:
        """
        con, cur = Read_data().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con1, cur1 = Read_data().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)  # or typeone='';

        sql = """select typeone,id from goods_type where typeone='Servo Motor';"""
        Servo_Motors_id = Mysql().dql(cur1, sql)[0]['id']  # 获取伺服电机类型ID
        sql1 = """select typeone,id from goods_type where typeone='Servo Drive';"""
        Servo_Drive_id = Mysql().dql(cur1, sql1)[0]['id']  # 获取伺服驱动类型ID
        sql3 = """select typeone,id from goods_type where typeone='Servo Valve';"""
        Servo_Value_id = Mysql().dql(cur1, sql3)[0]['id']  # 获取伺服驱动类型ID

        sql2 = 'select name,description,url_key,meta_title,meta_keywords,meta_description from catalog_category_flat_store_1 where level="4";'

        infos = Mysql().dql(cur, sql2)
        print(len(infos))
        success = 0  # 计算成功数量
        erro = 0  # 计算失败数量
        n = 0  # 计算测试所在位置
        for info in infos:
            n += 1
            print(info)
            name = info['name']
            desctext = info['description']
            logo = self.get_logo(desctext)
            weights = 0
            productionplace = "null"

            if "Servo Drive" in name:
                goodstype_id = Servo_Drive_id
            elif "Servo Motor" in name:
                goodstype_id = Servo_Motors_id
            else :
                goodstype_id = Servo_Value_id

            url_key = info['url_key']
            meta_title = info['meta_title']
            meta_keywords = info['meta_keywords']
            meta_description = info['meta_description']

            try:
                res = self.add_goodsbrand(logo=logo, name=name, desctext=desctext, weights=weights,
                                          productionplace=productionplace, goodstypeid=goodstype_id,
                                          url_key=url_key, meta_title=meta_title,
                                          meta_keywords=meta_keywords, meta_description=meta_description)
                assert '操作成功' in res['message']
                success += 1
            except AssertionError:
                erro_info = f'商品品牌添加模块，第{n} 条数据错误，品牌名称为{info["name"]}，所属类型ID为{goodstype_id},错误信息为: {res["message"]}  \n'
                print(erro_info)
                Common().erro_log(log_path=r'../log/add_brand_log', erro_info=erro_info)
                erro += 1
            finally:
                print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
                print(f'分割线'.center(60, '-'))
        Read_data().close(con, cur)
        Read_data().close(con1, cur1)

    def check_erro(self,name):
        con, cur = Read_data().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con1, cur1 = Read_data().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)
        sql = f"""select * from catalog_category_flat_store_1 where name='{name}'"""
        info = Mysql().dql(cur,sql)[0]
        print(info)
        name = info['name']
        desctext = info['description']
        if desctext is None:
            desctext = ''
        logo = self.get_logo(desctext)
        weights = 0
        productionplace = "null"
        parent_id = info['parent_id']
        goodstype_id = self.get_goodstype_id(parent_id=parent_id, local_cur=cur, cur=cur1)
        url_key = info['url_key']
        meta_title = info['meta_title']
        meta_keywords = info['meta_keywords']
        meta_description = info['meta_description']
        res = self.add_goodsbrand(logo=logo, name=name, desctext=desctext, weights=weights,
                                  productionplace=productionplace, goodstypeid=goodstype_id,
                                  url_key=url_key, meta_title=meta_title,
                                  meta_keywords=meta_keywords, meta_description=meta_description)

        Read_data().close(con, cur)
        Read_data().close(con1, cur1)

        # url = 'http://18.118.13.94:8080/jeecg-boot/sys/api/goodsBrand/add'
        # header = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '614',
        #           'Accept': 'application/json,text/plain,*/*',
        #           'X-TIMESTAMP': '20220222134727', 'X-Sign': '49E05B356F062A652820197CA172C44B', 'tenant-id': '0',
        #           'X-Access-Token': f'{self.token}',
        #           'User-Agent': f'{self.useragent}',
        #           'Content-Type': f'application/json;charset=UTF-8', 'Origin': 'http://18.118.13.94',
        #           'Referer': 'http://18.118.13.94/',
        #           'Accept-Encoding': 'gzip,deflate',
        #           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
        # # data={"logo": "", "name": "COMET", "desctext": "null", "weights": 0, "productionplace": "null", "goodstypeid": "1524951737452101633", "urlKey": "comet", "metaTitle": "null", "metaKeywords": "null", "metaDescription": "null"}
        # data = json.dumps(data)
        # print(f'data为{data}')
        # res = self.sess.post(url=url, headers=header, data=data)
        # print(res.json())

if __name__ == '__main__':
    a = Add_Goodsbrand()
    a.clear_goodsbrand()
    a.main()
    a.add_level_4()
    # a.check_erro(name='Blue-White')