## host API


* 添加主机(POST)
```
{
	"name": "host4",
	"desc": "",
	"ip":"172.16.1.4",
	"port":22,
	"user":"root",
	"create_time":"2019-02-25 10:10:11",
	"create_user":"user2",
	"groups": ["group1", "group2"]
}
```
* 查看主机(GET)
```
{
    "count": 6,
    "next": "http://127.0.0.1:8080/api/asb/host/?page=2&token=901da076d9d17ced214dd99747168ac4",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "host1",
            "desc": null,
            "ip": "172.16.1.1",
            "port": 22,
            "user": "root",
            "create_time": "2019-02-18T03:46:09",
            "create_user": "user2",
            "group": [
                {
                    "id": 1,
                    "name": "webs",
                    "desc": "web servers",
                    "create_time": "2019-02-18T03:15:18",
                    "create_user": "user2"
                }
            ]
        },
        {
            "id": 2,
            "name": "host2",
            "desc": null,
            "ip": "172.16.1.2",
            "port": 22,
            "user": "root",
            "create_time": "2019-02-18T03:46:09",
            "create_user": "user2",
            "group": []
        }
    ]
}
```

## Group API
* 添加组(POST)
```angular2html
{
    name: "group1",
    desc: "This is a describe of group."
}
```
* 查看组(GET)
```angular2html
{
    "count": 3,
    "next": "http://127.0.0.1:8080/api/asb/group/?page=2&token=851f01c7bb521f13c23828d59a5c5c53",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "webs",
            "desc": "前端服务器组",
            "create_time": "2019-02-28T15:10:13.825267",
            "create_user": "user2"
        },
        {
            "id": 2,
            "name": "dbs",
            "desc": "database servers",
            "create_time": "2019-02-18T03:15:23",
            "create_user": "user2"
        }
    ]
}
```

* copy管理公钥至被控端
```angular2html
{
    "ip": "172.16.1.28", 
    "port": 22, 
    "user":"root", 
    "password":"123456"
}
```

* 远程命令管理(POST)
```angular2html
{
	"mode": "host",  # host/group
	"targets": "host28, host215",
	"module": "shell",
	"args": "hostname"
}
```