# bookstore

> 作业内容说明和要求文档为参见源代码处<br>

**1.实现功能<br>**

- 实现一个提供网上购书功能的网站后端。<br>
- 网站支持书商在上面开商店，购买者可以通过网站购买。<br>
- 买家和卖家都可以注册自己的账号。<br>
- 一个卖家可以开一个或多个网上商店。
- 买家可以为自已的账户充值，在任意商店搜索图书、购买图书。<br>
- 支持 下单->付款->发货->收货 流程。<br>

1)用户权限接口，注册、登录、修改密码、登出、注销<br>

2)买家用户接口，充值、下单、订单确认、订单状态、订单查询、订单收货、付/退款<br>

3)卖家用户接口，创建店铺、填加书籍信息及描述、增加库存、订单发货、收款<br>

4)利用文本索引搜索图书 <br>

通过对应的功能测试，所有 test case 都 pass <br>

## bookstore目录结构
```
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试
        |-- conf.py                   测试参数
        |-- conftest.py               pytest初始化配置
        |-- ....
  |-- ....
```

## 安装配置
安装 python (需要 python3.6 以上) 

进入 bookstore 文件夹下：

安装依赖

```powershell
pip install -r requirements.txt
```

执行测试
```bash
bash script/test.sh
```

（注意：如果提示`"RuntimeError: Not running with the Werkzeug Server"`，请输入下述命令，将 flask 和 Werkzeug 的版本均降低为2.0.0。）

```powershell
 pip install flask==2.0.0  

 pip install Werkzeug==2.0.0
```

## 备注

1.bookstore 文件夹是该项目的 demo，采用 Flask 后端框架与 MongoDB 数据库，实现了所有功能以及对应的测试用例代码。
 bookstore/fe/data/book.db中包含测试的数据，从豆瓣网抓取的图书信息，
 其DDL为：

    create table book
    (
        id TEXT primary key,
        title TEXT,
        author TEXT,
        publisher TEXT,
        original_title TEXT,
        translator TEXT,
        pub_year TEXT,
        pages INTEGER,
        price INTEGER,
        currency_unit TEXT,
        binding TEXT,
        isbn TEXT,
        author_intro TEXT,
        book_intro text,
        content TEXT,
        tags TEXT,
        picture BLOB
    );
实操中忽略了picture。
    
2.对程序与数据库执行的性能有考量，使用了索引

3.项目完成过程中使用了git 等版本管理工具

4.未实现界面，只通过代码测试体现功能与正确性

5.覆盖率：
<img width="416" alt="image" src="https://github.com/user-attachments/assets/f96569cf-f314-4144-9411-1ff837b2c4b0">

