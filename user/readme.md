## user API
* 登录(POST)
```angular2html
{
"username": "user2", 
"password": "123456"
}
```
* 添加账号(POST)
```
{
"name": "user2", 
"passwd": "123456", 
"alias": "测试用户2", 
"role": "common",  # common/admin/superadmin
"email": "user2@test.com",  # null 
"user_group": "group1", 
"birth":"2010-01-01 11:02:00"
}
```
* 查看账号信息(GET)
```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 19,
            "role_name": "common",
            "group_name": "group1",
            "name": "user1",
            "alias": "测试1",
            "email": "user1@test.com",
            "birth": "2019-02-25T06:24:18",
            "created": "2019-02-25T06:24:29"
        }
    ]
}
```

## Group API
* 添加组(POST)
```angular2html
{
name: "group1",
alias: "测试组1",
desc: "This is a describe of group."
}
```
* 查看组(GET)
```angular2html
{
    "count": 11,
    "next": "http://127.0.0.1:8080/api/user/groups/?page=2&token=f7d5abbafb33dd9f49080d8b8f0b2999",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "group1",
            "alias": "group1",
            "desc": ""
        },
        {
            "id": 2,
            "name": "group2",
            "alias": "group2",
            "desc": ""
        }
    ]
}
```