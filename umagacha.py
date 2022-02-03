# encoding:utf-8
import json
import random
import math
import os

from PIL import Image
from nonebot import MessageSegment

from hoshino.util import pic2b64
from hoshino.config import RES_DIR

working_path = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

img_path = os.path.join(RES_DIR, "img", "umagacha")
#img_path = os.path.join(working_path, 'res')
banner_path = os.path.join(img_path, 'pool')
player_path = os.path.join(img_path, 'player')
support_path = os.path.join(img_path, 'support')
for path in [banner_path,player_path,support_path]:
    if not os.path.exists(path):
        os.makedirs(path)

player_pool = {3: [], 2: [], 1: []}
player_data = {}
support_pool = {3: [], 2: [], 1: []}
support_data = {}
gacha_data = {}
cn_data = {}


def data_init():
    global player_pool, support_pool, gacha_data, player_data, support_data, cn_data

    char_data = json.load(
        open(os.path.join(working_path, "db.json"), encoding="utf-8"))
    for player in char_data['players']:
        player_pool[player["default_rarity"]].append(str(player["db_id"]))
        player_data[str(player["db_id"])] = player
    for support in char_data['supports']:
        support_pool[support["rarity"]].append(str(support["db_id"]))
        support_data[str(support["db_id"])] = support

    gacha_data = json.load(
        open(os.path.join(working_path, "banner_data.json"), encoding="utf-8"))

    cn_data = json.load(
        open(os.path.join(working_path, "cn.json"), encoding="utf-8"))


data_init()

probs = {
    "up_3": 50,
    "other_3": 50,
    "star_3": 3,
    "star_2": 18,
    "star_1": 79
}


def get_player_pic(pid):
    charid = pid[:4]
    picname = f"Chr_icon_{charid}_{pid}_01.png"
    picpath = os.path.join(player_path, picname)
    return picpath


def get_player_pic_r(pid):
    rarity=player_data[str(pid)]['default_rarity']
    masker=Image.open(os.path.join(img_path, f'Star_{rarity}_mask.png')).resize((160, 175))
    r, g, b, a = masker.split()
    charid = pid[:4]
    picname = f"Chr_icon_{charid}_{pid}_01.png"
    pic = Image.open(os.path.join(player_path, picname)).resize((160, 175))
    pic.alpha_composite(masker, (0,0))
    return pic


def get_support_pic(sid):
    picname = f"Support_thumb_{sid}.png"
    picpath = os.path.join(support_path, picname)
    return picpath


def get_support_pic_r(sid):
    rarity=support_data[str(sid)]['rarity']
    masker=Image.open(os.path.join(img_path, f'support_r_{rarity}.png')).resize((45, 45))
    r, g, b, a = masker.split()
    picname = f"Support_thumb_{sid}.png"
    pic = Image.open(os.path.join(support_path, picname)).resize((159, 212))
    pic.alpha_composite(masker, (13,0))
    return pic


def roll(n):
    return random.randint(0, n-1)


def pull_naive(rate_3=3):
    star = 1
    up = False
    x1 = roll(100)
    if x1 < probs["star_3"]:
        x2 = roll(100)
        star = 3
        up = (x2 < probs["up_6"])
    elif x1 < probs["star_3"]+probs["star_2"]:
        star = 2
    else:
        pass
    return {"star": star, "up": up}
# learn from HoshinoBot


def gen_team_pic(team, sizex=64, sizey=64, ncol=5, ptype='player'):
    nrow = math.ceil(len(team)/ncol)
    des = Image.new("RGBA", (ncol * sizex, nrow * sizey), (0, 0, 0, 0))
    for i, name in enumerate(team):
        path = get_player_pic(
            name) if ptype == 'player' else get_support_pic(name)
        face = Image.open(path).convert("RGBA").resize(
            (sizex, sizey), Image.LANCZOS)
        x = i % ncol
        y = math.floor(i / ncol)
        des.paste(face, (x * sizex, y * sizey), face)
    return img_segment(des)


def gen_realistic_player_pic(team):
    base_img = Image.open(os.path.join(img_path, 'player_base.png')).convert("RGBA")
    height=175
    width=160
    dis=63
    floor=70
    st1=60
    st1h=110
    st2=170

    boxlist=[]

    box1 = (st1, st1h)
    for i in range(3):
        boxlist.append(box1)
        lst = list(box1)
        lst[0] += width+dis
        box1 = tuple(lst)

    box2 = (st2, st1h+height+floor)
    for i in range(2):
        boxlist.append(box2)
        lst = list(box2)
        lst[0] += width+dis
        box2 = tuple(lst)

    box3 = (st1, st1h+2*(height+floor))
    for i in range(3):
        boxlist.append(box3)
        lst = list(box3)
        lst[0] += width+dis
        box3 = tuple(lst)
    
    box4 = (st2, st1h+3*(height+floor))
    for i in range(2):
        boxlist.append(box4)
        lst = list(box4)
        lst[0] += width+dis
        box4 = tuple(lst)
        

    for i, name in enumerate(team):
        tmp_img = get_player_pic_r(name).resize((width, height))
        r, g, b, a = tmp_img.split()
        base_img.alpha_composite(tmp_img, boxlist[i])
    
    return img_segment(base_img)

def gen_realistic_support_pic(team):
    base_img = Image.open(os.path.join(img_path, 'support_base.png')).convert("RGBA")
    height=212
    width=159
    dis=60
    floor=30
    st1=62
    st1h=125
    st2=175

    boxlist=[]

    box1 = (st1, st1h)
    for i in range(3):
        boxlist.append(box1)
        lst = list(box1)
        lst[0] += width+dis
        box1 = tuple(lst)

    box2 = (st2, st1h+height+floor)
    for i in range(2):
        boxlist.append(box2)
        lst = list(box2)
        lst[0] += width+dis
        box2 = tuple(lst)

    box3 = (st1, st1h+2*(height+floor))
    for i in range(3):
        boxlist.append(box3)
        lst = list(box3)
        lst[0] += width+dis
        box3 = tuple(lst)
    
    box4 = (st2, st1h+3*(height+floor))
    for i in range(2):
        boxlist.append(box4)
        lst = list(box4)
        lst[0] += width+dis
        box4 = tuple(lst)
        

    for i, name in enumerate(team):
        tmp_img = get_support_pic_r(name).resize((width, height))
        r, g, b, a = tmp_img.split()
        base_img.alpha_composite(tmp_img, boxlist[i])
    
    return img_segment(base_img)


def get_player_name(cid, full=True):
    player = player_data[str(cid)]
    name = player['name']
    chara = player['charaName']
    if name in cn_data:
        name = cn_data[name]
    if chara in cn_data:
        chara = cn_data[chara]
    if full:
        return f'[{name}]{chara}'
    else:
        return f'{chara}'


def get_support_name(sid, full=True):
    support = support_data[str(sid)]
    name = support['name']
    chara = support['charaName']
    if name in cn_data:
        name = cn_data[name]
    if chara in cn_data:
        chara = cn_data[chara]
    if full:
        return f'[{name}]{chara}'
    else:
        return f'{chara}'


def img_segment(img):
    return MessageSegment.image(pic2b64(img))


class Gacha:
    def __init__(self):
        self.reset()

    def reset(self):
        self.count = {}
        self.char_count = {}
        self.result_list = []
        #self.rare_list = {5: [], 6: []}
        #self.rare_chance = True
        self.nth = 0
        self.nth_target = 0
        self.nth_favor = 0

    def set_player_banner(self, b, type="playerpool"):
        self.banner = gacha_data["playerpool"][b]
        self.pool = {}
        self.pool["up"] = self.banner["up"]
        exclude = self.banner["up"]  # + self.banner["exclude"]
        for key in [1, 2, 3]:
            self.pool[key] = [x for x in player_pool[key] if x not in exclude]

    def set_support_banner(self, b):
        self.banner = gacha_data["supportpool"][b]
        self.pool = {}
        self.pool["up"] = self.banner["up"]
        exclude = self.banner["up"]  # + self.banner["exclude"]
        for key in [1, 2, 3]:
            self.pool[key] = [x for x in support_pool[key] if x not in exclude]

    def explain_banner(self):
        main_up = self.banner["up"]
        up_name = [get_player_name(x, full=True) for x in main_up]
        main_pic = gen_team_pic(main_up, 64, 70, len(main_up))
        banner_name = self.banner["title"]
        lines = []
        lines.append(f"当前马娘卡池: {banner_name}")
        # print(img_segment(main_pic))
        lines.append(
            f"{img_segment(Image.open(os.path.join(banner_path, self.banner['banner'])))}")
        lines.append(f"主打角色: {' '.join(up_name)}")
        lines.append(f"{main_pic}")
        return "\n".join(lines)

    def explain_s_banner(self):
        main_up = self.banner["up"]
        up_name = [get_support_name(x, full=True) for x in main_up]
        main_pic = gen_team_pic(main_up, 60, 80, len(main_up), ptype='support')
        banner_name = self.banner["title"]
        lines = []
        lines.append(f"当前支援卡池: {banner_name}")
        # print(img_segment(main_pic))
        lines.append(
            f"{img_segment(Image.open(os.path.join(banner_path, self.banner['banner'])))}")
        lines.append(f"主打支援卡: {' '.join(up_name)}")
        lines.append(f"{main_pic}")
        return "\n".join(lines)

    def pull(self, s3_prob=3, s2_prob=18):
        result = []
        statue = 0
        up = False
        x1 = roll(100)
        if x1 < s3_prob:
            x2 = roll(100)
            star = 3
            statue = 20
            up = (x2 < 50)
        elif x1 < s3_prob+s2_prob:
            star = 2
            statue = 3
        else:
            star = 1
            statue = 1
        if up:
            result.append(random.choice(self.pool["up"]))
        else:
            result.append(random.choice(self.pool[star]))
        return result, statue

    def ten_pull(self, s3_prob=3, s2_prob=18):
        result = []
        statue = 0
        for i in range(0, 9):
            up = False
            x1 = roll(100)
            if x1 < s3_prob:
                x2 = roll(100)
                star = 3
                statue += 20
                up = (x2 < 50)
            elif x1 < s3_prob+s2_prob:
                star = 2
                statue += 3
            else:
                star = 1
                statue += 1
            if up:
                result.append(random.choice(self.pool["up"]))
            else:
                result.append(random.choice(self.pool[star]))
        up = False
        x1 = roll(100)
        if x1 < s3_prob:
            x2 = roll(100)
            star = 3
            statue += 20
            up = (x2 < 50)
        else:
            star = 2
            statue += 3
        if up:
            result.append(random.choice(self.pool["up"]))
        else:
            result.append(random.choice(self.pool[star]))
        return result  # , statue

    def tenjo_pull(self, s3_prob=3, s2_prob=18):
        info = {'up': 0, 's3': 0, 's2': 0, 's1': 0}
        result = []
        statue = 0
        first_up_pos = 999
        for i in range(20):
            for j in range(1, 10):
                up = False
                x1 = roll(100)
                if x1 < s3_prob:
                    x2 = roll(100)
                    star = 3
                    statue += 20
                    info['s3'] += 1
                    up = (x2 < 50)
                elif x1 < s3_prob+s2_prob:
                    info['s2'] += 1
                    star = 2
                    statue += 3
                else:
                    info['s1'] += 1
                    star = 1
                    statue += 1
                if up:
                    info['up'] += 1
                    first_up_pos = min(first_up_pos, 10 * i + j)
                    result.append(random.choice(self.pool["up"]))
                elif star == 3:
                    result.append(random.choice(self.pool[star]))
                else:
                    pass
            up = False
            x1 = roll(100)
            if x1 < s3_prob:
                x2 = roll(100)
                star = 3
                info['s3'] += 1
                statue += 20
                up = (x2 < 50)
            else:
                star = 2
                statue += 3
            if up:
                first_up_pos = min(first_up_pos, 10 * i + 10)
                result.append(random.choice(self.pool["up"]))
            elif star == 3:
                result.append(random.choice(self.pool[star]))
            else:
                pass
        info['result'] = result
        info['statue'] = statue
        info['first_up_pos'] = first_up_pos
        return info


def tenjo_summarize(info, ptype='player'):
    if ptype == 'player':
        pic = gen_team_pic(info['result'], 64, 70, ptype=ptype)
    else:
        pic = gen_team_pic(info['result'], 60, 80, ptype=ptype)
    text = []
    text.append(str(pic))
    text.append("抽卡结果:☆3×%d ☆2×%d ☆1×%d" %
                (info['s3'], info['s2'], info['s1']))
    if ptype == 'player':
        text.append("获得女神像×%d！" % info['statue'])
    if info['up'] > 0:
        text.append("第%d抽首次获得up" % info['first_up_pos'])
    else:
        text.append("据说天井的概率只有4.86%")
    # 评价
    judge = info['first_up_pos']
    if judge <= 25:
        text.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
    elif judge < 50:
        text.append("可以了，您已经很欧了")
    elif judge < 100:
        text.append("期望之内，亚洲水平")
    elif judge < 170:
        text.append("补井还是不补井，这是一个问题...")
    elif judge < 201:
        text.append("标 准 结 局")
    else:
        text.append("这位酋长，梦幻包考虑一下？")

    return "\n".join(text)


def summarize_tenpull(rst):
    text = []
    text += ["\n".join([f"☆{player_data[x]['default_rarity']}{get_player_name(x, full=True)}" for x in rst])]
    return "\n".join(text)


def summarize_tenpull_support(rst):
    text = []
    text += ["\n".join([f"{support_data[x]['rare']} {get_support_name(x, full=True)}" for x in rst])]
    return "\n".join(text)
