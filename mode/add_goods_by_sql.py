"""
#共789,237 条商品数据

#插入ID
insert into goods(id) select product_id from all_product_data_new ;

#更新name
update goods set name=(SELECT product_name from all_product_data_new where all_product_data_new.product_id = goods.id);
#更新图片  IMGs、l、m

update goods set goodsImageS=CONCAT("http://18.118.13.94:8080/jeecg-boot/sys/common/view/temp",(SELECT img from all_product_data_new where all_product_data_new.product_id = goods.id));

update goods set goodsImageM=CONCAT("http://18.118.13.94:8080/jeecg-boot/sys/common/view/temp",(SELECT img from all_product_data_new where all_product_data_new.product_id = goods.id)),goodsImageL=CONCAT("http://18.118.13.94:8080/jeecg-boot/sys/common/view/temp",(SELECT img from all_product_data_new where all_product_data_new.product_id = goods.id));

#更新类型ID
update goods set typeid=(select id from goods_type where typeone = (SELECT category_name from all_product_data_new where all_product_data_new.product_id = goods.id));

#更新仓库
update goods set warehouseid='1503306485733752834';

#更新数量 amount
update goods set amount=(SELECT qty from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新成本价格销售价格
update goods set costPrice=(SELECT cost_price from all_product_data_new where all_product_data_new.product_id = goods.id),salePrice=(SELECT price from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新描述，是否推荐，状态
update goods set goodsDesc=(SELECT product_description from all_product_data_new where all_product_data_new.product_id = goods.id),isRecommend=1,status=1;

#更新商品权重
update goods set goodsWeights=200 - (SELECT position from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新商品重量
update goods set goods_weight=(SELECT weight from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新是否询盘
update goods set inquiry=(SELECT is_quote from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新URL_key
update goods set url_key=(SELECT url_t from all_product_data_new where all_product_data_new.product_id = goods.id);

# #更新meta_title,meta_keywords,meta_description,min_buy_count
update goods set
meta_title=(SELECT meta_title from all_product_data_new where all_product_data_new.product_id = goods.id),
meta_keywords=(SELECT meta_keywords from all_product_data_new where all_product_data_new.product_id = goods.id),
meta_description=(SELECT meta_description from all_product_data_new where all_product_data_new.product_id = goods.id),
min_buy_count=(SELECT min_sale_qty from all_product_data_new where all_product_data_new.product_id = goods.id);

#更新SKU
update goods set sku=(SELECT sku from all_product_data_new where all_product_data_new.product_id = goods.id);


--  # 更新品牌表之前修改 伺服产品相关名称： 使其名称变成 品牌名称 + 伺服类型
-- update all_product_data_new set brand_name = CONCAT(all_product_data_new.brand_name,' ',all_product_data_new.category_name) where category_name='Servo Drive';
--
-- update all_product_data_new set brand_name = CONCAT(all_product_data_new.brand_name,' ',all_product_data_new.category_name) where category_name='Servo Motor';
--
-- update all_product_data_new set brand_name = CONCAT(all_product_data_new.brand_name,' ',all_product_data_new.category_name) where category_name='Servo Valve';



CREATE TABLE brand_info (select c.brand_id,d.type_name,d.brand_name,d.typeid,d.product_id,d.product_name from
(select id as brand_id,name,goodstypeid from goods_brand) as c RIGHT JOIN (
select a.id as typeid,b.type_name,b.brand_name,b.product_id,b.product_name from
(select id,typeone from goods_type) as a RIGHT JOIN (SELECT category_name as type_name,brand_name, product_id,product_name from all_product_data_new) as b
on a.typeone = b.type_name
) as d
on c.`name` = d.brand_name and c.goodstypeid = d.typeid
order by c.brand_id);

alter table  brand_info  add  primary key(product_id);

update goods set brandid=(select brand_id from brand_info where brand_info.product_id=goods.id);


UPDATE `all_product_data_new` SET url_t = (SELECT request_path FROM `all-product-url-fz` WHERE `all_product_data_new`.product_id = `all-product-url-fz`.entity_id ) WHERE (`all_product_data_new`.url_t is NULL)

"""