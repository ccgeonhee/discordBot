import asyncio #비동기 프로그래밍
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
        cur.execute(f"SELECT EXISTS (SELECT * FROM timerTBL WHERE channelID = '{channelID}' AND authorID= '{authorID}') as success;")
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
            cur.execute(f"SELECT time, num FROM timerTBL WHERE channelID = '{channelID}' AND authorID = '{authorID}';")
            embed = discord.Embed(title=f"⏰ {message.author} 님이 등록한 타이머")
            i = 1
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                Origin_Time = row[0]
                Msg_Id = row[1]

                embed.add_field(name=f"{i}번째 타이머 (id= {Msg_Id})", value= f"등록시간 = {Origin_Time}분 \n", inline=False)
                i += 1
            msg = await channel.send(embed=embed)
            conn.commit()
            conn.close()
            return msg

    @commands.command()
    async def 타이머추가(self, ctx):
        channelID = str(ctx.channel.id)
        authorID = str(ctx.author.id)
        msgid = ctx.message.id
        User_Command = await ctx.fetch_message(int(msgid))
        conn = pymysql.connect()
        cur = conn.cursor()
        embed = discord.Embed(title="\U000023F0 시간을 입력해주세요", description="분 단위로 입력해주세요\nex)180분")
        embed.set_footer(text="'@취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            Time_Msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await msg.delete()
            await Time_Msg.delete()
            await User_Command.delete()
            if Time_Msg.content == "@취소":
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            Origin_Time = Time_Msg.content.split("분")[0]
            Origin_Time = Origin_Time.strip()
            if Origin_Time.isdigit() == False:
                embed = discord.Embed(title="🚫  정상적인 입력 값이 아닙니다. 숫자를 입력해주세요.ex)180분")
                await ctx.send(embed=embed)
                return
            else:
                Origin_Time = int(Origin_Time)

            embed = discord.Embed(title=f"\U000023F0 {Origin_Time}분 타이머", description=f"남은 시간 = {Origin_Time} 분")
            Timer_Msg = await ctx.send(embed=embed)
            msgID = Timer_Msg.id
            cur.execute(f"INSERT INTO timerTBL(channelID, authorID, timerID, time) "
                        f"VALUES('{channelID}', '{authorID}', '{msgID}', {Origin_Time})")
            conn.commit()
            Current_Time = Origin_Time
            for i in range(Origin_Time):
                await asyncio.sleep(60)
                Current_Time -= 1
                if Current_Time == 0:
                    Delete_Msg = await ctx.fetch_message(Timer_Msg.id)
                    await Delete_Msg.delete()
                    embed = discord.Embed(title=f"\U000023F0 {Origin_Time}분 타이머 종료", description="타이머가 종료되었습니다.")
                    await ctx.send(embed=embed)
                    cur.execute(f"DELETE FROM timerTBL WHERE timerID = '{Timer_Msg.id}';")
                    conn.commit()
                    conn.close()
                else:
                    try:
                        embed = discord.Embed(title=f"\U000023F0 {Origin_Time}분 타이머", description=f"남은 시간 = {Current_Time} 분")
                        await Timer_Msg.edit(embed=embed)
                    except discord.errors.NotFound:
                        return
    @commands.command()
    async def 타이머(self, ctx):#토리야 타이머
        try:
            await self.showTimer(ctx.message)
        except:
            embed = discord.Embed(title="🚫 등록된 타이머가 없습니다.", description="토리야 타이머추가를 통해 추가해주세요.")
            await ctx.send(embed=embed)

    @commands.command()
    async def 타이머중지(self, ctx):#토리야 타이머중지
        channelID = str(ctx.channel.id)
        authorID = str(ctx.author.id)
        Timer_Msg = await self.showTimer(ctx.message)
        embed = discord.Embed(title="\U000023F0 중지할 타이머의 id를 입력해주세요.", description="ex)타이머의 id가 7일 경우 7 입력.\n")
        embed.set_footer(text="'@취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            Db_Id = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await Timer_Msg.delete()
            await msg.delete()
            if Db_Id.content == '@취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            if Db_Id.content.isdigit() == False:
                embed = discord.Embed(title="🚫  타이머의 id 숫자값을 입력해주세요.")
                await ctx.send(embed=embed)
                return
            conn = pymysql.connect()
            cur = conn.cursor()
            cur.execute(f"SELECT EXISTS (SELECT * FROM timerTBL WHERE channelID = '{channelID}' AND authorID = '{authorID}' AND num = {int(Db_Id.content)}) as success;")
            while (True):
                row = cur.fetchone()  # 한 행씩 추출
                if row == None:
                    break
                existChecked = row[0]

            if existChecked == 0:
                embed = discord.Embed(title="잘못된 id 값입니다!")
                await ctx.send(embed=embed)
                conn.commit()
                conn.close()
            else:
                cur.execute(f"SELECT timerID FROM timerTBL WHERE channelID = '{channelID}' AND authorID = '{authorID}';")
                while (True):
                    row = cur.fetchone()
                    if row == None:
                        break
                    Msg_Id = row[0]
                cur.execute(f"DELETE FROM timerTBL WHERE channelID = '{channelID}'AND authorID = '{authorID}'AND "
                            f"num = '{int(Db_Id.content)}';")
                embed = discord.Embed(title="\U000023F0 타이머가 정상적으로 삭제되었습니다.")
                Delete_Msg = await ctx.fetch_message(int(Msg_Id))
                await Delete_Msg.delete()
                conn.commit()
                conn.close()
                await ctx.send(embed=embed)
                await self.showTimer(ctx.message)

def setup(bot):
    bot.add_cog(Timer(bot))
