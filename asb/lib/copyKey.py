# coding: utf-8
from .conf import ID_PUB_PATH
from .ansible_py_api import AnsibleTask, AnsibleHost
import os


class CopyKey(object):
    def __init__(self, **dst_kwargs):
        self.dst_host = dst_kwargs.get("host")
        self.dst_ip = dst_kwargs.get("ip")
        self.dst_port = dst_kwargs.get("port", 22)
        self.dst_user = dst_kwargs.get("user", "root")
        self.dst_password = dst_kwargs.get("password", None)

    @property
    def _dst_key_file(self):
        if self.dst_user == "root":
            return "/root/.ssh/authorized_keys"
        else:
            return "/home/%s/.ssh/authorized_keys" % self.dst_user

    def copy_it(self):
        ansible_host = [
            AnsibleHost(self.dst_host, self.dst_ip, user=self.dst_user, port=self.dst_port, password=self.dst_password)
        ]
        task = AnsibleTask(ansible_host)
        with open(ID_PUB_PATH) as key_file:
            pub_key_str = key_file.read()

        task.exec_hoc("file", "path={} state=touch".format(self._dst_key_file))

        res = task.exec_hoc("lineinfile", 'path={dst_path} line="{line}"'.format(line=pub_key_str, dst_path=self._dst_key_file))

        return res






if __name__ == "__main__":
    h = {
        "host": "host215",
        "ip": "172.16.1.215",
        "port": 22,
        "user": "root",
        "password": "123456"
    }

    copykey = CopyKey(**h)
    ret = copykey.copy_it()
    print ("****", ret)


