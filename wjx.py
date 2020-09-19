from multiprocessing import cpu_count, Process, Manager, Queue
class config:
    debug=False
    warn_num=375
    branch="devel"
    version=1.1
    zip_version=1.0
def process_log(queue):
    import logging
    logger_=logging.getLogger()
    if config.debug==True:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO
    logger_.setLevel(log_level)
    formatter=logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
    handler=logging.FileHandler(filename="works.log",mode="w",encoding="utf-8",delay=True)
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    while True:
        record=queue.get()
        if record==None:
            break
        logger=logging.getLogger(record.name)
        logger.handle(record)
def multicoreproc(id_:int,url_:str,times:int,queue):
    import logging
    import random
    import time
    import logging.handlers
    max_conn=3
    failed_num=0
    thread_logger=logging.getLogger()
    handler=logging.handlers.QueueHandler(queue)
    thread_logger.addHandler(handler)
    if config.debug==True:
        thread_logger.setLevel(logging.DEBUG)
    else:
        thread_logger.setLevel(logging.INFO)
    thread_logger.info("开始执行线程 %d 的工作内容" %id_)
    def do_survey(url_2:str,thread_id:int):
        import time
        import random
        from selenium import webdriver
        from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions
        browser=webdriver.ChromeOptions()
        browser.binary_location="./Chrome/App/chrome.exe"
        if config.debug==False:
            browser.add_argument("headless")
        try:
            driver = webdriver.Chrome(executable_path="./Chrome/app/chromedriver.exe",options=browser)
        except WebDriverException:
            thread_logger.error("线程 %d 初始化浏览器驱动程序失败" %thread_id)
            return False
        try:
            driver.get(url_2)
        except WebDriverException:
            thread_logger.error("线程 %d 连接目标网址失败，请检查网络连接后重试" %thread_id)
            return False
        try:
            element = WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.ID,'submit_button')))
        except TimeoutException:
            thread_logger.error("线程 %d 连接网络超时，请检查网络连接后重试" %thread_id)
            return False
        def do_queue(driver_=driver):
            question_elements=driver_.find_elements_by_xpath('//div[@class="div_question"]')
            def gen_str(num:int):
                import string
                return ''.join(random.sample(string.ascii_letters + string.digits, num))    
            for question_element in question_elements:
                question_element_pos=question_elements.index(question_element)
                title_element=question_element.find_element_by_class_name("div_title_question")
                question_title=title_element.text
                question_answers=question_element.find_elements_by_tag_name("li")
                if len(question_answers)==0:
                    question_answers=[question_element.find_element_by_tag_name("textarea")]
                removed_num=0
                for item in question_answers:
                    if item.get_attribute("class")=="notchoice":
                        question_answers.remove(item)
                        removed_num=removed_num+1
                thread_logger.info("线程 %d 已清理无效元素共 %d 个" %(thread_id,removed_num))
                try:
                    sample_element=question_answers[0].find_element_by_tag_name("input")
                except NoSuchElementException:
                    sample_element=question_answers[0]
                if sample_element.get_attribute("type")=="radio":
                    targets=random.sample(question_answers,1)
                    choose_answer_title=targets[0].find_element_by_tag_name("label").text
                    targets[0].find_element_by_tag_name("a").click()
                    time.sleep(random.randint(1,3))
                elif sample_element.get_attribute("type")=="checkbox":
                    choose_num=random.randint(2,len(question_answers))
                    choose_answers=[]
                    choose_answers_pos=[]
                    choose_answer_title=""
                    try:
                        span_element=title_element.find_element_by_tag_name("span")
                    except NoSuchElementException:
                        thread_logger.debug("线程 %d 未找到最大选择数量限制" %id_)
                    else:
                        b_elements=span_element.find_elements_by_tag_name("b")
                        if len(b_elements)>=2:
                            max_num=int(b_elements[1].text)
                            if max_num>2:
                                choose_num=random.randint(2,max_num)
                                thread_logger.debug("线程 %d 找到最大选择数量为 %d" %(id_,max_num))
                        else:
                            thread_logger.debug("线程 %d 未找到最大选择数量限制" %id_)
                    targets=random.sample(question_answers,choose_num)
                    for target in targets:
                        choose_answers.append(target)
                        choose_answers_pos.append(question_answers.index(target))
                    text=""
                    choose_answer_title=""
                    for answer in choose_answers:
                        answer.find_element_by_tag_name("a").click()
                        choose_answer_title=choose_answer_title+answer.find_element_by_tag_name("label").text
                        if len(answer.find_elements_by_tag_name("input"))==2:
                            text_input=answer.find_elements_by_tag_name("input")[1]
                            text_input.click()
                            text_input.clear()
                            text=gen_str(random.randint(5,10))
                            text_input.send_keys(text)
                            choose_answer_title=choose_answer_title+text+"\n"
                        else:
                            choose_answer_title=choose_answer_title+"\n"
                        time.sleep(random.randint(1,3))
                elif sample_element.get_attribute("class")=="inputtext":
                    target=question_answers[0]
                    target.click()
                    target.clear()
                    text=gen_str(random.randint(10,20))
                    target.send_keys(text)
                    choose_answer_title=text+"\n"
                else:
                    raise RuntimeError("无法获取正确的元素，请重试！")
                thread_logger.info("线程 "+str(thread_id)+" 选择内容：\n问题："+question_title+"\n选择："+choose_answer_title+"\n")
        do_queue(driver_=driver)
        time.sleep(random.randint(1,3))
        driver.find_element_by_tag_name("td").find_element_by_tag_name("input").click()
        try:
            target=driver.find_element_by_xpath('//span[@id="SM_TXT_1"]')
        except NoSuchElementException:
            thread_logger.info("线程 %d 未找到验证元素，看起来没有触发验证" %thread_id)
            driver.quit()
            return True
        else:
            thread_logger.warning("线程 %d 找到验证元素，似乎已经触发验证，已记录失败次数" %thread_id)
            if target.get_attribute("id")=="SM_BTN_1":
                def bypass_captcha(driver_,element_):
                    pass
                bypass_captcha(driver_=driver,element_=target)
            driver.quit()
            return False
    if times>0:
        if times<=max_conn:
            for time0 in range(times):
                if do_survey(url_2=url_,thread_id=id_)==False:
                    failed_num=failed_num+1
                    thread_logger.error("线程 %d 第 %d 次提交失败" %(id_,time0))
                else:
                    thread_logger.info("线程 %d 第 %d 次提交成功" %(id_,time0))
                time.sleep(random.randint(1,3))
        else:
            times1,more_times=divmod(times,max_conn)
            if more_times!=0:
                group=-1
                for time1 in range(more_times):
                    if do_survey(url_2=url_,thread_id=id_)==False:
                        failed_num=failed_num+1
                        thread_logger.error("线程 %d 第 %d 组第 %d 次提交失败" %(id_,group,time1))
                    else:
                        thread_logger.info("线程 %d 第 %d 组第 %d 次提交成功" %(id_,group,time1))
                    time.sleep(random.randint(1,3))
            for time2 in range(more_times,times1+more_times):
                for conn in range(max_conn):
                    if do_survey(url_2=url_,thread_id=id_)==False:
                        failed_num=failed_num+1
                        thread_logger.error("线程 %d 第 %d 组第 %d 次提交失败" %(id_,time2,conn))
                    else:
                        thread_logger.info("线程 %d 第 %d 组第 %d 次提交成功" %(id_,time2,conn))
                    time.sleep(random.randint(1,3))
                time.sleep(random.randint(3,5))
    else:
        raise ValueError("执行次数必须为正整数")
    if failed_num>0:
        pause_time=random.randint(10,60)
        thread_logger.warning("线程 %d 失败 %d 次，等待 %2d 秒后将继续补齐失败次数" %(id_,failed_num,pause_time))
        times=failed_num
        time.sleep(pause_time)
        multicoreproc(id_=id_,url_=url_,times=times,queue=queue)
    thread_logger.info("线程 %d 结束运行" %id_)
if __name__=="__main__":
    import os 
    import shutil
    import logging
    import logging.handlers
    import subprocess
    import time
    if os.name!="nt":
        raise RuntimeError("此脚本仅支持Windows XP SP2及更高版本")
    if config.debug==True:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    queue=Queue(-1)
    logger=logging.getLogger()
    logger.setLevel(log_level)
    formatter=logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
    console=logging.StreamHandler()
    console.setFormatter(formatter)
    queue_handler=logging.handlers.QueueHandler(queue)
    logger.addHandler(console)
    logger.addHandler(queue_handler)
    def gen_bootstrap():
        import sys
        lines=[
            "@echo off\n",
            "%1 mshta vbscript:CreateObject(\"Shell.Application\").ShellExecute(\"cmd.exe\",\"/c %~s0 ::\",\"\",\"runas\",1)(window.close)&&exit\n",
            "cd /d \"%~dp0\"\n",
            "(echo selenium==3.141.0\necho requests==2.23.0) > requirements.txt\n",
            "\""+sys.executable+"\" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\n",
            "reg ADD HKLM\SOFTWARE\Policies\Google\Chrome /v RendererCodeIntegrityEnabled /t REG_DWORD /d 0 /f\n",
            "del /F /S /Q requirements.txt\n"]
        with open("bootstrap.bat","w",encoding="utf-8") as generator:
            generator.writelines(lines)
    def unpack(md5_:str):
        import hashlib
        import zipfile
        with open("Chrome/env.zip","rb") as file_reader:
            md5=hashlib.md5(file_reader.read()).hexdigest()
        if md5==md5_ or md5_=="":
            if md5_=="":
                logger.warning("未传入压缩文件的MD5值，跳过验证")
            with zipfile.ZipFile("Chrome/env.zip","r",compression=zipfile.ZIP_DEFLATED) as archive:
                archive.extractall("Chrome")
            os.remove("Chrome/env.zip")
            return 0
        else:
            logger.error("文件MD5不符，终止解压缩")
            return 1
    def down_env(addr_head:str,zip_md5="dcf2981ec68a72e206f949066ee8eedd",version="1.0"):
        import requests
        envaddr=addr_head+"/zhanghua000/wjx-auto-generator-env/releases/download/"+str(version)+"/env.zip"
        if os.path.exists("Chrome/env.zip")==False:
            with open("Chrome/env.zip","wb") as file_downloader:
                file_downloader.write(requests.get(envaddr).content)
        if unpack(zip_md5)==1:
            logger.warning("下载失败，请手动下载 "+envaddr+" 并以 env.zip 的文件名保存到Chrome目录下，之后重启程序")
            return 1
        else:
            return 0
    def check_stat(list_:list):
        import requests
        result=[]
        for addr in list_:
            resp=requests.get(addr)
            if resp.status_code==200:
                result.append(addr)
        return result
    def check_update(server:str):
        import requests
        import hashlib
        import zipfile
        address=server+"/zhanghua000/wjx-auto-generator-env/raw/master/version.json"
        try:
            response=requests.get(address)
            version_inf=response.json()
        except:
            logger.error("检查更新失败")
            return -1
        if version_inf["version"]>config.version:
            logger.info("已发现脚本更新")
            ans=input("是否下载新版本？(Y/n)").lower()
            if ans=="n":
                return 2
            if config.branch!=version_inf["branch"]:
                logger.error("升级信息中的分支与实际分支不符")
                return 4
            r=requests.get(server+"/zhanghua000/wjx-auto-generator/raw/"+str(version_inf["branch"])+"/wjx.py")
            shutil.copy("wjx.py","wjx.py.bak")
            with open("wjx.py","w",encoding="utf-8") as updater:
                updater.write(r.read)
            with open("wjx.py","rb") as md5_checker:
                md5=hashlib.md5(md5_checker.read()).hexdigest()
                if md5!=version_inf["scr_md5"]:
                    logging.error("MD5验证失败，取消本次更新")
                    shutil.move("wjx.py.bak","wjx.py")
                    return 1
        else:
            logger.info("未发现脚本更新")
        if version_inf["zip_version"]>config.zip_version:
            logger.info("已发现运行环境更新")
            ans=input("是否下载新版本？(Y/n)").lower()
            if ans=="n":
                return 2
            shutil.rmtree("Chrome")
            os.mkdir("Chrome")
            logger.info("正在更新运行环境至 %f" %version_inf["zip_version"])
            re=down_env(server,zip_md5=version_inf["zip_md5"],version=version_inf["zip_version"])
            if re==1:
                return 1
        else:
            logger.info("未发现运行环境更新")
            return 3
        return 0
    try:
        import requests
        from selenium import webdriver
    except:
        logger.info("正在初始化依赖环境。。。")
        gen_bootstrap()
        try:
            subprocess.run("bootstrap.bat")
        except:
            raise RuntimeError("初始化依赖环境失败，请手动执行 bootstrap.bat 完成初始化。弹出的UAC认证提示请予以通过")
        else:
            os.remove("bootstrap.bat")
            logger.info("初始化依赖环境完成")
    else:
        logger.info("依赖环境正常")
        if os.path.exists("bootstrap.bat")==True:
            os.remove("bootstrap.bat")
        if os.path.exists("Chrome/env.zip")==True:
            unpack("")
    if os.path.exists("Chrome")==False:
        os.mkdir("Chrome")
    if os.path.exists("Chrome/App/chrome.exe")==False:
        logger.info("正在初始化运行环境。。。")
        if down_env("https://download.fastgit.org")==1:
            raise RuntimeError("下载运行环境出错，请检查网络连接后重试")
    res=check_update("https://hub.fastgit.org")
    if res==-1:
        logger.error("下载版本信息失败")
    elif res==0:
        logger.info("更新成功")
    elif res==1:
        logger.error("文件下载出错，验证失败")
    elif res==2:
        logger.warning("更新已被用户取消")
    elif res==3:
        logger.info("未发现更新")
    elif res==4:
        logger.error("检查更新过程出现错误")
    else:
        raise ValueError("意料之外的返回值")
    times=int(input("请输入生成的问卷的份数："))
    if times>=config.warn_num:
        logger.warning("当前问卷份数较多，大于 %s 次，较易出现验证。" %config.warn_num)
    print("问卷星地址举例：https://www.wjx.cn/jq/89714348.aspx")
    url=str(input("请输入问卷星创建的问卷地址："))
    url="https://www.wjx.cn/jq/"+url.split("/")[-1].replace(" ","")
    logger.info("转换地址完成，为："+url)
    start_time=time.time()
    threads=[]
    thread_num=int(cpu_count()/2)
    times_,more_times_=divmod(times,thread_num)
    logger_process=Process(target=process_log,args=(queue,))
    logger_process.start()
    if more_times_!=0:
        more_thread=Process(target=multicoreproc,args=(thread_num+1,url,more_times_,queue))
        more_thread.start()
        threads.append(more_thread)
    if times_!=0:
        for thread_id in range(thread_num):
            thread=Process(target=multicoreproc,args=(thread_id,url,times_,queue))
            thread.start()
            threads.append(thread)
    if len(threads)!=0:
        for thread_ in threads:
            thread_.join()
    m,s=divmod(int(time.time()-start_time),60)
    h,m=divmod(m,60)
    logger.info("执行完成，选择内容可查看日志文件输出记录，用时 %02d:%02d:%02d 共提交 %d 份问卷。具体选择内容请参考脚本目录下的 record.log 文件" %(h, m, s, times))
    queue.put_nowait(None)
    logger_process.join()