import asyncio #비동기 프로그래밍
import math
import pymysql #mysql 데이터베이스
import discord #디스코드 기능
import datetime
import calendar
from discord.ext import commands

class AttCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def show_att_ranking(self,message):
        channel = message.channel
        guildID = str(message.guild.id)
        authorName = []
        checkCnt = []
        progressBar = ""
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month
        dayOfMonth = calendar.monthrange(year, month)[1]  # 이 달의 일 수 ex)1월 - 31일

        conn = pymysql.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT checkCnt, authorName FROM attcheckTBL WHERE guildID = '" + guildID + "' ORDER BY checkCnt desc;")
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            checkCnt.append(row[0])
            authorName.append(row[1])
        embed = discord.Embed(title="📌  현재 서버의 출석점수 랭킹", description="`출석 점수` = `출석일 수 x 3 point`")
        conn.commit()
        conn.close()
        for i in range(len(authorName)):
            check_per_month = round((checkCnt[i] / dayOfMonth) * 100, 1)  # 출석률
            num_of_square = math.floor(check_per_month / 10)  # 검은 사각형 개수(출석 진행도)
            for j in range(num_of_square):
                progressBar += "\U0001F7E9"
            for j in range(10 - num_of_square):
                progressBar += "\U00002B1C"

            embed.add_field(name=str(i + 1) + "위\t" + authorName[i] + "\t\t" + str(checkCnt[i] * 3) + "점\n",
                            value=progressBar +
                                  " 출석률: " + str(check_per_month) + "%", inline=False)
            progressBar = ""

        await channel.send(embed=embed)

    # 수정
    @commands.command()
    async def 출석설정(self,ctx):
        guildID = ctx.guild.id
        embed = discord.Embed(title="\U0001F6E0	 출석시간설정 [서버장 기능]",
                              description="출석시간을 입력해주세요. \nex)아침 8시인 경우 8:00 입력, 오후 3시반인 경우 15:30입력\n\n"
                                          "시간설정 취소를 원할 경우 '#시간설정취소'\n'#취소' 입력시 취소.",
                              color=0x00aaaa)
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("시간초과")
        else:
            await msg.delete()
            if msg2.content == '#취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            try:
                if ctx.author.id != ctx.guild.owner_id:  # 서버장이 아닐경우.
                    embed = discord.Embed(title="🚫  설정 실패", description=ctx.author.name + "님은 서버장이 아닙니다.")
                    await ctx.send(embed=embed)
                    return
                elif ctx.author.id == ctx.guild.owner_id and msg2.content == '#시간설정취소':  # 시간설정취소를 원할경우
                    conn = pymysql.connect()
                    cur = conn.cursor()
                    cur.execute(f"DELETE FROM attsetTBL WHERE guildID = '{guildID}';")
                    conn.commit()
                    conn.close()

                    embed = discord.Embed(title="\U00002611  취소 완료", description="설정된 시간 값이 삭제되었습니다.")
                    await ctx.send(embed=embed)
                else:  # 시간설정을 원할 경우
                    conn = pymysql.connect()
                    cur = conn.cursor()
                    cur.execute(
                        f"SELECT EXISTS (SELECT * FROM attsetTBL WHERE guildID = '{guildID}') as success;")  # 설정시간 존재여부
                    while (True):
                        row = cur.fetchone()  # 한 행씩 추출
                        if row == None:
                            break
                        setChecked = row[0]

                    if setChecked == 0:  # 설정시간이 없으면 INSERT
                        setTime = msg2.content
                        cur.execute(f"INSERT attsetTBL (guildID, setTime) VALUES ('{guildID}', '{setTime}');")
                        conn.commit()
                        conn.close()
                        embed = discord.Embed(title="\U00002611  설정 완료", description=f"'{setTime}'으로 출석시간이 설정되었습니다.")
                        await ctx.send(embed=embed)
                    else:  # 설정시간이 있으면 UPDATE
                        setTime = msg2.content
                        cur.execute(f"UPDATE attsetTBL SET setTime = '{setTime}' WHERE guildID = '{guildID}';")
                        conn.commit()
                        conn.close()
                        embed = discord.Embed(title="\U00002611  설정 완료", description=f"'{setTime}'으로 출석시간이 설정되었습니다.")
                        await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)15:30")
                await ctx.send(embed=embed)

    @commands.command()  # 수정
    async def 출석체크(self,ctx):
        guildID = str(ctx.guild.id)  # 서버ID
        authorID = str(ctx.author.id)  # 유저ID
        authorName = str(ctx.author)
        existChecked = 0  # 존재여부
        timeChecked = 0
        isChecked = 0  # 출석여부
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y-%m-%d')

        conn = pymysql.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS (SELECT * FROM attcheckTBL WHERE guildID = '" + guildID + "' AND authorID= '" + authorID + "') as success;")  # 출석일 존재여부
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            existChecked = row[0]

        cur.execute(
            f"SELECT EXISTS (SELECT * FROM attsetTBL WHERE guildID = '{guildID}') as success;")  # 출석시간 설정되어있는지 확인.
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            timeChecked = row[0]  # 출석시간 존재여부

        if existChecked == 0:  # 데이터베이스에 값이 없고
            if timeChecked == 0:  # 시간 설정값이 없으면
                cur.execute(
                    "INSERT INTO attcheckTBL(guildID, authorID, checkCnt, isChecked, authorName) VALUES('" + guildID + "', '" +
                    authorID + "', 1, 1, '" + authorName + "');")
                cur.execute(
                    "INSERT INTO attdateTBL(guildID, authorID, attDate) VALUES('" + guildID + "', '" + authorID + "', '" + nowDate + "');")
                conn.commit()
                conn.close()
                embed = discord.Embed(title="\U0001F4C5 첫 출석체크시군요!", description="출석체크 되었습니다.")
                await ctx.send(embed=embed)
            else:  # 시간 설정값이 있으면
                cur.execute(f"SELECT setTime FROM attsetTBL WHERE guildID={guildID};")
                while (True):
                    row = cur.fetchone()  # 한 행씩 추출
                    if row == None:
                        break
                    setTime = str(row[0])
                setHour, setMinute = int(setTime.split(":")[0]), int(setTime.split(":")[1])
                nowHour, nowMinute = int(now.strftime('%H')), int(now.strftime('%M'))
                calTime = (nowHour * 60 + nowMinute) - (setHour * 60 + setMinute)
                if 0 <= calTime <= 10:  # 정상출석
                    cur.execute(
                        "INSERT INTO attcheckTBL(guildID, authorID, checkCnt, isChecked, authorName) VALUES('" + guildID + "', '" +
                        authorID + "', 1, 1, '" + authorName + "');")
                    cur.execute(
                        "INSERT INTO attdateTBL(guildID, authorID, attDate) VALUES('" + guildID + "', '" + authorID + "', '" + nowDate + "');")
                    conn.commit()
                    conn.close()
                    embed = discord.Embed(title="\U0001F4C5 첫 출석체크시군요!", description="출석체크 되었습니다.")
                    await ctx.send(embed=embed)
                else:  # 지각
                    embed = discord.Embed(title=f"\U0001F4C5 출석시간을 지켜주세요.",
                                          description=f"출석시간은 {setHour}:{setMinute}입니다.")
                    await ctx.send(embed=embed)
        else:  # 데이터베이스에 값이 있고
            cur.execute(
                "SELECT isChecked FROM attcheckTBL WHERE guildId = '" + guildID + "' AND authorID = '" + authorID + "'")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                isChecked = row[0]

            if isChecked == 1:  # 이미 출석체크했으면
                embed = discord.Embed(title="\U0001F4C5 이미 출석체크 하셨습니다.", description="출석체크는 하루에 한 번만 가능합니다.")
                await ctx.send(embed=embed)
                return

            if timeChecked == 0:  # 시간설정이 안되어있으면
                cur.execute(
                    "UPDATE attcheckTBL set checkCnt = checkCnt + 1, isChecked = 1 WHERE guildID = '" + guildID + "' AND authorID = '" + authorID + "';")
                cur.execute(
                    "INSERT INTO attdateTBL(guildID, authorID, attDate) VALUES('" + guildID + "', '" + authorID + "', '" + nowDate + "');")
                conn.commit()
                conn.close()
                embed = discord.Embed(title="\U0001F4C5 출석체크 완료!", description=nowDate + " 출석!")
                embed.set_footer(text="'토리야 출석표'를 통해 출석일수를 확인할 수 있습니다.")
                await ctx.send(embed=embed)
            else:  # 시간설정이 되어있으면
                cur.execute(f"SELECT setTime FROM attsetTBL WHERE guildID={guildID};")
                while (True):
                    row = cur.fetchone()  # 한 행씩 추출
                    if row == None:
                        break
                    setTime = str(row[0])
                setHour, setMinute = int(setTime.split(":")[0]), int(setTime.split(":")[1])
                nowHour, nowMinute = int(now.strftime('%H')), int(now.strftime('%M'))
                calTime = (nowHour * 60 + nowMinute) - (setHour * 60 + setMinute)
                if 0 <= calTime <= 10:  # 정상출석
                    cur.execute(
                        "UPDATE attcheckTBL set checkCnt = checkCnt + 1, isChecked = 1 WHERE guildID = '" + guildID + "' AND authorID = '" + authorID + "';")
                    cur.execute(
                        "INSERT INTO attdateTBL(guildID, authorID, attDate) VALUES('" + guildID + "', '" + authorID + "', '" + nowDate + "');")
                    conn.commit()
                    conn.close()
                    embed = discord.Embed(title="\U0001F4C5 출석체크 완료!", description=nowDate + " 출석!")
                    embed.set_footer(text="'토리야 출석표'를 통해 출석일수를 확인할 수 있습니다.")
                    await ctx.send(embed=embed)
                else:  # 지각
                    embed = discord.Embed(title=f"\U0001F4C5 출석시간을 지켜주세요.",
                                          description=f"출석시간은 {setHour}:{setMinute}입니다.")
                    await ctx.send(embed=embed)

    @commands.command()
    async def 출석랭킹(self,ctx):
        await self.show_att_ranking(ctx.message)

    @commands.command()
    async def 출석표(self,ctx):
        setTime = None  # 수정
        guildID = str(ctx.guild.id)
        authorID = str(ctx.author.id)
        checkCnt = 0
        isChecked = 0
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month
        now = datetime.datetime.now()
        dayOfMonth = calendar.monthrange(year, month)[1]  # 이 달의 일 수 ex)1월 - 31일
        progressBar = ""
        text = calendar.TextCalendar()
        cal = text.formatmonth(year, month)
        cal = cal.replace(str(year), "")
        attDate = []  # 출석일

        try:
            conn = pymysql.connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT checkCnt, isChecked FROM attcheckTBL WHERE guildID ='" + guildID + "' AND authorID = '" + authorID + "';")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                checkCnt = row[0]
                isChecked = str(row[1])

            cur.execute(f"SELECT attDate FROM attdateTBL WHERE guildID ='{guildID}' AND authorID = '{authorID}';")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                attDate.append(str(row[0]))

            cur.execute(f"SELECT setTime FROM attsetTBL WHERE guildID = '{guildID}';")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                setTime = str(row[0])

            if setTime == None:  # 수정
                setTime = 'X   '
            for i in range(len(attDate)):  # 출석일을 찾아서 느낌표로 변경.
                attDay = attDate[i].split("-")[2]  # 2021-01-21 일 경우 맨 뒤의 21일만 저장.
                attDay = attDay.lstrip("0")

                if len(attDay) == 1:  # 1자리수
                    cal = cal.replace(attDay, "\U00002757", 1)  # 느낌표 이모지로 표시
                else:  # 1자리수이상
                    cal = cal.replace(attDay, " \U00002757", 1)
            cal = f"```{cal}```"
            check_per_month = round((checkCnt / dayOfMonth) * 100, 1)  # 출석률
            num_of_square = math.floor(check_per_month / 10)  # 검은 사각형 개수(출석 진행도)

            for i in range(num_of_square):
                progressBar += "\U0001F7E9"
            for i in range(10 - num_of_square):
                progressBar += "\U00002B1C"

            if isChecked == '0':  # 수정
                embed = discord.Embed(title="\U0001F4C5  출석표",
                                      description=f"오늘은 아직 출석체크를 안하셨네요? <@{authorID}>님의 이번 달 출석 횟수는 "
                                                  f"{str(checkCnt)}회 입니다.\n\n현재 서버의 출석시간은 {setTime[:-3]} 입니다.")
                embed.add_field(name="진행도", value=progressBar + " 출석률 " + str(check_per_month) + "%")
                await ctx.send(embed=embed)
                await ctx.send(f"{cal}\n출석일 = \U00002757, 현재 날짜 = {now.strftime('%Y-%m-%d')}")
            elif isChecked == '1':  # 수정
                embed = discord.Embed(title="\U0001F4C5  출석표",
                                      description=f"오늘도 출석체크 하셨네요. <@{authorID}>님의 이번 달 출석 횟수는 "
                                                  f"{str(checkCnt)}회 입니다.\n\n현재 서버의 출석시간은 {setTime[:-3]} 입니다.")
                embed.add_field(name="진행도", value=progressBar + " 출석률 " + str(check_per_month) + "%")
                await ctx.send(embed=embed)
                await ctx.send(f"{cal}\n출석일 = \U00002757, 현재 날짜 = {now.strftime('%Y-%m-%d')}")
            else:
                embed = discord.Embed(title="\U0001F4C5  아직 한 번도 출석하지 않으셨네요.", description="'토리야 출석체크' 를 입력해서 "
                                                                                           "출석체크 해주세요.")
                await ctx.send(embed=embed)
            conn.commit()
            conn.close()
        except:
            embed = discord.Embed(title="🚫 출석체크를 먼저 진행해주세요.", description="입력 방식  ➡  토리야 출석체크")
            await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(AttCheck(bot))