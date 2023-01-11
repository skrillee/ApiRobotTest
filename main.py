#! -*- coding: utf-8 -*-
__author__ = 'Yan.zhe 2023.01.09'

import requests
import json
import functools
from apscheduler.schedulers.blocking import BlockingScheduler


boot_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fffe3e0f-3b61-4fe6-8a1a-6183129158cc"
pic_url = "https://frame-versions.oss-cn-shenzhen.aliyuncs.com/test_pics/test_factory_4.jpg"
boot_data = {"msg_type": "text", "content": {"text": ""}}
boot_send_data = []


def frame_login(**kwargs):
    base_api = kwargs['base_api']
    user_name = kwargs['user_name']
    password = kwargs['password']
    project_oauth_api = "https://" + base_api + "/uaa/oauth/token"
    data_login = {
        "username": user_name,
        "password": password,
        "grant_type": "password",
        "client_id": "app",
    }
    headers_login = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "",
    }
    try:
        res = requests.post(url=project_oauth_api, params=data_login, headers=headers_login)
        result = res.json()

        token_type = result["token_type"].strip()
        access_token = result["access_token"].strip()
        token = token_type.title() + " " + access_token
    except Exception as e:
        token = None
        boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下登录失败"
        requests.post(url=boot_url, data=json.dumps(boot_data))

    return token


def frame_binding(**kwargs):
    base_api = kwargs['base_api']
    token = kwargs['token']
    user_id = kwargs['user_id']
    frame_id = kwargs['frame_id']
    project_oauth_api = "https://" + base_api + "/frame/users/{}/frames".format(user_id)
    try:
        # binding
        if token:
            boot_send_data.append("登录【pass】")
            # boot_data["content"]["text"] = "【pass】" + base_api + "域名下-app登录成功"
            # requests.post(url=boot_url, data=json.dumps(boot_data))
            frame_url = project_oauth_api
            frame_data = {"frameId": frame_id, "nickname": '庞' + '松易'}
            frame_headers = {"Content-Type": "application/json; charset=utf-8",
                             "Authorization": token}
            res_bind = requests.post(url=frame_url, data=json.dumps(frame_data), headers=frame_headers)
            status = res_bind.json()['status']
            if status == "OK":
                boot_send_data.append("绑定相框【pass】")
                # boot_data["content"]["text"] = "【pass】" + base_api + "域名下-绑定相框成功"
                # requests.post(url=boot_url, data=json.dumps(boot_data))
                return token
            else:
                boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下绑定相框失败"
                requests.post(url=boot_url, data=json.dumps(boot_data))
        else:
            boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下登录失败"
            requests.post(url=boot_url, data=json.dumps(boot_data))
    except Exception as e:
        boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下绑定相框失败"
        requests.post(url=boot_url, data=json.dumps(boot_data))


def send_pic(**kwargs):
    base_api = kwargs['base_api']
    user_id = kwargs['user_id']
    frame_id = kwargs['frame_id']
    token = kwargs['token']
    try:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": token}
        data = {
            'files': [{"url": pic_url, "size": "100", "mimeType": "jpg", "md5": "1231131346"}],
            'userId': user_id,
            'frameIds': [frame_id],
            'loginToken': token
        }
        project_oauth_api = "https://" + base_api + "/frame/medias/push"
        res_result = requests.post(url=project_oauth_api, data=json.dumps(data), headers=headers)
        if res_result.status_code == 200:
            boot_send_data.append("发图【pass】")
            # boot_data["content"]["text"] = "【pass】" + base_api + "域名下-发图成功"
            # requests.post(url=boot_url, data=json.dumps(boot_data))
        else:
            boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下发图失败"
            requests.post(url=boot_url, data=json.dumps(boot_data))
    except Exception as e:
        boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下发图失败"
        requests.post(url=boot_url, data=json.dumps(boot_data))


def frame_delete(**kwargs):
    base_api = kwargs['base_api']
    token = kwargs['token']
    user_id = kwargs['user_id']
    frame_id = kwargs['frame_id']
    try:
        project_oauth_api = "https://" + base_api + "/frame/frames/{}/users/{}".format(frame_id, user_id)
        frame_data = {}
        frame_headers = {"Content-Type": "application/json; charset=utf-8",
                         "Authorization": token}
        res_bind = requests.delete(url=project_oauth_api, data=json.dumps(frame_data), headers=frame_headers)
        if res_bind.status_code == 205:
            boot_send_data.append("解绑【pass】")
            # boot_data["content"]["text"] = "【pass】" + base_api + "域名下-解除绑定相框成功"
            # requests.post(url=boot_url, data=json.dumps(boot_data))
            return token
        else:
            boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下解除绑定相框失败"
            requests.post(url=boot_url, data=json.dumps(boot_data))
    except Exception as e:
        boot_data["content"]["text"] = "【fail！！！】" + base_api + "域名下解除绑定相框失败"
        requests.post(url=boot_url, data=json.dumps(boot_data))


def outer(origin):
    @functools.wraps(origin)
    def inner(**kwargs):
        """
        login and binding
        :param kwargs: dict
        :return: token
        """
        base_api = kwargs['api_url']
        frame_id = kwargs['frame_id']
        user_id = kwargs['user_id']
        user_name = kwargs['user_name']
        password = kwargs['password']
        # login
        token = frame_login(base_api=base_api, user_name=user_name, password=password)
        # binding
        frame_binding(token=token, base_api=base_api, user_id=user_id, frame_id=frame_id)
        # send_pic and others
        res = origin(token=token, user_id=user_id, frame_id=frame_id, base_api=base_api)
        # delete
        frame_delete(token=token, user_id=user_id, frame_id=frame_id, base_api=base_api)
        # robot send message
        result_str = "*域名：" + base_api + "*结果："
        for rec in boot_send_data:
            result_str += rec
        boot_data["content"]["text"] = result_str
        requests.post(url=boot_url, data=json.dumps(boot_data))
        boot_send_data.clear()
        return res
    return inner


@outer
def biuframe_api(**kwargs):
    token = kwargs["token"]
    user_id = kwargs['user_id']
    frame_id = kwargs['frame_id']
    base_api = kwargs['base_api']
    send_pic(token=token, user_id=user_id, frame_id=frame_id, base_api=base_api)


def start_biuframe_api_test():
    biuframe_api(api_url="biu.aiframe.net", frame_id="5505664517", user_name="NbsDZncnb@163.com",
                 password="ybc19940829", user_id=93213319774)
    biuframe_api(api_url="meta.aiframe.net", frame_id="6624303444", user_name="yanzhe001@qq.com",
                 password="ybc19940829", user_id=93213281086)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(start_biuframe_api_test, 'interval', seconds=1800, id='task')
    scheduler.start()
