from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=32, verbose_name="组名", unique=True)
    desc = models.TextField(blank=True, null=True, max_length=200, verbose_name="组描述")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=32, verbose_name="创建者")



class Host(models.Model):
    name = models.CharField(max_length=32, verbose_name="主机名", unique=True)
    desc = models.TextField(blank=True, null=True, max_length=200, verbose_name="主机描述")
    ip = models.CharField(max_length=32, verbose_name="IP地址")
    port = models.IntegerField(verbose_name="远程端口")
    user = models.CharField(max_length=32, verbose_name="账号")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=32, verbose_name="创建者")

    group = models.ManyToManyField(Group)

