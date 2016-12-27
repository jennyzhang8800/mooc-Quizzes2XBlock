# mooc-Quizzes2XBlock
操作系统课程在OpenEdx上的XBlock插件，用于学生回答问题

## 部署方法(以下为在cherry.cs.tsinghua.edu.cn上的安装)

**1.clone到本地**
```
$ git clone https://github.com/Heaven1881/mooc-Quizzes2XBlock.git
$ sudo chown -R edxapp:edxapp mooc-Quizzes2XBlock/
```

**2.更改conf.py**

位于 mooc-Quizzes2XBlock/quizzes2/conf.py
把下面的root_token改为gitlab的private token; hostname改为gitlab的IP（不能写外部url，要写成IP）;
```
# teacher/answer gitlab 配置
    teacherGitlab = {
        'root_token': 'XXXXXXXXXX',
        'hostname': '192.168.1.136',
        'port': 80,
        'repo_id': 287,
        'file_operation_url': '/api/v3/projects/%(repo_id)d/repository/files?private_token=%(root_token)s&&file_path=%(filepath)s&&ref=%(ref)s',
        'ref': 'master',
    }
```

**3.安装XBlock**

```
$ sudo -u edxapp /edx/bin/pip.edxapp install yourXBlock/
```

**4.重启Edx服务器：**
```
$ sudo /edx/bin/supervisorctl restart edxapp:
```

**5.在Studio中把在线代码编辑器block添加到课程的高级设置中。**

登录到Studio,打开你的课程
settings->Advanced Setting
在"advanced_modules"的值后添加"quizzes2"
可以在Studio中看到"练习"并使用该组件

## FAQ
- 如何编辑已经发布的题目内容
 - 在编辑题目block里面载入题目进行编辑，
 - 编辑好的题目，需要在Studio对应的XBlock里面选择编辑，重新保存配置信息，最后选择右侧的发布按钮
 - 单击发布按钮以后就可以在LMS页面看到更改了
 - 注意，如果需要改变xblock的题号，那么需要删除原有的XBlock，然后重新创建新的XBlock，然后再指定题号
