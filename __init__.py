# encoding:utf-8
import os
import json

from datetime import datetime
from traceback import format_exc

from hoshino import R, Service, priv, util
from hoshino.typing import MessageSegment, CQEvent
from hoshino.util import FreqLimiter, DailyNumberLimiter

from .umagacha import *
from .umares import update_base_data, down_player, down_support, down_pool

working_path = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
#char_data = json.load(open(os.path.join(working_path, "db.json"), encoding="utf-8"))
gacha_data = json.load(
    open(os.path.join(working_path, "banner_data.json"), encoding="utf-8"))

EXCEED_NOTICE = f'您今天已经抽过6000钻了，请明早5点后再来~'
EXCEED_NOTICE2 = f'您今天已经抽过2井了，请明早5点后再来~'

_nlmt = DailyNumberLimiter(4)
_tlmt = DailyNumberLimiter(2)

sv_help = '''
[马娘十连] 马娘抽卡
[马娘天井] 马娘抽一井
[查看马娘卡池] 当前马娘卡池信息
[切换马娘卡池] 更改马娘卡池

[支援十连] 支援抽卡
[支援天井] 支援抽一井
[查看支援卡池] 当前支援卡池信息
[切换支援卡池] 更改支援卡池

[切换马娘抽卡模式] 切换十连结果图片的简略/仿真模式，默认简略
'''.strip()

sv = Service('umagacha', help_=sv_help, bundle="娱乐", enable_on_default=True)

group_banner = {}

try:
    group_banner = json.load(
        open(os.path.join(working_path, "group_banner.json"), encoding="utf-8"))
except FileNotFoundError:
    print('load umagacha group config error!')
    pass


def save_group_banner():
    with open(os.path.join(working_path, "group_banner.json"), "w", encoding="utf-8") as f:
        json.dump(group_banner, f, ensure_ascii=False)


def group_init(gid):
    group_banner[gid] = {"banner": "30016", "banner_s": "30061", "method": "simple"}


@sv.on_fullmatch(("查看马娘卡池"))
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        group_init(gid)
    banner = group_banner[gid]["banner"]
    gacha = Gacha()
    gacha.set_player_banner(banner)
    line = gacha.explain_banner()
    await bot.send(ev, line)


@sv.on_fullmatch(("查看支援卡池"))
async def s_gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        group_init(gid)
    banner = group_banner[gid]["banner_s"]
    gacha = Gacha()
    gacha.set_support_banner(banner)
    line = gacha.explain_s_banner()
    await bot.send(ev, line)


@sv.on_prefix(("切换马娘卡池"))
async def set_pool(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)
    if not gid in group_banner:
        group_init(gid)
    if not name:
        # 列出当前卡池
        current_time = datetime.now().timestamp()
        list_cur = []
        for gacha in gacha_data["playerpool"]:
            if int(gacha_data["playerpool"][gacha]["end"]) > int(current_time):
                list_cur.append(gacha_data["playerpool"][gacha]["title"])
        if list_cur:
            lines = ["当期卡池:"] + list_cur + \
                ["", "使用命令[切换马娘卡池 （卡池名）]进行设置", "使用命令[查看马娘历史卡池]查看全部往期卡池"]
            await bot.finish(ev, "\n".join(lines))
        else:
            await bot.finish(ev, "未找到正在进行中的卡池……请联系维护组更新卡池信息或使用命令[查看马娘历史卡池]查看全部往期卡池")
    else:
        for gacha in gacha_data["playerpool"]:
            if name == gacha_data["playerpool"][gacha]["title"]:
                group_banner[gid]["banner"] = gacha
                save_group_banner()
                await bot.send(ev, f"卡池已经切换为 {name}", at_sender=True)
                await gacha_info(bot, ev)
                return
        await bot.finish(ev, f"没找到卡池: {name}")


@sv.on_prefix(("切换支援卡池"))
async def set_pool(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)
    if not gid in group_banner:
        group_init(gid)
    if not name:
        # 列出当前卡池
        current_time = datetime.now().timestamp()
        list_cur = []
        for gacha in gacha_data["supportpool"]:
            if int(gacha_data["supportpool"][gacha]["end"]) > int(current_time):
                list_cur.append(gacha_data["supportpool"][gacha]["title"])
        if list_cur:
            lines = ["当期卡池:"] + list_cur + \
                ["", "使用命令[切换支援卡池 （卡池名）]进行设置", "使用命令[查看支援历史卡池]查看全部往期卡池"]
            await bot.finish(ev, "\n".join(lines))
        else:
            await bot.finish(ev, "未找到正在进行中的卡池……请联系维护组更新卡池信息或使用命令[查看支援历史卡池]查看全部往期卡池")
    else:
        for gacha in gacha_data["supportpool"]:
            if name == gacha_data["supportpool"][gacha]["title"]:
                group_banner[gid]["banner_s"] = gacha
                save_group_banner()
                await bot.send(ev, f"卡池已经切换为 {name}", at_sender=True)
                await s_gacha_info(bot, ev)
                return
        await bot.finish(ev, f"没找到卡池: {name}")


@sv.on_fullmatch(("查看马娘历史卡池"))
async def history_pool(bot, ev: CQEvent):
    lines = ["全部卡池:"]
    for gacha in gacha_data["playerpool"]:
        lines.append(gacha_data["playerpool"][gacha]["title"])
    lines.append("使用命令 切换马娘卡池 [卡池名] 进行设置")
    await bot.finish(ev, "\n".join(lines))


@sv.on_fullmatch(("查看支援历史卡池"))
async def history_pool(bot, ev: CQEvent):
    lines = ["全部卡池:"]
    for gacha in gacha_data["supportpool"]:
        lines.append(gacha_data["supportpool"][gacha]["title"])
    lines.append("使用命令 切换支援卡池 [卡池名] 进行设置")
    await bot.finish(ev, "\n".join(lines))


@sv.on_prefix(("马娘十连"))
async def gacha_10(bot, ev: CQEvent):
    gid = str(ev.group_id)
    uid = ev['user_id']
    if not _nlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE, at_sender=True)
        return
    if not gid in group_banner:
        group_init(gid)
    b = group_banner[gid]["banner"]
    method= group_banner[gid]["method"]
    print(method)
    g = Gacha()
    g.set_player_banner(b)
    g.rare_chance = False
    result = g.ten_pull()
    if method=='simple':
        pic = gen_team_pic(result, 64, 70, ptype='player')
    elif method=='realistic':
        pic = gen_realistic_player_pic(result)
    await bot.send(ev, pic+'\n'+summarize_tenpull(result), at_sender=True)
    _nlmt.increase(uid)


@sv.on_prefix(("支援十连"))
async def gacha_10(bot, ev: CQEvent):
    gid = str(ev.group_id)
    uid = ev['user_id']
    if not _nlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE, at_sender=True)
        return
    if not gid in group_banner:
        group_init(gid)
    b = group_banner[gid]["banner_s"]
    method= group_banner[gid]["method"]
    g = Gacha()
    g.set_support_banner(b)
    result = g.ten_pull()
    if method=='simple':
        pic = gen_team_pic(result, 60, 80, ptype='support')
    elif method=='realistic':
        pic = gen_realistic_support_pic(result)
    await bot.send(ev, pic+'\n'+summarize_tenpull_support(result), at_sender=True)
    _nlmt.increase(uid)


@sv.on_prefix(("马娘天井", "马娘来一井"))
async def gacha_300(bot, ev: CQEvent):
    gid = str(ev.group_id)
    uid = ev['user_id']
    if not _tlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE2, at_sender=True)
        return
    if not gid in group_banner:
        group_init(gid)
    b = group_banner[gid]["banner"]
    g = Gacha()
    g.set_player_banner(b)
    info = g.tenjo_pull()
    await bot.send(ev, tenjo_summarize(info), at_sender=True)
    _tlmt.increase(uid)


@sv.on_prefix(("支援天井", "支援来一井"))
async def gacha_300(bot, ev: CQEvent):
    gid = str(ev.group_id)
    uid = ev['user_id']
    if not _tlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE2, at_sender=True)
        return
    if not gid in group_banner:
        group_init(gid)
    b = group_banner[gid]["banner_s"]
    g = Gacha()
    g.set_support_banner(b)
    info = g.tenjo_pull()
    await bot.send(ev, tenjo_summarize(info, ptype='support'), at_sender=True)
    _tlmt.increase(uid)


@sv.on_fullmatch('切换马娘抽卡模式')
async def change_method(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        group_init(gid)
    methodnow=group_banner[gid]["method"]
    if methodnow=='simple':
        group_banner[gid]["method"]='realistic'
        save_group_banner()
        await bot.send(ev, f"已切换为仿真模式", at_sender=True)
    elif methodnow=='realistic':
        group_banner[gid]["method"]='simple'
        save_group_banner()
        await bot.send(ev, f"已切换为简略模式", at_sender=True)


@sv.on_prefix('马娘抽卡氪金')
async def kakin(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS:
        await bot.send(ev, f"只有维护组才能使用此命令～")
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            _nlmt.reset(uid)
            _tlmt.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")


@sv.on_fullmatch('更新马娘基础数据')
async def update_data(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev,'此命令仅维护组可用，请联系维护组~')
        return
    await bot.send(ev, '正在更新请稍候……')
    try:
        result = await update_base_data()
        await bot.send(ev, '更新基础数据成功！')
    except Exception as e:
        print(format_exc())
        await bot.send(ev, f'更新失败……{e}')

@sv.on_fullmatch('更新马娘资源')
async def update_res(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev,'此命令仅维护组可用，请联系维护组~')
        return
    await bot.send(ev, '正在更新请稍候……')
    try:
        player_result = await down_player()
        support_result = await down_support()
        if player_result+support_result:
            await bot.send(ev, f'更新资源成功！已新增{player_result+support_result}张图像！')
        else:
            await bot.send(ev, '资源已是最新版本！')
    except Exception as e:
        print(format_exc())
        await bot.send(ev, f'更新失败……{e}')

@sv.on_fullmatch(("更新马娘卡池"))
async def update_pool(bot, ev: CQEvent):
    global gacha_data
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev,'此命令仅维护组可用，请联系维护组~')
        return
    await bot.send(ev, '正在更新请稍候……')
    try:
        result = await down_pool()
        if result:
            data_init()
            gacha_data = json.load(open(os.path.join(working_path, "banner_data.json"), encoding="utf-8"))
            await bot.send(ev, f'更新卡池成功！新增{result}个卡池！')
        else:
            await bot.send(ev, '卡池已是最新版本！')
    except Exception as e:
        print(format_exc())
        await bot.send(ev, f'更新失败……{e}')