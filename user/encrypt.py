from hashlib import md5
from .conf import PASSWD_SALT
import time

def encrypt_str(username, passwd=None):
    """
    :param username: 加密用户名
    :param passwd:  为密码加密时传递此参数
    :return:  返回加密后的字串
    """
    ctime = time.time()
    m = md5(username.encode("utf-8"))
    if not passwd:
        m.update(str(ctime).encode("utf-8"))
    else:
        # m.update(passwd.encode("utf-8"))
        m.update("{passwd}{salt}".format(passwd=passwd, salt=PASSWD_SALT).encode("utf-8"))
    res = m.hexdigest()
    return res



# print (encrypt_str('u22221', passwd='123456', _type="pass"))