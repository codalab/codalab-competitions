-2017.12.23 开始国际化
1、进入codalab django虚拟化空间：docker exec -it django bash
2、在对应html里标记动态翻译部分{%trans''% }
3、在虚拟化空间里创建中文国际化目录（我已创建好，即locale）django-admin.py makemessages -l zh_CN
4、修改locale里的django.po文件翻译成中文
5、django-admin.py compilemessages编译生成mo文件
6、生效（如果不生效可去codalab/settings/base.py里保存一下语言设置）
7、后期更新django.po文件可用django-admin.py makemessages -a命令，注意每次改动po文件最后都要执行第5步