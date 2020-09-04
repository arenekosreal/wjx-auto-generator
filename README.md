# wjx-auto-generator
自动生成问卷星的答案，无过验证功能，使用selenium在python中构建
## 用法
下载存储库中的`wjx.py`文件（[国内镜像1](https://hub.fastgit.org/zhanghua000/wjx-auto-generator/raw/master/wjx.py) [国内镜像2](https://github.com.cnpmjs.org/zhanghua000/wjx-auto-generator/raw/master/wjx.py)），使用Python 3.0及以上的版本执行，第一次需要初始化运行环境，启动后根据终端提示输入数据后等待执行完毕返回提示符，之后就可以到后台看数据是否增加。
## 注意
- 此脚本不包含过验证功能，如果连接次数过多，可能触发网站的防机器人验证，请等待一段时间后重试。在构建脚本是已加入两次连接中随机等待一段时间（1-3秒），一般不会触发，但仍须注意
- chrome driver似乎有一个特性未解决，导致执行脚本时有几率出现未知错误（unknown error），但概率较小，可以忽略，如果发生，请重新执行脚本
- 脚本选项为随机选择，如果题目间有逻辑联系，可能导致错误答案。目前可以处理单选和多选，~~需要输入的将无法解决~~目前可以处理输入内容，将随机生成一个字符串填入输入框，具体参阅脚本中的`gen_str()`部分。
