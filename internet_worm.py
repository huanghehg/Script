import requests
import json
import asyncio
from lxml import etree
from lxml import html
import lxml
import time
import base64

headers = {
    'User-Agent': "xxxxxx",
    'Cookie': "xxxxx"
}

params = {
    'action':"getmsg",
    '__biz':"xxxx",
    "f":"json",
    "is_ok":"1",
    "scene":"124",
    "uin":"xxxx",
    "key":"xxxxx",
    "pass_ticket":"xxxx",
    "appmsg_token":"xxxxx",
    "x5":"0",
    "offset":"0",
    "count":"10"
}

url = "https://mp.weixin.qq.com/mp/profile_ext"

async def get_article_list():
    can_msg_continue = True
    while can_msg_continue:
        response = requests.get(url=url, headers=headers, params=params, verify=False)
        # if len(response["errmsg"]) > 0: break
        data = json.loads(str(response.content, encoding='utf-8'))
        params["offset"] = str(data["next_offset"])
        can_msg_continue = int(data["can_msg_continue"])
        general_msg_list = json.loads(data["general_msg_list"])
        print(general_msg_list)
        for article in general_msg_list["list"]:
            asyncio.create_task(get_article(article))
        await asyncio.sleep(0)
    pass


async def get_article(article):
    time_array = time.localtime(article["comm_msg_info"]["datetime"])
    other_way_time = time.strftime("%Y.%m.%d", time_array)
    file_name = '%s-%s.html' % (other_way_time, article["app_msg_ext_info"]["title"])
    print("下载{}".format(file_name))
    response = requests.get(url=article["app_msg_ext_info"]["content_url"], headers=headers, verify=False);

    res = str(response.content, encoding='utf-8')
    html = etree.HTML(res);
    image_arr = html.xpath('//*[@id="js_content"]/p/descendant::img')
    for img in image_arr:
        image_data = img.attrib['data-src'];
        picture = requests.get(image_data,headers=headers, verify=False).content
        base64_data = base64.b64encode(picture)
        img.attrib['src'] = 'data:image/png;base64,' + str(base64_data, encoding='utf-8');

    txt = lxml.html.tostring(html);

    with open(file_name, 'w+') as f:
        f.write(str(txt, encoding="utf-8"))


if __name__ == "__main__":
    asyncio.run(get_article_list())