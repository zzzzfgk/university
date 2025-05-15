import csv
import json
import time
from datetime import datetime

import requests

# 设置请求的cookies和headers，用于模拟登录状态和请求头信息
cookies = {
    'kpf': 'PC_WEB',
    'clientid': '3',
    'did': 'web_2a8beae7ededf2cdb3daa48334425899',
    'userId': '4512325721',
    'kuaishou.server.webday7_st': 'ChprdWFpc2hvdS5zZXJ2ZXIud2ViZGF5Ny5zdBKwAWc8Qx3aGJk8E74Q5hapgYN20bnUelZ149AW21wldWvu87hxNgKR6t9NoYg_bxmn0A4u8PWz8M422TTWFwf6J3M9CQVB3iEuZfiRrNpuw6MGINMGsYgE5iiq-FHtIN1xkUON8mDFzwdYnJZtLOfrTGIWL1_6HlFkhxJFGx4xCUm0drN7fh78fppbXeJcz0PldyrFZnT_mjBY-CZZIpUNh7PT4ZoKm8E5kzncOKxs7o2GGhJ32Gzi8Y6eXXgqE46vXeXgmRUiIIdl65WLlU1_1JuF6tmlU-wMx18QkNKAmB5oboxnhUFyKAUwAQ',
    'kuaishou.server.webday7_ph': '29bce4746deb9f87c9424809b3e9b61d5d46',
    'kpn': 'KUAISHOU_VISION',
}

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://www.kuaishou.com',
    'Referer': 'https://www.kuaishou.com/profile/3x5btyya96iquca',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'accept': '*/*',
    'content-type': 'application/json',
    'dnt': '1',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Catsxp";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# 快手主页作品列表的GraphQL查询参数
homepage_json_data = {
    'operationName': 'visionProfilePhotoList',
    'variables': {
        'userId': '3x5btyya96iquca',
        'pcursor': '',
        'page': 'profile',
    },
    'query': 'fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment feedContentWithLiveInfo on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    livingInfo\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContentWithLiveInfo\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',
}
# 快手作品评论列表的GraphQL查询参数
comment_json_data = {
    'operationName': 'commentListQuery',
    'variables': {
        'photoId': '',
        'pcursor': '',
    },
    'query': 'query commentListQuery($photoId: String, $pcursor: String) {\n  visionCommentList(photoId: $photoId, pcursor: $pcursor) {\n    commentCount\n    pcursor\n    rootComments {\n      commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      authorLiked\n      subCommentCount\n      subCommentsPcursor\n      subComments {\n        commentId\n        authorId\n        authorName\n        content\n        headurl\n        timestamp\n        likedCount\n        realLikedCount\n        liked\n        status\n        authorLiked\n        replyToUserName\n        replyTo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
}

photo_list = []  # 存储爬取到的作品信息

#获取主页作品列表信息
def get_homepage_photos_info(num=22):
    while True:
        response = requests.post('https://www.kuaishou.com/graphql', cookies=cookies, headers=headers,
                                 json=homepage_json_data)
        feeds = response.json()['data']['visionProfilePhotoList']['feeds']
        for feed in feeds:
            photo = {
                '编号': feed['photo']['id'],
                '标题': feed['photo']['caption'].replace('\xa0', ' ').replace('\n', '').replace('\r', ''),
                '喜欢数量': feed['photo']['likeCount'],
                '观看数量': feed['photo']['viewCount'],
                '发布时间': datetime.fromtimestamp(int(feed['photo']['timestamp']) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            }

            photo['评论数量'], photo['评论'] = get_comment(feed['photo']['id'])
            photo_list.append(photo)
            save_to_json(photo)
            print(photo)
            time.sleep(1)

            if len(photo_list) >= num:
                return
            else:
                homepage_json_data['variables']['pcursor'] = response.json()['data']['visionProfilePhotoList'][
                    'pcursor']
                if homepage_json_data['variables']['pcursor'] is None or homepage_json_data['variables']['pcursor'] == '':
                    return

#获取指定作品的评论列表
def get_comment(photo_id):
    comment_json_data['variables']['photoId'] = photo_id
    response = requests.post('https://www.kuaishou.com/graphql', cookies=cookies, headers=headers,
                             json=comment_json_data)
    root_comments = response.json()['data']['visionCommentList']['rootComments']
    comments = []
    for comment in root_comments:
        comments.append(comment['content'])
    return [response.json()['data']['visionCommentList']['commentCount'], comments]

#保存作品信息到json文件
def save_to_json(photo):
    with open('kuaishou.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(photo, ensure_ascii=False, indent=4) + '\n')

#保存作品信息到csv文件
# def save_to_csv(photo):
#     with open('kuaishou.csv', 'a', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerow([photo['id'], photo['caption'], photo['publishTime'], photo['likeCount'], photo['viewCount'],
#                          photo['commentCount'], photo['comments']])

#主函数
if __name__ == '__main__':
    get_homepage_photos_info(num=200)
