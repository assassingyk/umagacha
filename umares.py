import re, json, requests, time, os, copy
from bs4 import BeautifulSoup
from contextlib import closing
from async_retrying import retry

from hoshino import aiorequests
from hoshino.config import RES_DIR

proxies={'http':'http://127.0.0.1:7890','https':'http://127.0.0.1:7890'}

uma_url=r'https://wiki.biligame.com/umamusume/%E8%B5%9B%E9%A9%AC%E5%A8%98%E5%9B%BE%E9%89%B4'
support_url=r'https://wiki.biligame.com/umamusume/%E6%94%AF%E6%8F%B4%E5%8D%A1%E5%9B%BE%E9%89%B4'
pool_url=r'https://wiki.biligame.com/umamusume/%E5%8D%A1%E6%B1%A0'

working_path = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

img_path = os.path.join(RES_DIR, "img", "umagacha")
#img_path = os.path.join(working_path, 'res')
banner_path = os.path.join(img_path, 'pool')
player_path = os.path.join(img_path, 'player')
support_path = os.path.join(img_path, 'support')
for path in [banner_path,player_path,support_path]:
    if not os.path.exists(path):
        os.makedirs(path)

@retry(attempts=3)
async def down_from_git(url, file):
    urlpart=url.split(r'https://github.com/')[-1]
    try:
        res = await aiorequests.get(rf"https://raw.githubusercontent.com/{urlpart}", timeout=10,proxies=proxies)
    except:
        try:
            res = await aiorequests.get(rf"https://raw.githubusercontent.com/{urlpart}", timeout=10)
        except:
            try:
                res = await aiorequests.get(rf"https://gitcdn.link/repo/{urlpart}", timeout=10,proxies=proxies)
            except:
                res = await aiorequests.get(rf"https://gitcdn.link/repo/{urlpart}", timeout=10)
    data = await res.json()
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))
    return


async def update_base_data():
    dbpath=os.path.join(working_path, "db.json")
    cnpath=os.path.join(working_path, "cn.json")
    await down_from_git(r"https://github.com/wrrwrr111/pretty-derby/master/src/assert/db.json", dbpath)
    await down_from_git(r"https://github.com/wrrwrr111/pretty-derby/master/src/assert/cn.json", cnpath)


@retry(attempts=3)
async def down_pic_from_thumb(url, name, path):
    link=url.replace('/thumb', '')
    link='/'.join(link.split('/')[:-1])
    png_path = os.path.join(path, name)
    if os.path.exists(png_path):
        print('already there, pass')
        return 0
    png = await aiorequests.get(link, timeout=20, proxies=proxies)
    png = await png.content
    with open(png_path, 'wb') as f:
        print(f'down {name}')
        f.write(png)
    return 1

async def down_player():
    print('\n\nnow start player\n\n')
    down=[]
    counter=0
    r = await aiorequests.get(uma_url, proxies=proxies)
    soup = BeautifulSoup(await r.text)
    for index in soup.find(id="CardSelectTr").find_all('tr')[1:]:
        name=index.span.text[1:-1]
        try:
            iconlink=index.a.img['src']
            filename=iconlink.split('-')[-1]
            down.append([iconlink, filename])
        except:
            print(f'error in {name} icon')
            continue

    for set in down:
        try:
            filename = set[1]
            png_path = os.path.join(player_path, filename)
            if os.path.exists(png_path):
                print('already there, pass')
                continue
            res=await down_pic_from_thumb(set[0], filename, player_path)
            counter+=res
        except Exception as e:
            print(f'error in down {set[1]}')
    return counter


async def down_support():
    print('\n\nnow start support\n\n')
    down=[]
    counter=0
    r = await aiorequests.get(support_url, proxies=proxies)
    soup = BeautifulSoup(await r.text)
    for index in soup.find(id="CardSelectTr").find_all('tr')[1:]:
        try:
            iconlink=index.a.img['src']
            filename=iconlink.split('-')[-1]
            down.append([iconlink, filename])
        except:
            print(f'error check')
            continue

    for set in down:
        try:
            filename = set[1]
            png_path = os.path.join(support_path, filename)
            if os.path.exists(png_path):
                print('already there, pass')
                continue
            res=await down_pic_from_thumb(set[0], filename, support_path)
            counter+=res
        except Exception as e:
            print(f'error in down {set[1]}')
    return counter


async def down_pool():
    playerpool={}
    supportpool={}
    print('\n\nnow start down pool\n\n')
    counter=0
    r = await aiorequests.get(pool_url, proxies=proxies)
    soup = BeautifulSoup((await r.text).replace('\n','').replace('<br>', '').replace('<br/>', ''))
    
    for index in soup.find_all('td', text='赛马娘卡池'):
        tempinfo={}
        index=index.parent

        gachatime=index.td.text
        opentime = gachatime.split('~')[0]
        opentimestp = time.mktime(time.strptime(opentime, "%Y/%m/%d %H:%M"))
        endtime = gachatime.split('~')[1]
        endtimestp = time.mktime(time.strptime(endtime, "%Y/%m/%d %H:%M"))
        tempinfo["open"] = opentimestp
        tempinfo["end"] = endtimestp

        tempinfo['title']=index.a['title']
        banner=index.a.img['src']
        tempinfo['banner']=banner.split('-')[-1]
        poolid=tempinfo['banner'].split('_')[-1].split('.')[0]
        tempinfo['poolid']=poolid
        imglist=index.find_all('img')
        up=[]
        for img in imglist:
            if img['alt'][:8]!='Chr icon':
                continue
            else:
                up.append(img['alt'].split('.')[0].split(' ')[3])
        print(f'pool {index.a["title"]} has {len(up)} up.')
        tempinfo['up']=up
        playerpool[poolid]=copy.deepcopy(tempinfo)
        res=await down_pic_from_thumb(banner, banner.split('-')[-1], banner_path)
        counter+=res
        
    for index in soup.find_all('td', text='支援卡卡池'):
        tempinfo={}
        index=index.parent
        #time=index.td.text
        tempinfo['title']=index.a['title']
        banner=index.a.img['src']
        tempinfo['banner']=banner.split('-')[-1]
        
        poolid=tempinfo['banner'].split('_')[-1].split('.')[0]
        tempinfo['poolid']=poolid
        playerid=str(int(poolid)-1)
        if playerid in playerpool:
            tempinfo["open"] = playerpool[playerid]["open"]
            tempinfo["end"]=playerpool[playerid]["end"]
        else:
            tempinfo["open"] =tempinfo["end"]=time.mktime(time.strptime('2001/01/01 00:00', "%Y/%m/%d %H:%M"))
        
        imglist=index.find_all('img')
        up=[]
        for img in imglist:
            if img['alt'][:13]!='Support thumb':
                continue
            else:
                up.append(img['alt'].split('.')[0].split(' ')[2])
        print(f'pool {index.a["title"]} has {len(up)} up.')
        tempinfo['up']=up
        supportpool[index.a['title']]=copy.deepcopy(tempinfo)
        res=await down_pic_from_thumb(banner, banner.split('-')[-1], banner_path)
        counter+=res

    pooldata={'playerpool':playerpool, 'supportpool':supportpool}

    with open(os.path.join(working_path, "banner_data.json"), "w", encoding="utf-8") as f:
        json.dump(pooldata, f, indent=2, ensure_ascii=False)
    
    return counter