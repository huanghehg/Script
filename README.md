### [header_change](https://huanghehg.github.io/2019/09/28/import/)

主要功能：修改xcode 项目头文件引用的脚本

执行环境：python2.7

包管理工具：pip

依赖库：io、os、re、string、subprocess、shutil、GitPython

使用方法：
```
举例需要改的pod库地址
git@git.xxx.net:group1/appdemo.git
git@git.xxx.net:group1/appdemo1.git
git@git.xxx.net:group2/appdemo2.git
git@git.xxx.net:group3/appdemo3.git
```

`CHECK_PODS`：传入需要修改的`git`库名，如：`CHECK_PODS = ['appdemo', 'appdemo1', 'appdemo2']`

`GIT_DEFAULT_GROUP`：默认`group`名，如：`GIT_DEFAULT_GROUP = 'group1'`

`GIT_REPO_GROUPS`：如果有多个`group`使用，如：`GIT_REPO_GROUPS` = `{'appdemo2':'group2', 'appdemo3': 'group3'}`

配置好上面三个变量就可以使用

执行逻辑：

1. `clone` 仓库到 `ios_check`文件夹，默认`develop`分支
2. 对每个仓库执行以下步骤
3. 从`develop`分支创建`feature/change_header`分支
4. 找到`Podfile`文件所在路径执行`pod update`
5. 遍历当前库所有文件，解析文件，找出所有`import`引号引用文件
6. 找出不属于当前库文件
7. 去`Pods`路径下匹配库名，建立文件名与库名`map`
8. 遍历文件将引号引用替换为`<库名/文件>`
9. 替换完成，会将`feature/change_header`分支提交推送

ps：写的时候时间比较紧迫，没有在意python版本^_^，方法也比较暴力，因为是一次性使用脚本，没怎么考虑执行效率，有需要的可以自行修改

### [ipa_server](https://huanghehg.github.io/2019/10/18/site-for-ipa-download/)

主要功能：提供持续化集成中打包平台的服务端接口

执行环境：python3.x

包管理工具：pip

依赖库：json, os, zipfile, plistlib, sys, re, pymysql, uuid, shutil, time, flask, flask_cors

使用方法：

1. 配置ssl证书
2. 启动Apache、https
3. 接收jenkins 打包的ipa，生成plist文件，将信息写入数据库

ps：代码没有分模块，没有拆分，没有加异常判断

### internet_worm
微信公众号爬虫脚本
```
headers = {
    'User-Agent': "xxxxxx",
    'Cookie': "xxxxx"
}
params = {
	'action':"getmsg",
	'__biz':"xxxx",
	"f":"json",
	"is_ok":"1",
	"scene":"124",
	"uin":"xxxx",
	"key":"xxxxx",
	"pass_ticket":"xxxx",
	"appmsg_token":"xxxxx",
	"x5":"0",
	"offset":"0",
	"count":"10"
}
```
使用`charles`抓取公众号文章列表，将上面`xxxx`修改为对应的配置

