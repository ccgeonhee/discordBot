import asyncio #비동기 프로그래밍
import math
import pymysql #mysql 데이터베이스
import discord #디스코드 기능
from discord.ext import commands
class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def showTimer(self,message):  # 등록되어있는 타이머 출력.
        channel = message.channel
        channelID = str(message.channel.id)
        authorID = str(message.author.id)
        existChecked = 0
        conn = pymysql.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS (SELECT * FROM timerTBL WHERE channelID = '" + channelID + "' AND authorID= '" + authorID + "') as success;")
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            existChecked = row[0]

        if existChecked == 0:
            embed = discord.Embed(title="⏰  등록된 타이머가 없습니다.", description="'토리야 타이머추가'를 입력해서 타이머를 추가해주세요.")
            await channel.send(embed=embed)
            conn.commit()
            conn.close()
        else:
            cur.execute(
                "SELECT * FROM timerTBL WHERE channelID = '" + channelID + "' AND authorID = '" + authorID + "';")
            i = 1
            embed = discord.Embed(title="⏰  " + str(message.author) + " 님이 등록한 타이머")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                originTimer = row[1]
                timer = row[2]
                id = row[4]
                progress = int(originTimer) - int(timer)  # 진행 시간
                per_progress = round(progress / int(originTimer) * 100)  # 진행률
                num_of_square = math.floor(per_progress / 10)  # 사각형 개수
                progress_bar = ""
                for j in range(num_of_square):
                    progress_bar += "\U0001F7E9"
                for j in range(10 - num_of_square):
                    progress_bar += "\U00002B1C"

                embed.add_field(name=str(i) + "번째 타이머 (id= `" + str(id) + "`)",
                                value="남은 시간 = `" + str(timer) + "분` \n" + progress_bar, inline=False)
                # await channel.send("<@" + authorID + ">님이 등록한 " + str(i) + "번째 타이머는 `" + str(timer) + " 분` 남았습니다.")
                i += 1
            await channel.send(embed=embed)
            conn.commit()
            conn.close()

    @commands.command()
    async def 타이머추가(self,ctx):
        channel = ctx.channel
        channelID = str(ctx.channel.id)
        authorID = str(ctx.author.id)
        embed = discord.Embed(title="타이머 시간을 분 단위로 입력해주세요(최소 1분).\tex)180분\n'#취소'를 입력하면 취소됩니다.")
        msg = await  ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await msg.delete()
            if msg2.content == '#취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            try:
                setTime = msg2.content.split("분")[0]
                setTime = setTime.strip()
                conn = pymysql.connect()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO timerTBL (channelID, originTimer, timer, authorID) VALUES('" + channelID + "', '" +
                    setTime + "', '" + setTime + "', '" + authorID + "');")
                conn.commit()
                conn.close()
                embed = discord.Embed(title="타이머가 시작됩니다.", description="시간 = " + str(setTime) + "분")
                embed.set_footer(text="30분마다 남은시간을 알려드릴게요!")
                # 30분마다 알림오게해야함. 남은시간 공지.
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)180분")
                await ctx.send(embed=embed)

    @commands.command()
    async def 타이머(self,ctx):
        try:
            await self.showTimer(ctx.message)
        except:
            embed = discord.Embed(title="🚫 등록된 타이머가 없습니다.", description="토리야 타이머추가")
            await ctx.send(embed=embed)

    @commands.command()
    async def 타이머중지(self,ctx):
        channelID = str(ctx.channel.id)
        await self.showTimer(ctx.message)
        embed = discord.Embed(title="중지할 타이머의 id를 입력해주세요.", description="ex)타이머의 id가 7일 경우 7 입력.\n"
                                                                        "'#취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            id = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await msg.delete()
            if id.content == '#취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            conn = pymysql.connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT EXISTS (SELECT * FROM timerTBL WHERE channelID = '" + channelID + "' AND num= '" + id.content + "') as success;")
            while (True):
                row = cur.fetchone()  # 한 행씩 추출
                if row == None:
                    break
                existChecked = row[0]

            if existChecked == 0:
                embed = discord.Embed(title="잘못된 id 값입니다.")
                await ctx.send(embed=embed)
                conn.commit()
                conn.close()
            else:
                cur.execute(
                    "DELETE FROM timerTBL WHERE channelID = '" + str(
                        ctx.channel.id) + "' AND num = " + id.content + ";")
                embed = discord.Embed(title="\U000023F0 타이머가 정상적으로 삭제되었습니다.")
                conn.commit()
                conn.close()
                await ctx.send(embed=embed)
                await self.showTimer(ctx.message)
def setup(bot):
    bot.add_cog(Timer(bot))