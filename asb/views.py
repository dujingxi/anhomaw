# -*- coding: utf-8 -*-

import os
from operator import itemgetter
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Host, Group
from .serializers import HostSerializer, GroupSerializer
from .lib.copyKey import CopyKey
from .lib.ansible_py_api import AnsibleHost, AnsibleTask
from .lib.conf import ANSIBLE_BASE_DIR, ANSIB_PLAYBOOK
from rest_framework import status
from datetime import datetime
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser


class HostBatchView(APIView):
    """
    Add classes of hosts in batches
    """
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            host_file = request.FILES["file"]
        except:
            return Response({"code": 4003, "msg": "File not found."})
        # print ("*"*20,host_file.name, type(request.data['file']))
        if not host_file.name.endswith(".csv"):
            ret = {
                "code": 4002,
                "msg": "文件格式错误"
            }
            return Response(ret)

        # failed items
        error_results = []
        while True:
            host = host_file.readline()
            if not host:
                break
            else:
                host = host.decode("utf-8").strip()
                # check per item
                try:
                    name, ip, port, user, passwd, desc, groups = host.split(",")
                except:
                    error_results.append("Failed: {} -> Parsing failure".format(host))
                    continue

                # test copykey
                copykey = CopyKey(ip=ip, port=port, user=user, password=passwd)
                result = copykey.copy_it()
                if not result["success"]:
                    error_results.append("Failed: {} -> Copykey failure.".format(host))
                    continue

                # Check if the host already exists
                hobjs = Host.objects.filter(name=name, ip=ip)
                if hobjs:
                    error_results.append("Failed: {} -> Host already exists.".format(host))
                    continue

                # Check if the group exists
                for group in groups.split():
                    gobjs = Group.objects.filter(name=group)
                    if not gobjs:
                        error_results.append("Failed: {} -> Group {} don't exists.".format(host, group))

                # exec add
                try:
                    host_obj = Host(name=name, ip=ip, port=port, user=user, desc=desc, create_user=request.user)
                    host_obj.save()
                except:
                    error_results.append("Failed: {} -> Add failed.".format(host))
                    continue
                else:
                    for group in groups.split():
                        g_obj = Group.objects.get(name=group)
                        host_obj.group.add(g_obj)

        ret = {"code": 2000, "error": error_results}
        return Response(ret)


class HostViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    def create(self, request, *args, **kwargs):
        # 重定create，处理提交处理中的 groups 多对多字段
        post_data = request.data
        groups = post_data.get("groups", '')
        if groups: groups = groups.split(",")
        host_name = post_data.get("name")
        post_data["create_time"] = datetime.now()


        serializer = self.get_serializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # print ("*"*20, groups)
        if groups:
            # 获取组对象列表
            # try:
            groups_obj = []
            for group in groups:
                g_obj = Group.objects.all().get(name=group)
                groups_obj.append(g_obj)
            # except:
            #     raise NotFound("hello world")
                # return Response("", status=status.HTTP_403_FORBIDDEN)
            # 添加组
            host_obj = Host.objects.all().get(name=host_name)
            host_obj.group.add(*groups_obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # 重写修改方法，需客外处理上传数据中的 groups 字段
        put_data = request.data
        groups = put_data.pop("groups", '')
        if groups: groups = groups.split(",")

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=put_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # update by dujingxi
        if groups:
            hname = put_data.get("name")
            hobj = Host.objects.all().get(name=hname)
            db_groups = [ i["name"] for i in hobj.group.values() ]
            if set(groups) != set(db_groups):
                for need_join in (set(groups) - set(db_groups)):
                    need_join_g_obj = Group.objects.all().get(name=need_join)
                    hobj.group.add(need_join_g_obj)
                for need_detach in (set(db_groups) - set(groups)):
                    need_detach_g_obj = Group.objects.all().get(name=need_detach)
                    hobj.group.remove(need_detach_g_obj)


        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GroupVewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        获取单条组信息时，返回所包含的主机列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        # print ("*"*10, instance.host_set.values('name', 'ip'))
        serializer = self.get_serializer(instance)
        results = serializer.data
        results["hosts"] = list(instance.host_set.values('name', 'ip'))
        return Response(results)


class CopyPrivateKey(APIView):
    """
    传输公钥，将服务器生成的公钥传输到各被控端
    """
    def post(self, request, *args, **kwargs):
        ip = request.data.get("ip")
        port = request.data.get("port")
        user = request.data.get("user")
        password = request.data.get("password")
        host = dict(
            ip=ip,
            port=port,
            user=user,
            password=password
        )
        copykey = CopyKey(**host)
        result = copykey.copy_it()
        if result["success"]:
            ret = {"code": 2000, "results": result}
        else:
            ret = {"code": 5001, "results": result}
        return Response(ret)


class CheckHost(APIView):
    """
    check host obj exists
    """
    def post(self, request, *args, **kwargs):
        hosts = request.data["hosts"].strip()
        hosts = hosts.strip(",")
        for host in hosts.split(','):
            host = host.strip()
            try:
                Host.objects.get(name=host)
            except:
                return Response({"code": 40005, "host": host})
            else:
                continue
        return Response({"code": 2000, "host": hosts.split(",")})


class AdHocView(APIView):
    """
    在指定的被控端主机上执行远程指令
    指定ansible中需执行的模块及各参数
    """
    def post(self, request, *args, **kwargs):
        mode = request.data.get("mode")
        targets = request.data.get("targets")
        module = request.data.get("module")
        args = request.data.get("args")
        hosts = []
        str_lists = targets.split(",")
        if mode == "group":
            for group in str_lists:
                group = group.strip()
                if not group: continue
                try:
                    group_obj = Group.objects.all().get(name=group)
                except:
                    ret = {
                        "code": 4001,
                        "msg": "未知的组 {}".format(group)
                    }
                    return Response(ret)

                for host in group_obj.host_set.values():
                    ansible_host = AnsibleHost(host["name"], host["ip"], user=host["user"], port=host["port"])
                    hosts.append(ansible_host)
        else:
            for host in str_lists:
                host = host.strip()
                if not host: continue
                try:
                    host_obj = Host.objects.all().get(name=host)
                except:
                    ret = {
                        "code": 4002,
                        "msg": "未知的主机 {}".format(host)
                    }
                    return Response(ret)

                ansible_host = AnsibleHost(host_obj.name, host_obj.ip, user=host_obj.user, port=host_obj.port)
                hosts.append(ansible_host)
        task = AnsibleTask(hosts)
        try:
            result = task.exec_hoc(exec_module=module, exec_args=args)
        except:
            ret = {
                "code": 5000,
                "msg": "执行指令失败，请检查模块名称和参数是否书写正确，请参考帮助文档."
            }
        else:
            ret = {
                "code": 2000,
                "count": {
                    "success": len(result["success"]),
                    "failed": len(result["failed"]),
                    "unreachable": len(result["unreachable"])
                },
                "result": result
            }
        finally:
            return Response(ret)


class PlayBookView(APIView):
    def post(self, request):
        filename = request.data.get('filename')
        file_path = os.join(ANSIBLE_BASE_DIR, filename)
        from subprocess import Popen as popen, PIPE

        p = popen("ANSIB_PLAYBOOK {}".format(file_path), shell=True, stdout=PIPE)
        res = p.stdout.read()
        return Response({"results": res})


class ListFdView(APIView):
    def post(self, request, *args, **kwargs):
        post_fd = request.data.get("fdpath", None)
        full_path = os.path.join(ANSIBLE_BASE_DIR, post_fd)
        if not os.path.isdir(full_path):
            with open(full_path) as fd:
                content = fd.read()
            return Response({"code": 2000, "type": "file", "content": content})
        else:
            all_member = []
            for f in os.listdir(full_path):
                if not os.path.isdir(os.path.join(full_path, f)):
                    all_member.append({"type": "file", "name": os.path.join(post_fd, f)})
                else:
                    all_member.append({"type": "dir", "name": os.path.join(post_fd, f)})
            all_member = sorted(all_member, key=itemgetter("type"))
            return Response({"code": 2000, "type": "dir", "content": all_member})








