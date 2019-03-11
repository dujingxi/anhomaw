# coding: utf-8
"""
current version of ansible: 2.7.1
如果 ansible 的 python API 调用方式改变了，则需要重写此文件
"""

import os
import tempfile
import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C
from collections import Iterable


class AnsibleHost(object):
    def __init__(self, host, ip, port=22, user="root", connection=None, password=None):
        self.host = host
        self.ip = ip
        self.port = port
        self.user = user
        self.connection = connection
        self.password = password

    def __str__(self):
        line_strs = "{host} ansible_host={ip} ansible_port={port} ansible_user={user} ".format(host=self.host, ip=self.ip, port=self.port, user=self.user)
        if self.password:
            line_strs += " ansible_ssh_pass=%s " % self.password
        if self.connection:
            line_strs += " ansible_connection=%s" % self.connection
        return line_strs



class AnsibleResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def __init__(self, *args, **kwargs):
        super(AnsibleResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        执行成功的返回结果
        """
        host = result._host.get_name()
        self.host_ok[host] = result
        # print(json.dumps({host: result._result}, indent=4))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """
        执行失败的返回结果
        """
        host = result._host.get_name()
        self.host_failed[host] = result
        # print(json.dumps({host: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result):
        """
        不可达的返回结果
        """
        host = result._host.get_name()
        self.host_unreachable[host] = result
        # print(json.dumps({host: result._result}, indent=4))


class AnsibleTask:
    def __init__(self, hosts):
        self.hosts = hosts
        self._validate()
        self.hosts_file = None
        self._generate_hosts_file()

        Options = namedtuple('Options',
                             ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff', 'host_key_checking', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        self.options = Options(connection='ssh', module_path=None, forks=5, become=None, become_method=None, become_user=None, check=False, diff=False, host_key_checking=False, listhosts=None, listtags=None, listtasks=None, syntax=None)

        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')
        self.inventory = InventoryManager(loader=self.loader, sources=[self.hosts_file])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)


    def _validate(self):
        """
        验证传入的hosts参数是否正确
        :return:
        """
        if not self.hosts:
            raise Exception("hosts 不能为空")
        if not isinstance(self.hosts, Iterable):
            raise Exception("hosts 必须为可迭代类型, 由AnsibleHost对象组成的列表或元组")

    def _generate_hosts_file(self):
        """
        创建临时文件做为 inventory
        :return:
        """
        self.hosts_file = tempfile.mktemp()
        with open(self.hosts_file, 'w+', encoding='utf-8') as fp:
            hosts = []
            for host in self.hosts:
                hosts.append(str(host))
            fp.write('\n'.join(hosts))


    def exec_hoc(self, exec_module="command", exec_args=None):
        """
        Ad-Hoc: ansible command line
        :param exec_module:
        :param exec_args:
        :return:
        """
        play_source = dict(
            name = "Ansible play",
            hosts = "all",
            gather_facts = "no",
            tasks = [
                dict(action=dict(module=exec_module, args=exec_args), register="shell_out"),
            ]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        results_callback = AnsibleResultCallback()
        tqm = None

        try:
            tqm = TaskQueueManager(
                inventory = self.inventory,
                variable_manager = self.variable_manager,
                loader = self.loader,
                options = self.options,
                passwords = self.passwords,
                stdout_callback = results_callback
            )
            tqm.run(play)

            result_raw = dict(
                success=dict(),
                failed = dict(),
                unreachable = dict()

            )
            for host, result in results_callback.host_ok.items():
                result_raw['success'][host] = dict(status="ok")
                if "cmd" in result._result.keys():
                    result_raw['success'][host].update({"cmd": result._result["cmd"]})
                if "stdout_lines" in result._result.keys():
                    result_raw['success'][host].update({"stdout": result._result["stdout_lines"]})
                if "msg" in result._result.keys():
                    result_raw['success'][host].update({"msg": result._result["msg"]})


            for host, result in results_callback.host_failed.items():
                result_raw['failed'][host] = dict(status="failed")
                if "cmd" in result._result.keys():
                    result_raw['failed'][host].update({"cmd": result._result["cmd"]})
                if "stderr_lines" in result._result.keys():
                    result_raw['failed'][host].update({"stderr": result._result["stderr_lines"]})
                if "msg" in result._result.keys():
                    result_raw['failed'][host].update({"msg": result._result["msg"]})

            for host, result in results_callback.host_unreachable.items():
                result_raw['unreachable'][host] = dict(
                    status="unreachable",
                    msg=result._result["msg"]
                )

            # return json.dumps(result_raw, indent=4)
            return result_raw


        except:
            raise
        finally:
            if tqm is not None:
                tqm.cleanup()

            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def exec_playbook(self, playbooks):
        """
        exec playbook
        :param playbooks:
        :return:
        """
        """
        results_callback = AnsibleTaskResultCallback()
        playbook = PlaybookExecutor(playbooks=playbooks, inventory=self.inventory,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader, options=self.options, passwords=self.passwords)
        setattr(getattr(playbook, '_tqm'), '_stdout_callback', results_callback)
        playbook.run()
        if results_callback.error_msg:
            raise Exception(results_callback.error_msg)
        return results_callback.result
        """

    def __del__(self):
        if self.hosts_file:
            os.remove(self.hosts_file)


if __name__ == "__main__":
    hosts = [AnsibleHost("host215", "172.16.1.215")]
    task = AnsibleTask(hosts)
    # res = task.exec_hoc("copy", "src=/data/gitlab/core/server/lr/lrc/dlr.py dest=/mnt/")
    res = task.exec_hoc("shell", "uptime")
    print (res)
