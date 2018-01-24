=================2017.12.23国际化相关=================
1、进入codalab django虚拟化空间：docker exec -it django bash
2、在对应html里标记动态翻译部分{%trans''% }
3、在虚拟化空间里创建中文国际化目录（我已创建好，即locale）django-admin.py makemessages -l zh_CN
4、修改locale里的django.po文件翻译成中文
5、django-admin.py compilemessages编译生成mo文件
6、生效（如果不生效可去codalab/settings/base.py里保存一下语言设置）
7、后期更新django.po文件可用django-admin.py makemessages -a命令，注意每次改动po文件最后都要执行第5步

=================2018.01.12 User Model模型图绘制&&界面改版=================
1、进入数据库docker exec -it posrgres bash
2、psql（首次要createdb）
3、进入root模式，之后操作和postgres一致
4、界面风格统一换成北航蓝。
5、今后110服务器为正式服务器，谨慎改动

=================2018.01.24 深度国际化之修改数据库================
1、原导航栏Learn the Details、Participate、Results写在Django数据库中，已在scriptes/initialize.py下完成修改。但目前数据库设计较多索引字段，在models.py competitions.py form.py中将这些get索引字段统一改成中文，虽中文可正常显示但实际效果并不完美无法切换至其它语言。

