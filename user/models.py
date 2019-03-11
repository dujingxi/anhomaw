from django.db import models
import datetime

class User(models.Model):
    role_choices = (
        (1, 'common'),
        (2, 'admin'),
        (3, 'superadmin')
    )
    name = models.CharField(max_length=32, unique=True, verbose_name="用户名")
    passwd = models.CharField(max_length=64, verbose_name="密码")
    alias = models.CharField(max_length=200, verbose_name="用户显示名")
    role = models.IntegerField(choices=role_choices)
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱地址")
    # birth = models.DateTimeField(verbose_name="出生日期")
    created = models.DateTimeField(auto_now=True)

    user_group = models.ForeignKey("Group", related_name="users", on_delete=models.CASCADE)


class UserToken(models.Model):
    name = models.OneToOneField("User", on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    remote_addr = models.CharField(max_length=32)
    token_time = models.DateTimeField(auto_now=True)


class Group(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name="用户组名")
    alias = models.CharField(max_length=200, verbose_name="用户组显示名")
    desc = models.TextField(verbose_name="组介绍", max_length=2048, null=True, blank=True, default="")
