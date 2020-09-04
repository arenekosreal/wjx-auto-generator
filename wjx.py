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
os.chdir(os.path.split(os.path.realpath(__file__))[0])
def gen_bootstrap():
    lines=[
        "@echo off\n",
        "%1 mshta vbscript:CreateObject(\"Shell.Application\").ShellExecute(\"cmd.exe\",\"/c %~s0 ::\",\"\",\"runas\",1)(window.close)&&exit\n",
        "cd /d \"%~dp0\"\n",
        "(echo selenium==3.141.0\necho requests==2.23.0) > requirements.txt\n",
        "\""+sys.executable+"\" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\n",
        "reg ADD HKLM\SOFTWARE\Policies\Google\Chrome /v RendererCodeIntegrityEnabled /t REG_DWORD /d 0 /f\n",
        "del /F /S /Q requirements.txt\n"]
    with open("bootstrap.bat","w",encoding="utf-8") as gen:
        gen.writelines(lines)
try:
    import requests
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
except:
    print("正在初始化依赖环境。。。")
    gen_bootstrap()
    re=subprocess.run("bootstrap.bat")
    if re.returncode==0:
        os.remove("bootstrap.bat")
        print("初始化依赖环境完成")
    else:
        raise RuntimeError("初始化依赖环境失败，请手动执行 bootstrap.bat 完成初始化。弹出的UAC认证提示请予以通过")
else:
    print("依赖环境正常")
if os.path.exists("Chrome")==False:
    os.mkdir("Chrome")
if os.path.exists("Chrome/App/chrome.exe")==False:
    print("正在初始化运行环境。。。")
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
            print("文件MD5不符，终止解压缩")
            return 1
    def down_env(addr_head:str):
        if os.path.exists("Chrome/env.zip")==False:
            envaddr=addr_head+"/zhanghua000/wjx-auto-generator-env/releases/download/1.0/env.zip"
            with open("Chrome/env.zip","wb") as file_downloader:
                file_downloader.write(requests.get(envaddr).content)
        if unpack("dcf2981ec68a72e206f949066ee8eedd")==1:
            print("下载失败，请手动下载 "+envaddr+" 并以 env.zip 的文件名保存到Chrome目录下，之后重启程序")
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
if os.path.exists("log"):
    shutil.rmtree("log")
os.mkdir("log")
times=int(input("请输入生成的问卷的份数："))
print("问卷星地址举例：https://www.wjx.cn/jq/89714348.aspx")
url=str(input("请输入问卷星创建的问卷地址："))
main_log=open("log/main.log","w",encoding="utf-8")
url="https://www.wjx.cn/jq/"+url.split("/")[-1]
print("转换地址完成，为："+url,file=main_log)
start_time=time.time()
def do_survey(url,log):
    browser=webdriver.ChromeOptions()
    browser.binary_location="./Chrome/App/chrome.exe"
    browser.add_argument("headless")
    driver = webdriver.Chrome("./Chrome/app/chromedriver.exe",options=browser)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(expected_conditions.element_to_be_clickable((By.ID,'submit_button')))
    def do_queue(driver_=driver):
        root_element=driver_.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/fieldset")
        question_elements=root_element.find_elements_by_class_name("div_question")
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
                    choose_answer_title=choose_answer_title+answer.find_element_by_tag_name("label").text+"\n"
                    answer.find_element_by_tag_name("a").click()
                    time.sleep(random.randint(1,3))
            else:
                raise RuntimeError("无法获取正确的元素，请重试！")
            print("问题："+question_title+"\n选择："+choose_answer_title+"\n",file=log)
    do_queue(driver_=driver)
    driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[4]/table/tbody/tr/td/input").click()
    print("已提交记录",file=main_log)
    driver.quit()
class job_thread(threading.Thread):
    def __init__(self,id_:int,times:int,url:str):
        self.id=id_
        self.times=times
        self.url=url
        self.log=open("log/"+str(self.id)+".log","w",encoding="utf-8")
        threading.Thread.__init__(self)
    def run(self):
        print("线程 "+str(self.id)+" 开始执行",file=self.log)
        for each_time in range(self.times):
            do_survey(self.url,self.log)
        self.log.close()
threads=[]
thread_num=int(cpu_count()/2)
full_times,more_time=divmod(times,thread_num)
for cpu in range(thread_num):
    working_thread=job_thread(cpu,full_times,url)
    threads.append(working_thread)
    working_thread.start()
more_thread=job_thread(thread_num+1,more_time,url)
threads.append(more_thread)
more_thread.start()
for thread in threads:
    thread.join()
m,s=divmod(int(time.time()-start_time),60)
h,m=divmod(m,60)
print("执行完成，选择内容可查看日志文件输出记录,用时 %02d:%02d:%02d \n部分问卷可能由于网站防护机制未能提交，请手动登陆网页后台查看。" %(h, m, s),file=main_log)
main_log.close()