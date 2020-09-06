import os 
import sys
if os.name!="nt":
    raise RuntimeError("此脚本仅支持Windows XP SP2及更高版本")
from multiprocessing import cpu_count
import time
import random
import threading
import shutil
import zipfile
import hashlib
import subprocess
import logging
debug=False
warn_num=375
if debug==True:
    log_level=logging.DEBUG
else:
    log_level=logging.INFO
os.chdir(os.path.split(os.path.realpath(__file__))[0])
if os.path.exists("log"):
    shutil.rmtree("log")
os.mkdir("log")
logger=logging.getLogger()
logger.setLevel(log_level)
formatter=logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
console=logging.StreamHandler()
console.setFormatter(formatter)
files_=logging.FileHandler(filename="log/main.log",mode="w",encoding="utf-8")
files_.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(files_)
def gen_bootstrap():
    lines=[
        "@echo off\n",
        "%1 mshta vbscript:CreateObject(\"Shell.Application\").ShellExecute(\"cmd.exe\",\"/c %~s0 ::\",\"\",\"runas\",1)(window.close)&&exit\n",
        "cd /d \"%~dp0\"\n",
        "(echo selenium==3.141.0\necho requests==2.23.0) > requirements.txt\n",
        "\""+sys.executable+"\" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\n",
        "reg ADD HKLM\SOFTWARE\Policies\Google\Chrome /v RendererCodeIntegrityEnabled /t REG_DWORD /d 0 /f\n",
        "del /F /S /Q requirements.txt\n"]
    with open("bootstrap.bat","w",encoding="utf-8") as gennerator:
        generator.writelines(lines)
try:
    import requests
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
except:
    logger.info("正在初始化依赖环境。。。")
    gen_bootstrap()
    re=subprocess.run("bootstrap.bat")
    if re.returncode==0:
        os.remove("bootstrap.bat")
        logger.info("初始化依赖环境完成")
    else:
        raise RuntimeError("初始化依赖环境失败，请手动执行 bootstrap.bat 完成初始化。弹出的UAC认证提示请予以通过")
else:
    logger.info("依赖环境正常")
    if os.path.exists("bootstrap.bat")==True:
        os.remove("bootstrap.bat")
    if os.path.exists("Chrome/env.zip")==True:
        os.remove("Chrome/env.zip")
if os.path.exists("Chrome")==False:
    os.mkdir("Chrome")
if os.path.exists("Chrome/App/chrome.exe")==False:
    logger.info("正在初始化运行环境。。。")
    envaddr_list=["https://github.wuyanzheshui.workers.dev","https://download.fastgit.org"]
    def unpack(md5_:str):
        with open("Chrome/env.zip","rb") as file_reader:
            md5=hashlib.md5(file_reader.read()).hexdigest()
        if md5==md5_:
            with zipfile.ZipFile("Chrome/env.zip","r",compression=zipfile.ZIP_DEFLATED) as archive:
                archive.extractall("Chrome")
            os.remove("Chrome/env.zip")
            return 0
        else:
            logger.error("文件MD5不符，终止解压缩")
            return 1
    def down_env(addr_head:str):
        if os.path.exists("Chrome/env.zip")==False:
            envaddr=addr_head+"/zhanghua000/wjx-auto-generator-env/releases/download/1.0/env.zip"
            with open("Chrome/env.zip","wb") as file_downloader:
                file_downloader.write(requests.get(envaddr).content)
        if unpack("dcf2981ec68a72e206f949066ee8eedd")==1:
            logger.warning("下载失败，请手动下载 "+envaddr+" 并以 env.zip 的文件名保存到Chrome目录下，之后重启程序")
            return 1
        else:
            return 0
    def check_stat(list_:list):
        result=[]
        for addr in list_:
            resp=requests.get(addr)
            if resp.status_code==200:
                result.append(addr)
        return result
    choosen_head=random.sample(check_stat(envaddr_list),1)[0]
    if down_env(choosen_head)==1:
        raise RuntimeError("下载运行环境出错，请检查网络连接后重试")
times=int(input("请输入生成的问卷的份数："))
if times>=warn_num:
    logger.warning("当前问卷份数较多，大于 %s 次，较易触发unknown error错误。如果触发，请重新执行脚本。" %warn_num)
print("问卷星地址举例：https://www.wjx.cn/jq/89714348.aspx")
url=str(input("请输入问卷星创建的问卷地址："))
url="https://www.wjx.cn/jq/"+url.split("/")[-1]
logger.info("转换地址完成，为："+url)
start_time=time.time()
def do_survey(url_2:str,logger_:logging.Logger):
    browser=webdriver.ChromeOptions()
    browser.binary_location="./Chrome/App/chrome.exe"
    if debug==False:
        browser.add_argument("headless")
    browser.add_argument("user-agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36\"")
    driver = webdriver.Chrome("./Chrome/app/chromedriver.exe",options=browser,service_log_path="log/driver.log")
    driver.get(url_2)
    wait = WebDriverWait(driver, 10)
    element = wait.until(expected_conditions.element_to_be_clickable((By.ID,'submit_button')))
    def do_queue(driver_=driver):
        root_element=driver_.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/fieldset")
        question_elements=root_element.find_elements_by_class_name("div_question")
        def gen_str(num:int):
            import string
            return ''.join(random.sample(string.ascii_letters + string.digits, num))
        for element in question_elements:
            element_pos=question_elements.index(element)
            question_title=element.find_element_by_xpath("./div[1]/div[2]").text
            question_answers=element.find_elements_by_xpath("./div[2]/ul/li")
            if question_answers[0].find_element_by_xpath("./input").get_attribute("type")=="radio":
                targets=random.sample(question_answers,1)
                choose_answer_title=targets[0].find_element_by_tag_name("label").text
                targets[0].find_element_by_tag_name("a").click()
                time.sleep(random.randint(1,3))
            elif question_answers[0].find_element_by_tag_name("input").get_attribute("type")=="checkbox":
                choose_num=random.randint(2,len(question_answers))
                choose_answers=[]
                choose_answers_pos=[]
                choose_answer_title=""
                targets=random.sample(question_answers,choose_num)
                for target in targets:
                    choose_answers.append(target)
                    choose_answers_pos.append(question_answers.index(target))
                for answer in choose_answers:
                    text=""
                    answer.find_element_by_tag_name("a").click()
                    if len(answer.find_elements_by_tag_name("input"))==2:
                        text_input=answer.find_elements_by_tag_name("input")[1]
                        text_input.click()
                        text_input.clear()
                        text=gen_str(random.randint(5,10))
                        text_input.send_keys(text)
                        choose_answer_title=choose_answer_title
                    choose_answer_title=choose_answer_title+answer.find_element_by_tag_name("label").text+text+"\n"
                    time.sleep(random.randint(1,3))
            elif question_answers[0].find_element_by_xpath("./input").get_attribute("type")=="text":
                target=question_answers[0]
                target.click()
                target.clear()
                text=gen_str(random.randint(10,20))
                target.send_keys(text)
                choose_answer_title=text+"\n"
            else:
                raise RuntimeError("无法获取正确的元素，请重试！")
            logger_.info("问题："+question_title+"\n选择："+choose_answer_title+"\n")
    do_queue(driver_=driver)
    time.sleep(random.randint(1,5))
    driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[4]/table/tbody/tr/td/input").click()
    try:
        target=driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]")
    except NoSuchElementException:
        logger_.info("未找到验证元素，看起来没有触发验证")
        logger_.info("已提交记录")
        driver.quit()
        return True
    else:
        logger_.warning("找到验证元素，似乎已经触发验证，已记录失败次数")
        if target.get_attribute("id")=="SM_BTN_1":
            def bypass_captcha(driver_,element_):
                pass
            bypass_captcha(driver_=driver,element_=target)
        driver.quit()
        return False
class job_thread(threading.Thread):
    def __init__(self,id_:int,times:int,url:str):
        self.id=id_
        self.times=times
        self.url=url
        self.thread_logger=logging.Logger("thread_logger")
        thread_log_handler=logging.FileHandler(filename="log/"+str(self.id)+".log",mode="w",encoding="utf-8")
        self.thread_logger.addHandler(thread_log_handler)
        threading.Thread.__init__(self)
    def run(self):
        self.failed_num=0
        self.thread_logger.info("线程 "+str(self.id)+" 开始执行")
        max_conn=3
        for each_time in range(self.times):
            def finish_survey(url_:str,each_time_:int,logger_2=self.thread_logger):
                if do_survey(url_2=url_,logger_=logger_2)==False:
                    self.failed_num=self.failed_num+1
                    logger_2.warning("线程 %s 在第 %d 次执行触发验证，提交失败" %(self.id,each_time_))
                else:
                    logger_2.info("线程 %d 在第 %d 次执行成功提交数据" %(self.id,each_time_))
            if self.times>0 and self.times<=max_conn:
                for each_time in range(self.times):
                    finish_survey(url_=self.url,each_time_=each_time)
            else:
                self.thread_logger.info("执行次数较多，将分成每 %d 次一组，每组间隔一定时间完成以避免验证" %max_conn)
                times_,more_times_=divmod(self.times,max_conn)
                if more_times_!=0:
                    for time_ in range(more_times_):
                        finish_survey(url_=self.url,each_time_=time_)
                    self.thread_logger.info("线程 %s 第 %d 次执行完成" %(self.id,time_))
                    time.sleep(random.randint(3,5))
                for time_ in range(times_):
                    for each_conn in range(max_conn):
                        finish_survey(url_=self.url,each_time_=each_conn)
                    self.thread_logger.info("线程 %s 第 %d 次执行完成" %(self.id,each_conn))
                    time.sleep(random.randint(3,5))
            time.sleep(random.randint(5,7))

        logger.info("线程 %d 结束运行" %self.id)
threads=[]
thread_num=int(cpu_count()/2)
full_times,more_time=divmod(times,thread_num)
all_faileds=0
for cpu in range(thread_num):
    working_thread=job_thread(cpu,full_times,url)
    threads.append(working_thread)
    working_thread.start()
more_thread=job_thread(thread_num+1,more_time,url)
threads.append(more_thread)
more_thread.start()
for thread in threads:
    thread.join()
    all_faileds=all_faileds+thread.failed_num
m,s=divmod(int(time.time()-start_time),60)
h,m=divmod(m,60)
logger.info("执行完成，选择内容可查看日志文件输出记录，用时 %02d:%02d:%02d 其中 %d 份问卷由于网站防护机制未能提交。" %(h, m, s, all_faileds))