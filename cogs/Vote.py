import asyncio #비동기 프로그래밍
import pymysql #mysql 데이터베이스
import discord #디스코드 기능
import re
import math
from discord.ext import commands

voteArray = []

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction, user):
        if user.bot or reaction.message.id not in voteArray:
            return
        conn = pymysql.connect()
        cur = conn.cursor()
        if reaction.emoji == '👍':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, pros, cons, num, voteItem) VALUES \
            ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},'','',1,0,'','');")
            conn.commit()
            conn.close()
        elif reaction.emoji == '👎':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, pros, cons, num, voteItem) VALUES \
            ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id}, '','',0,1,'','');")
            conn.commit()
            conn.close()
        elif reaction.emoji == '☑':
            authorID = ''
            voteName = ''
            pros = cons = 0
            cur.execute(f"SELECT authorID FROM voteTBL WHERE voteID = {reaction.message.id};")
            while (True):  # 투표제작자 ID를 구함.
                row = cur.fetchone()  # 한 행씩 추출
                if row == None:
                    break
                if row[0] != '':
                    authorID = row[0]

            if str(user.id) != str(authorID):
                return

            cur.execute(f"SELECT voteName FROM voteTBL WHERE voteID = {reaction.message.id};")  # 투표이름 구함
            while (True):
                row = cur.fetchone()  # 한 행씩 추출
                if row == None:
                    break
                if row[0] != '':
                    voteName = row[0]

            cur.execute(f"SELECT SUM(pros), SUM(cons) FROM voteTBL WHERE voteID={reaction.message.id}")
            row = cur.fetchone()
            while (True):
                if row == None:
                    break
                pros += row[0]
                cons += row[1]
                row = cur.fetchone()

            if pros > cons:
                embed = discord.Embed(title=f"\U00002714	'{voteName}' 투표가 종료되었습니다.", description="결과는 찬성!")
                embed.add_field(name="\U00002B55	찬성", value=f"{pros} 표", inline=True)
                embed.add_field(name="\U0000274C	반대", value=f"{cons} 표", inline=True)
                await reaction.message.channel.send(embed=embed)
            elif pros < cons:
                embed = discord.Embed(title=f"\U00002714'{voteName}' 투표가 종료되었습니다.", description="결과는 반대!")
                embed.add_field(name="\U00002B55	찬성", value=f"{pros} 표", inline=True)
                embed.add_field(name="\U0000274C	반대", value=f"{cons} 표", inline=True)
                await reaction.message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title=f"\U00002714'{voteName}' 투표가 종료되었습니다.", description="결과는 무효!")
                embed.add_field(name="\U00002B55	찬성", value=f"{pros} 표", inline=True)
                embed.add_field(name="\U0000274C	반대", value=f"{cons} 표", inline=True)
                await reaction.message.channel.send(embed=embed)

            voteArray.remove(reaction.message.id)
            cur.execute(f"DELETE FROM voteTBL WHERE voteID = {reaction.message.id};")
            conn.commit()
            conn.close()
        elif reaction.emoji == '1️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                num) \
                VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                '','', 1);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '2️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 2);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '3️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 3);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '4️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 4);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '5️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 5);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '6️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 6);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '7️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 7);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '8️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 8);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '9️⃣':
            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, \
                            num) \
                            VALUES ('{reaction.message.channel.id}','{user.name}','{user.id}',{reaction.message.id},\
                            '','', 9);")
            conn.commit()
            conn.close()
        elif reaction.emoji == '✅':
            voteNum = [0 for i in range(9)]
            authorID = ''
            voteName = ''
            itemlist = [0 for i in range(9)]
            voteItem = ""
            voteItemArr = []
            progressBar = ""
            sum_of_num = 0
            i = 0
            cur.execute(f"SELECT authorID FROM voteTBL WHERE voteID = {reaction.message.id};")
            while 1:
                row = cur.fetchone()
                if row == None:
                    break
                if row[0] != '':
                    authorID = row[0]

            if str(user.id) != str(authorID):
                print("아이디가 다름")
                print(user.id, authorID)
                return

            cur.execute(f"SELECT voteName FROM voteTBL WHERE voteID = {reaction.message.id};")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                if row[0] != '':
                    voteName = str(row[0])

            cur.execute(f"SELECT num FROM voteTBL WHERE voteID={reaction.message.id};")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                if row[0] != None:
                    voteNum[int(row[0]) - 1] += 1

            cur.execute(f"SELECT voteItem FROM voteTBL WHERE voteID={reaction.message.id};")
            while (True):
                row = cur.fetchone()
                if row == None:
                    break
                if row[0] != None:
                    voteItem = str(row[0])

            voteItemArr = voteItem.split(",")
            voteItemArr.pop()

            for i in range(len(voteNum)):
                sum_of_num += int(voteNum[i])

            embed = discord.Embed(title=f"\U00002714	'{voteName}' 투표가 종료되었습니다.", description="투표 결과")
            for i in range(len(voteItemArr)):
                vote_per_sum = round((voteNum[i] / sum_of_num) * 100, 1)
                num_of_square = math.floor(vote_per_sum / 10)
                for j in range(num_of_square):
                    progressBar += "\U0001F7E9"
                for j in range(10 - num_of_square):
                    progressBar += "\U00002B1C"
                embed.add_field(name=f"{i+1}. {voteItemArr[i]}    [{voteNum[i]} 표]", value=f"{progressBar} {vote_per_sum}%", inline=False)
                progressBar = ""
            await reaction.message.channel.send(embed=embed)
            voteArray.remove(reaction.message.id)
            cur.execute(f"DELETE FROM voteTBL WHERE voteID = {reaction.message.id};")
            conn.commit()
            conn.close()

    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction, user):
        if user.bot or reaction.message.id not in voteArray:
            return

        conn = pymysql.connect()
        cur = conn.cursor()
        if reaction.emoji == '👍':
            cur.execute(
                f"DELETE FROM voteTBL WHERE pros = '1' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '👎':
            cur.execute(
                f"DELETE FROM voteTBL WHERE cons = '1' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '1️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '1' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '2️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '2' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '3️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '3' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '4️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '4' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '5️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '5' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '6️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '6' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '7️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '7' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '8️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '8' AND userID = {user.id} AND voteID = '{reaction.message.id}'")
        elif reaction.emoji == '9️⃣':
            cur.execute(
                f"DELETE FROM voteTBL WHERE num = '9' AND userID = {user.id} AND voteID = '{reaction.message.id}'")

        conn.commit()
        conn.close()

    @commands.command()
    async def 찬반투표(self,ctx):
        conn = pymysql.connect()
        cur = conn.cursor()

        embed = discord.Embed(title='\U00002694     이지선다 투표', description="투표 제목을 입력해주세요. '#취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과 - 투표가 종료되었습니다")
        else:
            await msg.delete()
            if title.content == "#취소":
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            embed2 = discord.Embed(title=f"\U0001F4D1	{title.content}",
                                   description='👍 = 찬성,    👎 = 반대,     ☑ = 투표 종료',
                                   color=0x4b280a)
            embed2.set_footer(text="투표 종료는 투표 요청자만 가능합니다.")
            global msg2
            msg2 = await ctx.send(embed=embed2)
            await msg2.add_reaction('👍')
            await msg2.add_reaction('👎')
            await msg2.add_reaction('☑')

            voteArray.append(msg2.id)

            cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, pros, cons, num, voteItem) VALUES"
                        f"('{ctx.channel.id}','{ctx.author.name}','{ctx.author.id}','{msg2.id}', '{title.content}', '{ctx.author.id}',0,0,'','')")
            conn.commit()
            conn.close()

    @commands.command()
    async def 투표(self, ctx):
        conn = pymysql.connect()
        cur = conn.cursor()
        emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        voteItem = ""
        emoji = iter(emoji_list)  # next 사용하기 위함
        num = ''

        embed = discord.Embed(title='\U00002694     복수응답 투표',
                              description="투표제목/ 항목1,항목2... 형식으로 입력해주세요\n\n'#취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과 - 투표가 종료되었습니다")
        else:
            await msg.delete()
            if title.content == "#취소":
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return

            msglist =re.split(r"/|,", title.content)

            if len(msglist) > 11:
                embed = discord.Embed(title="투표 선택지는 9개까지만 가능합니다.")
                await ctx.send(embed=embed)
                return

            try:
                msg_iterlist = iter(msglist)
                embed = discord.Embed(title=msglist[0], color=0x4b280a)

                next(msg_iterlist)
                for n in range(1, len(msglist)):
                    num += f'{next(emoji)} {next(msg_iterlist)}\n'  # emoji_list에서 값을 하나씩 꺼냄
                    voteItem += f"{str(msglist[n])},"

                embed.add_field(name=num, value='투표중입니다. ✅를 누르면 투표가 종료됩니다.')
                global votemsg
                votemsg = await ctx.send(embed=embed)
                for i in range(len(msglist) - 1):  # 제목때문에 -1, '/'은 msglist에 포함 안 됨
                    await votemsg.add_reaction(emoji_list[i])
                await votemsg.add_reaction('✅')

                voteArray.append(votemsg.id)

                cur.execute(f"INSERT INTO voteTBL(guildID, userName, userID, voteID, voteName, authorID, voteItem) "
                            f"VALUES ('{ctx.channel.id}','{ctx.author.name}','{ctx.author.id}','{votemsg.id}', '{msglist[0]}', '{ctx.author.id}'"
                            f", '{voteItem}');")  # title.content -> msglist[0].content ??
                conn.commit()
                conn.close()
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="ex)오늘 놀러갈곳/잠실,홍대,건대")
                await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Vote(bot))