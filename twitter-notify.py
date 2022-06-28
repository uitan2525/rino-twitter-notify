import requests
import json
import os

import datetime

# ふっしー用
line_notify_token = "tr2qcAPf05DiY6ifdMykw1XUTJbcBW1jQsm7QXga1j0"
line_notify_api = "https://notify-api.line.me/api/notify"

insta_feed_path = '/home/uitan/git/フォロワー用/rino_twitter/twitterFeed.txt'
image_dir_path = '/home/uitan/git/フォロワー用/rino_twitter/image_0.'

# RSSフィード（暫定対応）
URL = 'http://localhost/rss-bridge/?action=display&bridge=Twitter&context=By+username&u=sureness_rino&norep=on&noretweet=on&nopinned=on&nopic=on&noimgscaling=on&format=Json'

def getInstagramJson():
    response = requests.get(URL)
    jsonData = response.json()
    items = jsonData["items"]

    return items

def saveFeed(items):
    for item in items:
        itemUrl = item["id"]

        try:
            images = item['attachments']
            title = item['title']

            with open(insta_feed_path, mode='r', newline='', encoding='utf-8') as f_in:
                flag = False
                lines = [line for line in f_in]
                for i in lines:
                    if itemUrl in i:
                        flag = True

                if not flag:
                    file = open(insta_feed_path, 'a', encoding='utf-8')
                    file.write(itemUrl + '\n')
                    file.close()

                    # 画像保存関数
                    saveImage(images, title, itemUrl)
        except KeyError:
            print("画像無し")

def saveImage(images, title, itemUrl):
    imageIndex = 1
    imageLen = len(images)

    for image in images:
        picture = image['url']
        re = requests.get(picture)

        # 拡張子をContent-typeから取得
        fileTypes = re.headers['Content-Type'].split('/')[-1]
        fileType = "".join(fileTypes)
        # Content-typeの拡張子を画像パスにつける
        filePath = image_dir_path + fileType
        
        # ローカルに保存
        with open(filePath , 'wb') as f:
            f.write(re.content)

        sendLineNotify2(title, itemUrl, imageLen, imageIndex, fileType)

        imageIndex = imageIndex + 1
        
        # 削除処理
        os.remove(image_dir_path + fileType)

def sendLineNotify2(text, url, imageLen, index, fileType):

    headers = {'Authorization': 'Bearer ' + line_notify_token}

    if index == 1:
        sendMassage = ' 📸Twitter投稿枚数%d枚 \n\n %s \n %s' % (imageLen, text, url)
    else:
        sendMassage = ' %d枚目 / %d枚中' % (index, imageLen)
    
    if fileType == "jpeg":
        image_dir_path2 = image_dir_path + 'jpeg'
        payload = {'message': sendMassage}
        files = {"imageFile": open(image_dir_path2, "rb")}
        requests.post(line_notify_api, data=payload, headers=headers, files=files)

def main():
    try:
        items = getInstagramJson()
        saveFeed(items)
    except:
        print('Error')

if __name__ == '__main__':
    main()
