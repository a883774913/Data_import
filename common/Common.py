import os


class Common:

    # 添加错误日志至相关文件中
    def erro_log(self,log_path,erro_info):
        """
        将错误信息卸任log目录下的log文件中
        :param log_path:  add_brand_log 文件地址
        :param erro_info: 错误日志信息
        :return:
        """
        with open(log_path,'a',encoding='utf-8') as f :
            f.write(erro_info)

    def useragent_list(self):
        useragent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
            'Fiddler/5.0.20211.51073 (.NET 4.8; WinNT 10.0.22000.0; zh-CN; 6xAMD64; Auto Update; Full Instance; Extensions: APITesting, AutoSaveExt, EventLog, FiddlerOrchestraAddon, HostsFile, RulesTab2, SAZClipboardFactory, SimpleFilter, Timeline)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3884.400 QQBrowser/10.8.4560.400',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0'
            ]
        return useragent_list



if __name__ == '__main__':
    a = Common()
    a.erro_log(log_path='../log/add_brand_log', erro_info='test')