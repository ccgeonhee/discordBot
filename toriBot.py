import asyncio #비동기 프로그래밍
import math
import matplotlib
import numpy
import pymysql #mysql 데이터베이스
import discord #디스코드 기능
import matplotlib.pyplot as plt
import nest_asyncio
import datetime
import os
from urllib.request import urlopen #크롤링(url open)
from bs4 import BeautifulSoup #크롤링(BeautifulSoup)
from discord.ext import commands

intents = discord.Intents(messages=True, guilds=True, members=True, reactions=True)
bot = commands.Bot(command_prefix="토리야 ", intents=intents)

@bot.event
async def on_ready():
    now = datetime.datetime.now()
    curDate = now.strftime('%Y-%m-%d %H:%M:%S')
    nest_asyncio.apply()
    server_cnt = 0  # 서버개수
    guild_list = bot.guilds
    for i in guild_list:  # 현재 봇이 들어가있는 서버 ID와 서버 이름 출력.
        server_cnt = server_cnt + 1
        print("서버 ID: {} / 서버 이름: {}".format(i.id, i.name))

    print(f"실행시작. 현재 시간은 {curDate} 입니다.")
    # 상태 메시지 설정
    # 종류는 3가지: Game, Streaming, CustomActivity
    # game = discord.Game(str(server_cnt) + " 개의 서버에서 봇 테스트")
    game = discord.Game("'토리야 도움말'을 입력해보세요.")
    # # 계정 상태를 변경한다.
    # # 온라인 상태, game 중으로 설정
    await bot.change_presence(status=discord.Status.online, activity=game)
    # # 간단하게 하자면 아래와 같이 표현 가능
    # print(guild_list)
    conn = pymysql.connect('')
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS scheduleTBL (guildID char(30), channelID char(30), authorName char(20), authorID char(30), scheduleName char(20), scheduleDL DATE, primary key(scheduleName));")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS attcheckTBL (guildID char(30), authorID char(30), checkCnt int(10), isChecked tinyint(1), authorName char(30), PRIMARY KEY (guildID, authorID));")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS timerTBL (channelID char(30), authorID char(30), timerID char(30), time int(10), num int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY);")#수정
    cur.execute(
        "CREATE TABLE IF NOT EXISTS attdateTBL (guildID char(30), authorID char(30), attDate DATE, FOREIGN KEY (guildID, authorID) REFERENCES attcheckTBL(guildID, authorID));")
    cur.execute("CREATE TABLE IF NOT EXISTS covidTBL (date DATE, data int(5), primary key(date));")
    cur.execute("CREATE TABLE IF NOT EXISTS attsetTBL (guildID char(30), setTime Time);")
    cur.execute("CREATE TABLE IF NOT EXISTS testTBL \
       (guildID char(30), userName char(20), userID char(20), voteID char(20), voteName char(20), authorID char(20), pros tinyint(1), cons tinyint(1), num char(5), voteItem char(30))")#수정
    cur.execute(
        "CREATE EVENT IF NOT EXISTS delete_event ON SCHEDULE EVERY 1 MINUTE STARTS '2020-12-22 15:00:00' ON completion preserve "
        "ENABLE COMMENT 'DELETE DATA DEADLINE' DO delete from scheduletbl where Date_ADD(scheduleDL, INTERVAL 1 DAY) <= Date_ADD(now(), INTERVAL 9 HOUR);")  # 일정기한이 지난 일정 삭제.
    cur.execute(
        "CREATE EVENT IF NOT EXISTS Change_Checked ON SCHEDULE EVERY 1 DAY STARTS '2020-12-29 15:00:00' ON completion preserve "
        "ENABLE COMMENT 'Change isChecked == 0' DO UPDATE attchecktbl SET isChecked = 0;")  # 매일 출석체크 초기화
    cur.execute(
        "CREATE EVENT IF NOT EXISTS Change_Month ON SCHEDULE EVERY 1 MONTH STARTS '2021-01-01 15:00:00' ON completion preserve "
        "ENABLE COMMENT 'Change checkCnt == 0' DO UPDATE attchecktbl SET checkCnt = 0;")  # 매달 출석일수 초기화
    cur.execute(
        "CREATE EVENT IF NOT EXISTS Delete_att_Date ON SCHEDULE EVERY 1 MONTH STARTS '2021-01-01 15:00:00' ON completion preserve "
        "ENABLE COMMENT 'Delete attDate every 1 month' DO DELETE FROM attdatetbl;")  # 매달 출석일 삭제.
    conn.commit()
    conn.close()

#수정
@bot.event
async def on_guild_join(guild):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await guild.create_text_channel('toriBot', overwrites=overwrites)
    text = ">>> 초대해주셔서 감사합니다!\n\n 토리 봇은 비대면 그룹 활동을 보조해주는 스케줄링 봇 입니다.\n\n " \
           "제공 기능은 `토리야 도움말`을 통해 확인하실 수 있습니다. 디스코드에 익숙하지 않으시다면 `토리야 가이드` 를" \
           "입력해주세요. \n\n 만약 봇 이용 중에 버그가 발생하거나, 문의할 점이" \
           " 있으시다면 언제든지 \n`토리야 문의하기`를 통해 개발자에게 문의해주세요! 감사합니다.\n\n "
    embed = discord.Embed(title="toriBot 두둥등장!", description=text)
    embed.set_footer(text="Made by DotoriMuk#4593")
    await channel.send(embed=embed)

    channel2 = await guild.create_text_channel('#자료방', overwrites=overwrites)
    text = ">>> 여기는 서로 자료를 공유하는 자료방입니다. 자료는 최대 8MB까지 업로드 가능합니다."
    embed = discord.Embed(title="자료방이 생성되었습니다.", description=text)
    await channel2.send(embed=embed)

async def drawingGraph():  # 매일 실행.
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("drawingGraph")
        now = datetime.datetime.now()
        curDate = now.strftime('%Y-%m-%d')
        day = []
        data = []
        conn = pymysql.connect('')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM covidTBL WHERE date >= Date_SUB('{curDate}', INTERVAL 6 DAY) ORDER BY date DESC;")
        while (True):
            row = cur.fetchone()
            if row == None:
                break
            day.append(str(row[0])[5:])
            data.append(row[1])

        day = list(reversed(day))
        data = list(reversed(data))
        graph = numpy.arange(len(day))
        y_lower = [i * 0.9 for i in data]
        y_upper = [i * 1.1 for i in data]

        for i, v in enumerate(day):
            plt.text(v, data[i], data[i], fontsize=11, color='black', horizontalalignment='center',
                     verticalalignment='bottom')
        fontprop = matplotlib.font_manager.FontProperties(fname=f"{os.getcwd()}/cogs/NanumGothic.ttf", size=13)
        plt.fill_between(day, y_lower, y_upper, alpha=0.2)
        plt.bar(graph, data, width=0.4, color="skyblue")
        plt.xticks(graph, day)
        plt.title('확진자 총 합계 추이', fontproperties=fontprop)
        plt.xlabel('날짜', fontproperties=fontprop)
        plt.ylabel('확진자 수', fontproperties=fontprop)
        plt.savefig('./cogs/savefig.png')
        conn.commit()
        conn.close()
        await asyncio.sleep(60 * 60 * 24)

async def Add_Covid_Data():  # 매일 실행.
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("Add_Covid_Data")
        html = urlopen("http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13")
        bsObject = BeautifulSoup(html, "html.parser")
        all_data = bsObject.find('div', 'data_table midd mgt24')
        place_name = all_data.find_all('th')
        place_data = all_data.find_all('td')
        now = datetime.datetime.now()
        Date = now.strftime('%Y-%m-%d')
        conn = pymysql.connect('')
        cur = conn.cursor()

        place_name_list = []  # 지역 리스트
        place_data_list = []  # 데이터 리스트

        for i in place_name:
            place_name_list.append(i.get_text())
        place_name_list = place_name_list[place_name_list.index('합계', 10):]
        j = 1  # 전일대비 확진환자 증감 합계만 알아내기 위해 임시변수j 활용.
        for i in place_data:
            if j == 1 or j % 8 == 1:  # 총 합계, 해외유입, 국내발생, 확진 환자, 격리 중, 격리 해제, 사망자, 발생률 총 8개의 항목. 합계만 알아내기위해 첫 번째 데이터만 고름.
                place_data_list.append(i.get_text())  # 데이터를 추가시킴.
            j = j + 1
        for i in range(len(place_name_list)):
            if place_name_list[i] == '합계':
                cur.execute(f"INSERT INTO covidTBL(date, data) VALUES ('{Date}', {int(place_data_list[i])});")
            else:
                pass
        conn.commit()
        conn.close()
        await asyncio.sleep(60 * 60 * 24)

async def loadTimer():  # 1분마다 타이머값을 불러들여옴. 30분마다, 남은시간이 60,30,0분일때 알림.
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("loadTimer")
        conn = pymysql.connect('')
        cur = conn.cursor()
        channelID = []
        timer = []
        originTime = []
        authorID = []

        cur.execute("UPDATE timerTBL SET timer = timer - 1;")
        conn.commit()

        cur.execute("SELECT * FROM timerTBL;")
        while (True):
            row = cur.fetchone()
            if row == None:
                break
            channelID.append(row[0])
            originTime.append(row[1])
            timer.append(row[2])
            authorID.append(row[3])

        for i in range(len(channelID)):
            progress = int(originTime[i]) - int(timer[i])  # 진행 시간
            per_progress = round(progress / (float(originTime[i])+0.1) * 100)  # 진행률
            num_of_square = math.floor(per_progress / 10)  # 사각형 개수
            progress_bar = ""
            for j in range(num_of_square):
                progress_bar += "\U0001F7E9"
            for j in range(10 - num_of_square):
                progress_bar += "\U00002B1C"

            channel = bot.get_channel(int(channelID[i]))
            if (timer[i] != 60 and timer[i] != 30 and timer[i] != 0) and ((originTime[i] - timer[i]) % 30 == 0):
                await channel.send("<@" + authorID[i] + ">")
                embed = discord.Embed(title="\U000023F3 30분 지났습니다. 남은 시간 =`" + str(timer[i]) + "분` \n" + progress_bar)
                await channel.send(embed=embed)
            elif timer[i] == 60:
                await channel.send("<@" + authorID[i] + ">")
                embed = discord.Embed(title="\U000023F3 60분 남았습니다!\n" + progress_bar)
                await channel.send(embed=embed)
            elif timer[i] == 30:
                await channel.send("<@" + authorID[i] + ">")
                embed = discord.Embed(title=" \U0000231B 30분 남았습니다! 조금만 더 힘내요!\n" + progress_bar)
                await channel.send(embed=embed)
            elif timer[i] == 0:
                await channel.send("<@" + authorID[i] + ">")
                embed = discord.Embed(title=" \U000023F0 타이머가 종료되었습니다. 수고하셨습니다.")
                await channel.send(embed=embed)
                cur.execute(
                    "DELETE FROM timerTBL WHERE channelID = '" + channelID[i] + "' AND timer = " + str(timer[i]) + ";")

        conn.commit()
        conn.close()
        await asyncio.sleep(60)

async def loadData():
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("loadData")
        conn = pymysql.connect('')
        cur = conn.cursor()
        now = datetime.datetime.now()
        channelID = []
        authorID = []
        scheduleName = []
        deadline = []
        today = now.strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM scheduleTBL")
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            channelID.append(row[1])
            authorID.append(row[3])
            scheduleName.append(row[4])
            deadline.append(str(row[5]))
            # print(channelID, authorID, scheduleName, deadline)
        conn.commit()
        conn.close()
        for i in range(len(deadline)):
            if deadline[i] == today:
                channel = bot.get_channel(int(channelID[i]))
                # print(channel)
                msg = "<@" + authorID[i] + ">님, '" + scheduleName[i] + "' 일정이 오늘까지 입니다."
                await channel.send(msg)
        await asyncio.sleep(60 * 60 * 24)


# 프로그램이 실행되면 제일 처음으로 실행되는 함수
if __name__ == "__main__":
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
    bot.loop.create_task(loadData())
    bot.loop.create_task(loadTimer())
    bot.loop.create_task(Add_Covid_Data())
    bot.loop.create_task(drawingGraph())
    bot.run("token")

