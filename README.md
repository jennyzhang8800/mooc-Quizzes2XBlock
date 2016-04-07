# mooc-Quizzes2XBlock
操作系统课程在OpenEdx上的XBlock插件，用于学生回答问题

## 部署方法
安装XBlock:
```
$ sudo -u edxapp /edx/bin/pip.edxapp install yourXBlock/
```

重启Edx服务器：
```
$ sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
```

## FAQ
- 如何编辑已经发布的题目内容
 - 在编辑题目block里面载入题目进行编辑，
 - 编辑好的题目，需要在Studio对应的XBlock里面选择编辑，重新保存配置信息，最后选择右侧的发布按钮
 - 单击发布按钮以后就可以在LMS页面看到更改了
 - 注意，如果需要改变xblock的题号，那么需要删除原有的XBlock，然后重新创建新的XBlock，然后再指定题号
