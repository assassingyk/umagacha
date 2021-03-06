# umagacha

适用hoshino bot的赛马娘抽卡模拟插件。

参考了[hoshino自带pcr抽卡](https://github.com/Ice-Cirno/HoshinoBot/tree/master/hoshino/modules/priconne/gacha)和[akgacha](https://github.com/xulai1001/akgacha)的思路。

基础数据和图像资源主要来自[bilibili赛马娘wiki](https://wiki.biligame.com/umamusume/%E9%A6%96%E9%A1%B5)与[乌拉拉大胜利赛马娘资料站](https://urarawin.com/)的[repo](https://github.com/wrrwrr111/pretty-derby)，感谢各位。

## 特点

- 马娘池与支援卡池基础十连与天井模拟

- 卡池切换与历史卡池选取

- 卡池信息与图像资源在线自动更新功能

- 十连抽结果仿真图片生成


## 安装

- 安装requirements内依赖
- 将本项目放在hoshino/modules/目录下
- 将res内umagacha文件夹放在Hoshino资源目录res/img下
- 在__bot__.py中添加umagacha
- 首次使用请先用维护指令更新基础数据与图像资源


## 使用方法

#### 主要功能指令：

[马娘/支援十连] 马娘/支援抽卡

[马娘天井] 300抽

[查看马娘/支援卡池] 当前马娘/支援卡池信息

[切换马娘/支援卡池 (卡池名)] 更改马娘/支援卡池，如不加卡池名则列出当期卡池列表

[查看马娘/支援历史卡池] 查看马娘/支援全部历史卡池

[切换马娘抽卡模式] 切换十连结果图片的简略/仿真模式，默认简略模式

===

#### 维护指令：

[更新马娘基础数据] 从urarawin更新基础数据db

[更新马娘资源] 根据基础数据从bilibiliwiki更新马娘头像和支援卡等图像资源

[更新马娘卡池] 从bilibiliwiki更新马娘卡池数据并更新卡池banner图像资源

## 示例

- 仿真模式

<img src="https://user-images.githubusercontent.com/55473115/152398334-7fc508d2-c7e2-4ece-8779-f0850d020dc5.jpg" width = "400" alt="">

- 简略模式

<img src="https://user-images.githubusercontent.com/55473115/152398222-4a7a7361-049c-4d27-88a8-dd837729c6b7.jpg" width = "400" alt=""  align=top /><img src="https://user-images.githubusercontent.com/55473115/152398243-fcf3ce6d-a610-4378-86a0-a58f9743172f.jpg" width = "400" alt="" align=top />




