"""
添加商品脚本
"""
import json
import os

from faker import Faker
from pymysql import IntegrityError

from Data_import.common.Common import Common
from Data_import.mode.login import Login
from Data_import.mysql.mysql import Mysql
from Data_import.mode.userAgent import UserAgent


class Add_Goods:
    def __init__(self):
        info = Login().login()
        self.sess = info[0]
        self.token = info[1]
        self.useragent = UserAgent().useragent_list()

    def add_goods(self, specId, specValue, isrecommend, status, goodsimages, goodsimagem, goodsimagel, name, productionplace, goodsWeights, goods_weight,
                  typeid, brandid, warehouseid, amount, costprice, saleprice, goodsdesc, inquiry, metaDescription, metaKeywords, metaTitle, urlKey, minBuyCount, sku):
        """
        添加商品接口
        :param goods_weight: 商品重量
        :param goodsWeights: 商品权重
        :param sku: 用于区分新老数据字段
        :param minBuyCount:
        :param urlKey:
        :param metaTitle:
        :param metaKeywords:
        :param metaDescription:
        :param inquiry: 是否询价
        :param specId: 规格ID，选填
        :param specValue: 规格属性，选填
        :param isrecommend: 是否推荐
        :param status: 是否上架
        :param goodsimages: 小尺寸图片
        :param goodsimagem: 中尺寸图片
        :param goodsimagel: 大尺寸图片
        :param name: 商品名称
        :param productionplace:产地
        :param typeid: 所属类型ID
        :param brandid: 所属品牌ID
        :param warehouseid: 仓库ID
        :param amount: 商品数量
        :param costprice: 商品成本价格
        :param saleprice: 商品销售价格
        :param goodsdesc: 商品描述
        :return: res.json() JSON结果,data
        """
        url = 'http://18.118.13.94:8080/jeecg-boot/sys/api/goods/add'
        headers = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '701',
                   'Accept': 'application/json,text/plain,*/*', 'X-TIMESTAMP': '20220513165624',
                   'X-Sign': 'D1E72D505119D2AC33AA71F8E7D9ECF6', 'tenant-id': '0',
                   'X-Access-Token': f'{self.token}',
                   'User-Agent': f'{self.useragent}',
                   'Content-Type': 'application/json', 'Origin': 'http://18.118.13.94', 'Referer': 'http://18.118.13.94/',
                   'Accept-Encoding': 'gzip,deflate', 'Accept-Language': 'zh-CN,zh;q=0.9'}
        data = {"speciArr": [{"specId": f"{specId}", "specValue": f"{specValue}"}],
                "isrecommend": f"{isrecommend}",
                "status": f"{status}",
                "inquiry": f"{inquiry}",
                "metaDescription": f"{metaDescription}",
                "metaKeywords": f"{metaKeywords}",
                "metaTitle": f"{metaTitle}",
                "urlKey": f"{urlKey}",
                "goodsimages": f"{goodsimages}",
                "goodsimagem": f"{goodsimagem}",
                "goodsimagel": f"{goodsimagel}",
                "name": f"{name}",
                "productionplace": f"{productionplace}",
                "typeid": f"{typeid}",
                "brandid": f"{brandid}",
                "warehouseid": f"{warehouseid}",
                "amount": f"{amount}",
                "costprice": f"{costprice}",
                "saleprice": f"{saleprice}",
                "minBuyCount": f"{minBuyCount}",
                "goodsdesc": f"<p>{goodsdesc}</p>",
                "goods_weight": f"{goods_weight}",  # 未添加进去
                "sku": f"{sku}",  # 未添加进去
                "goodsWeights": f"{goodsWeights}",  # 未添加进去
                }
        data = json.dumps(data)
        print(data)
        res = self.sess.post(url=url, headers=headers, data=data)
        print(res.json())
        return res, data

    def main(self):
        faker = Faker()
        try:
            os.remove('../log/add_goods_log')  # 删除先前日志文件
        except FileNotFoundError:
            pass
        local_con, local_cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        sql = 'select * from product_data_1 limit 1925,9000;'
        infos = Mysql().dql(local_cur, sql)  # 查询所有商品数据
        print(len(infos))
        success = 0  # 计算成功数量
        erro = 0  # 计算失败数量
        n = 0  # 计算测试所在位置
        for info in infos:
            try:
                n += 1

                query_spec_id = 'SELECT id FROM goods_spec ORDER BY RAND() LIMIT 1;'
                spec_id = Mysql().dql(local_cur, query_spec_id)[0]['id']

                spec_Value = faker.ean13()

                images = info['img']
                print(images)
                if images is None:
                    images = ''
                images_url = 'https://okmarts.com/pub/media/catalog/product/cache/738c201810d2c9c0374e9315f59a743f' + images


                name = info['product_name']

                productionplace = faker.country()

                typename = info['category_name']
                query_type_id = f'select typeid from typeid_typeone where typeone="{typename}";'
                typeid = Mysql().dql(local_cur, query_type_id)[0]['typeid']

                brand_name = info['brand_name']
                query_brand_id = f'select brand_id from brand_id_name where brand_name="{brand_name}"'
                brand_id = Mysql().dql(local_cur, query_brand_id)[0]['brand_id']

                query_warehouse_id = 'select id from warehouse order by RAND() LIMIT 1;'
                warehouse_id = Mysql().dql(local_cur, query_warehouse_id)[0]['id']

                costprice = info['cost_price']
                if float(costprice) == 0:
                    costprice = 1

                saleprice = info['price']
                if float(saleprice) == 0:
                    saleprice = 1

                goodsdesc = info['product_description']

                inquiry = info['is_quote']

                metaDescription = info['meta_description']

                metaKeywords = info['meta_keywords']

                metaTitle = info['meta_title']

                urlKey = info['url_t']

                amount = info['qty']
                print(type(amount))
                if amount == 0:
                    amount = 1

                minBuyCount = info['min_sale_qty']

                sku = info['sku']

                goods_weight = info['weight']  # 重量

                goodsWeights = int(info['position']) - 200

                res = self.add_goods(specId=spec_id, specValue=spec_Value, isrecommend=1, status=1, goodsimages=images_url, sku=sku, goods_weight=goods_weight,
                                     goodsWeights=goodsWeights, metaDescription=metaDescription, metaKeywords=metaKeywords, metaTitle=metaTitle, urlKey=urlKey,
                                     goodsimagem=images_url, goodsimagel=images_url, name=name, productionplace=productionplace, typeid=typeid, brandid=brand_id,
                                     warehouseid=warehouse_id, amount=amount, costprice=costprice, saleprice=saleprice, goodsdesc=goodsdesc, inquiry=inquiry,
                                     minBuyCount=minBuyCount)
                assert '操作成功' in res[0].json()['message']
                success += 1
            except AssertionError:
                erro_info = f'商品添加模块，第{n}条数据错误, 错误信息为: {res[0].json()["message"]} ,data 为{res[1]}   \n'
                print(erro_info)
                Common().erro_log(log_path=r'../log/add_goods_log', erro_info=erro_info)
                erro += 1
            finally:
                print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
                print(f'分割线'.center(60, '-'))
        Mysql().close(local_con, local_cur)

    def create_goodstable(self):
        """
        分表
        :return:
        """
        con, cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)  # 建立链接
        num = 0
        for i in range(1, 80):  # 估计大概需要多少张表，做遍历添加
            name = 'product_data_' + f"{i}"  # 名字遍历生成 product_data_1，product_data_2
            try:
                sql_delete_table = f'drop table {name}'  # 此段代码是测试阶段使用，以免每次添加都会报 该表已存在的 错
                cur.execute(sql_delete_table)
            except:
                pass
            # 建表操作，建表之前需要去原表复制其表结构
            sql_createTb = f"""CREATE TABLE {name} (               
                             category_id INT,
                             brand_id INT,
                             category_name  varchar(255),
                             brand_name varchar(255),
                             product_id INT NOT NULL ,
                             sku varchar(255),
                             position INT,
                             price decimal,
                             cost_price decimal,
                             is_quote INT,
                             qty INT,
                             min_sale_qty int,
                             min_sale_qty_original INT,
                             weight DOUBLE,
                             product_name VARCHAR(255),
                             product_description TEXT,
                             product_short_description TEXT,
                             url VARCHAR(255),
                             meta_title VARCHAR(255),
                             meta_description VARCHAR(255),
                             meta_keywords TEXT,
                             img VARCHAR(255),
                             url_t VARCHAR(255),
                             PRIMARY KEY(product_id))
                             """
            cur.execute(sql_createTb)  # 提交请求
            print(f'表{name} 创建成功'.center(60, '-'))  # 检测是否建立成功，没有成功则报错
            sql = f"""INSERT into {name} SELECT * FROM all_product_data ORDER BY product_id LIMIT {num},10000;"""  # 遍历查询原表数据 添加到新表，
            Mysql().dml(con, cur, sql)  # 提交数据
            num += 10000  # 累加 下次查询下一万条数据
            print(f'表{name} 数据添加成功'.center(60, '-'))  # 检测是否添加成功，未添加成功则报错
        Mysql().close(con, cur)  # 关闭链接

    def add_typeinfo_to_local(self):

        """
        将线上数据库中的 品牌、类型、规格、仓库 中的name 、ID 加入到本地，加快添加速度
        :return:
        """
        local_con, local_cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        con, cur = Mysql().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)

        clear_type_sql = 'TRUNCATE TABLE typeid_typeone'
        clear_brand_sql =  'TRUNCATE TABLE brand_id_name'
        clear_warehouse_sql = 'TRUNCATE TABLE warehouse'
        clear_goods_spec_sql = 'TRUNCATE TABLE goods_spec'

        local_cur.execute(clear_type_sql)
        local_cur.execute(clear_brand_sql)
        local_cur.execute(clear_warehouse_sql)
        local_cur.execute(clear_goods_spec_sql)
        local_con.commit()  # 所有SQL执行完成后，提交事务

        sql_type = 'select typeone,id from goods_type'
        infos = Mysql().dql(cur, sql_type)

        for info in infos:
            print(info)
            insert_type = f"""insert into typeid_typeone(typeid,typeone) value('{info["id"]}','{info["typeone"]}')"""
            Mysql().dml(local_con, local_cur, insert_type)

        sql_brand = 'select name,id from goods_brand'
        brands = Mysql().dql(cur,sql_brand)

        for brand in brands:
            print(brand)
            insert_brand = f"""insert into brand_id_name(brand_id,brand_name) value('{brand["id"]}','{brand["name"]}')"""
            Mysql().dml(local_con,local_cur,insert_brand)

        sql_warehouse = 'select id,name from warehouse'
        warehouses = Mysql().dql(cur, sql_warehouse)
        for warehouse in warehouses:
            print(warehouse)
            insert_warehouse = f"""insert into warehouse(id,name) value('{warehouse["id"]}','{warehouse["name"]}')"""
            Mysql().dml(local_con, local_cur, insert_warehouse)

        sql_goods_spec = 'select id,name from goods_spec'
        specs = Mysql().dql(cur,sql_goods_spec)
        for spec in specs:
            print(spec)
            insert_specs = f"""insert into goods_spec(id,spec_name) value('{spec["id"]}','{spec["name"]}')"""
            Mysql().dml(local_con, local_cur, insert_specs)
        Mysql().close(con, cur)
        Mysql().close(local_con, local_cur)

    def check_requests(self):
        url = 'http://18.118.13.94:8080/jeecg-boot/sys/api/goods/add'
        headers = {'Host': '18.118.13.94:8080', 'Connection': 'keep-alive', 'Content-Length': '701',
                   'Accept': 'application/json,text/plain,*/*', 'X-TIMESTAMP': '20220513165624',
                   'X-Sign': 'D1E72D505119D2AC33AA71F8E7D9ECF6', 'tenant-id': '0',
                   'X-Access-Token': f'{self.token}',
                   'User-Agent': f'{self.useragent}',
                   'Content-Type': 'application/json', 'Origin': 'http://18.118.13.94', 'Referer': 'http://18.118.13.94/',
                   'Accept-Encoding': 'gzip,deflate', 'Accept-Language': 'zh-CN,zh;q=0.9'}
        data ={"speciArr": [{"specId": "1503307464130658305", "specValue": "7156015379150"}],
               "isrecommend": "1", "status": "1", "inquiry": "1",
               "metaDescription": "Supply of Berger Lahr Servo Motor IFS93/2DPOISDS/1DI-I54/O-001RPP41, Berger Lahr HDS05.2-W300N-HS12-01-FW, Berger Lahr Servo Drive, Berger Lahr Servo Product from Okmarts industrial supply, which provides professional solution for your business.",
               "metaKeywords": "IFS93/2DPOISDS/1DI-I54/O-001RPP41,Servo IFS93/2DPOISDS/1DI-I54/O-001RPP41,Servo Motor IFS93/2DPOISDS/1DI-I54/O-001RPP41,Berger Lahr Servo Motor IFS93/2DPOISDS/1DI-I54/O-001RPP41,Berger Lahr IFS93/2DPOISDS/1DI-I54/O-001RPP41",
               "metaTitle": "Berger Lahr Servo Motor IFS93/2DPOISDS/1DI-I54/O-001RPP41 - Berger Lahr Servo Drive - Berger Lahr Servo Product - Okmarts Supply",
               "urlKey": "berger-lahr-servo-motor-ifs93-2dpoisds-1di-i54-o-001rpp41.html",
               "goodsimages": "https://okmarts.com/pub/media/catalog/product/cache/738c201810d2c9c0374e9315f59a743f/i/f/ifs93-2dpoisds-1di-i54-o-001rpp41.jpg",
               "goodsimagem": "https://okmarts.com/pub/media/catalog/product/cache/738c201810d2c9c0374e9315f59a743f/i/f/ifs93-2dpoisds-1di-i54-o-001rpp41.jpg",
               "goodsimagel": "https://okmarts.com/pub/media/catalog/product/cache/738c201810d2c9c0374e9315f59a743f/i/f/ifs93-2dpoisds-1di-i54-o-001rpp41.jpg",
               "name": "Berger Lahr Servo Motor IFS93/2DPOISDS/1DI-I54/O-001RPP41", "productionplace": "Guyana", "typeid": "1527198271380049921",
               "brandid": "1527198427273940994", "warehouseid": "1503306510501117953", "amount": "800", "costprice": "32099", "saleprice": "12346",
               "minBuyCount": "1", "goodsdesc": "<p>The Berger Lahr Servo Motor is high quality!</p>", "goods_weight": "10.0", "sku": "BLSM-004", "goodsWeights": "0"}
        data = json.dumps(data)
        print(data)
        res = self.sess.post(url=url, headers=headers, data=data)
        print(res.json())

    def insert_by_sql(self):
        """
        通过SQL语言直接插入数据库
        :return:
        """
        try:
            os.remove('../log/add_goods_by_sql_log')  # 删除先前日志文件
        except FileNotFoundError:
            pass
        con, cur = Mysql().con_db(user="root", pwd="OKmarts888.,", host="18.118.13.94", db="okmarts", port=3306)
        local_con, local_cur = Mysql().con_db(user='root', pwd="root", host='localhost', db='goodspic', port=3306)
        sql = 'select * from product_data_1 limit 1723,9000;'
        faker = Faker()
        infos = Mysql().dql(local_cur, sql)  # 查询所有商品数据
        success = 0  # 计算成功数量
        erro = 0  # 计算失败数量
        n = 0  # 计算测试所在位置
        for info in infos:
            n += 1
            print(info)
            query_spec_id = 'SELECT id FROM goods_spec ORDER BY RAND() LIMIT 1;'
            spec_id = Mysql().dql(local_cur, query_spec_id)[0]['id']

            spec_Value = faker.ean13()

            images = info['img']
            if images is None:
                images_url = ''
            else:
                images_url = 'https://okmarts.com/pub/media/catalog/product/cache/738c201810d2c9c0374e9315f59a743f' + images

            name = info['product_name']

            productionplace = faker.country()

            typename = info['category_name']
            query_type_id = f'select typeid from typeid_typeone where typeone="{typename}";'
            typeid = Mysql().dql(local_cur, query_type_id)[0]['typeid']

            brand_name = info['brand_name']
            query_brand_id = f'select brand_id from brand_id_name where brand_name="{brand_name}"'
            brand_id = Mysql().dql(local_cur, query_brand_id)[0]['brand_id']

            query_warehouse_id = 'select id from warehouse order by RAND() LIMIT 1;'
            warehouse_id = Mysql().dql(local_cur, query_warehouse_id)[0]['id']

            costprice = info['cost_price']
            if float(costprice) == 0:
                costprice = 0.00001

            saleprice = info['price']
            if float(saleprice) == 0:
                saleprice = 0.00001

            goodsdesc = info['product_description']

            inquiry = info['is_quote']

            metaDescription = info['meta_description']

            metaKeywords = info['meta_keywords']

            metaTitle = info['meta_title']

            urlKey = info['url_t']

            amount = info['qty']

            if amount == 0:
                amount = 1

            minBuyCount = info['min_sale_qty']

            sku = info['sku']

            goods_weight = info['weight']  # 重量

            goodsWeights = int(info['position']) - 200

            goodsno = faker.ean13()

            try:
                insert_sql = f"""insert into goods(id,goodsImageS,goodsImageM,goodsImageL,name,productionPlace,typeid,brandid,warehouseid,amount,costPrice,salePrice,
                            goodsDesc,isRecommend,status,goodsWeights,goods_weight,specid,inquiry,url_key,meta_title,meta_keywords,meta_description,min_buy_count,goodsno) 
                            value("{sku}","{images_url}","{images_url}","{images_url}","{name}","{productionplace}","{typeid}","{brand_id}","{warehouse_id}","{amount}","{costprice}","{saleprice}",
                            "{goodsdesc}",1,1,"{goodsWeights}","{goods_weight}","{spec_id}","{inquiry}","{urlKey}","{metaTitle}","{metaKeywords}","{metaDescription}","{minBuyCount}","{goodsno}")"""
                Mysql().dml(con, cur, insert_sql)
                success += 1
            except IntegrityError:
                print('已存在该商品')
                erro += 1
                erro_info = f'出错啦，id为{sku}'
                Common().erro_log(log_path=r'../log/add_goods_by_sql_log', erro_info=erro_info)
            finally:
                print(f'第{n}次操作完成,共存在{erro}次错误,成功{success}次')
                print(f'分割线'.center(60, '-'))
        Mysql().close(con, cur)
        Mysql().close(local_con,local_cur)

if __name__ == '__main__':
    a = Add_Goods()
    # a.insert_by_sql()
    a.main()
    # a.check_requests()
