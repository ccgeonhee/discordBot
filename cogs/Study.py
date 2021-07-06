import asyncio #비동기 프로그래밍
import re
import json
import discord #디스코드 기능
import random#수정
from discord.ext import commands

class Study(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # 수정
    async def 단어학습(self,ctx):
        guildID = ctx.guild.id
        path = "./cogs/vocaList.json"
        embed = discord.Embed(title="\U0001F4BE	  단어 학습",
                              description="단어와 뜻이 적힌 메모장 파일을 전송해주세요.\n\n양식: 원문[키보드 Tab]뜻[키보드 Enter]"
                                          "\n\nex) 단어장.txt\n\nTest\t\t테스트\nApple\t\t사과\n\n'#취소'를 입력하면 취소됩니다.",
                              color=0x00aaaa)
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("시간초과")
            await msg.delete()
        else:
            await msg.delete()
            if msg2.content != "#취소" and not msg2.attachments:
                embed = discord.Embed(title="🚫  입력 오류", description="첨부 파일을 입력해주세요.")
                await ctx.send(embed=embed)
            elif msg2.content == "#취소":
                await msg2.delete()
                return
            else:
                bytes = await msg2.attachments[0].read()
                bytes = bytes.decode()
                bytes = re.split(r"\t|\n", bytes)
                await msg2.delete()
                if len(bytes) % 2 == 1:  # 홀수개 입력되었다면
                    embed = discord.Embed(title="🚫  입력 오류", description="txt 파일의 단어와 뜻의 개수가 다릅니다.")
                    await ctx.send(embed=embed)
                    return
                else:
                    with open(path, 'r') as outfile:
                        json_data = json.load(outfile)
                    arr = {}
                    for i in range(0, len(bytes), 2):
                        arr[bytes[i]] = bytes[i + 1]

                    if str(guildID) in json_data:  # 기존 json 데이터에 있으면.
                        dic = json_data.get(str(guildID))
                        dic.update(arr)
                    else:  # 기존 json 데이터에 없으면
                        json_data[guildID] = arr
                        print(json_data)

                    with open(path, 'w') as outfile:
                        json.dump(json_data, outfile, indent=4)
                    embed = discord.Embed(title="\U00002611	단어 저장 완료!", description="`토리야 단어장`을 통해 확인할 수 있습니다.")
                    await ctx.send(embed=embed)

    @commands.command()  # 수정
    async def 단어장(self,ctx):
        guildID = ctx.guild.id
        path = "./cogs/vocaList.json"
        txt = ""
        with open(path, "r") as json_file:
            json_data = json.load(json_file)

        if str(guildID) in json_data:  # 기존 json 데이터에 있으면.
            dic = json_data.get(str(guildID))
            for word, mean in dic.items():
                txt += f"{word}\t\t:\t\t{mean}\n\n"

            embed = discord.Embed(title="\U0001F4D5  단어장", description=txt)
            await ctx.send(embed=embed)
        else:  # 기존 json 데이터에 없으면
            embed = discord.Embed(title="🚫 입력된 단어가 없습니다.", description="먼저 `토리야 단어학습`을 통해 입력해주세요.")
            await ctx.send(embed=embed)

    @commands.command()  # 수정
    async def 단어삭제(self,ctx):
        guildID = ctx.guild.id
        path = "./cogs/vocaList.json"
        embed = discord.Embed(title="삭제할 단어[왼쪽]를 ,(쉼표)로 구분하여 입력해주세요.", description="ex) test : 테스트 일 경우 test 입력."
                                                                                   "모두 삭제할 경우 '#모두삭제' 입력\n'#취소'입력시 취소.")
        msg = await ctx.send(embed=embed)
        await self.단어장(ctx)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await msg.delete()
            with open(path, 'r') as outfile:
                json_data = json.load(outfile)
            dic = json_data.get(str(guildID))

            if msg2.content == "#모두삭제":
                dic.clear()
            elif msg2.content == "#취소":
                await msg2.delete()
                return
            else:
                deleteWord = msg2.content.split(",")
                for i in range(len(deleteWord)):
                    deleteWord[i] = deleteWord[i].strip()
                    if deleteWord[i] in dic:
                        del dic[deleteWord[i]]
                    else:
                        await ctx.send(f"'{deleteWord[i]}' 라는 단어는 존재하지 않습니다.")

            with open(path, 'w') as outfile:
                json.dump(json_data, outfile, indent=4)
            embed = discord.Embed(title="\U00002611  정상적으로 삭제되었습니다!")
            await ctx.send(embed=embed)
            await self.단어장(ctx)

    @commands.command()  # 수정
    async def 단어문제(self,ctx):
        guildID = ctx.guild.id
        path = "./cogs/vocaList.json"
        txt = ""
        with open(path, "r") as json_file:
            json_data = json.load(json_file)

        if str(guildID) not in json_data:  # 기존 json 데이터에 없으면.
            embed = discord.Embed(title="🚫 입력된 단어가 없습니다.", description="먼저 `토리야 학습`을 통해 입력해주세요.")
            await ctx.send(embed=embed)
        else:  # 기존 json 데이터에 있으면
            dic = json_data.get(str(guildID))  # 단어장 저장
            embed = discord.Embed(title="\U0001F4D5 저장된 단어/뜻 중 한가지만 보여드립니다.", description="'단어', '뜻', '랜덤' 중 한가지를 입력해주세요.")
            msg = await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg2 = await self.bot.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("시간초과")
            else:
                await msg.delete()
                if msg2.content == "단어":
                    for word in dic:
                        txt += f"{word}\t\t= \n\n"
                    embed = discord.Embed(title="\U0001F4D5  단어장", description=txt)
                    await ctx.send(embed=embed)
                elif msg2.content == "뜻":
                    for mean in dic.values():
                        txt += f"\t\t=\t\t{mean}\n\n"
                    embed = discord.Embed(title="\U0001F4D5  단어장", description=txt)
                    await ctx.send(embed=embed)
                elif msg2.content == "랜덤":#수정
                    for i in range(len(dic)):
                        word = list(dic.keys())
                        mean = list(dic.values())
                        ran = random.choice([True, False])
                        if ran == True:#단어
                            txt += f"{word[i]}\t\t= \n\n"
                        elif ran == False:#뜻
                            txt += f"\t\t=\t\t{mean[i]}\n\n"
                    embed = discord.Embed(title="\U0001F4D5  단어장", description=txt)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="단어와 뜻 중 하나를 입력해주세요.")
                    await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Study(bot))