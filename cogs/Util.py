import asyncio #비동기 프로그래밍
import pickle #피클, 일종의 암호화 비스무리. SMTP 기능에서 비밀번호 숨기는 역할
import random
import discord #디스코드 기능
import smtplib #SMTP(메일 건의 송신기능)
from discord.utils import get
from email.mime.text import MIMEText #SMTP 이메일
from discord.ext import commands

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 도움말(self,ctx):
        # 답변 내용 구성
        embed = discord.Embed(title="사용 가능한 명령어는 다음과 같습니다.", color=0x4b280a)
        embed.set_author(name="토리봇")
        embed.add_field(name="⭐  기본", value="`토리야 제작자`,  `토리야 도움말`,  `토리야 문의`,  `토리야 가이드`,  \n`토리야 룰렛`, `토리야 사다리타기`, `토리야 역할부여`"
                                            ", `토리야 청소` ", inline=True)
        embed.add_field(name="😷  코로나 정보", value="`토리야 오늘확진자`", inline=False)
        embed.add_field(name="🔎  검색 정보", value="`토리야 오늘날씨`", inline=False)
        embed.add_field(name="📅  스케줄링 기능",
                        value="`토리야 일정표`,  `토리야 일정추가`,  \n`토리야 일정삭제`\n  `토리야 출석설정`, `토리야 출석체크`,\n `토리야 출석표`, `토리야 출석랭킹`,"
                              "\n `토리야 투표`, `토리야 찬반투표`, `토리야 약속장소`")
        embed.add_field(name="📖  스터디그룹 기능", value="`토리야 타이머추가`,  `토리야 타이머중지`,\n `토리야 타이머`\n`토리야 단어학습`, "
                                                   "`토리야 단어삭제`\n`토리야 단어장`, `토리야 단어문제`")
        embed.set_footer(text="Made By DotoriMuk#4593")
        await ctx.send(embed=embed)
        return None


    @commands.command()
    async def 제작자(self,ctx):
        msg = "Made By DotoriMuk#4593"
        await ctx.send(msg)
        return None

    @commands.command()#수정
    async def 가이드(self,ctx):
        text = "디스코드에 오신 것을 환영합니다.\n\n 디스코드는 카카오톡의 단톡방이라고 할 수 있는 서버가 있고, " \
               "각 서버는 \n채팅채널과 음성채널로 이루어져 있습니다. \n\n`#자료방` 과 같이 앞에 #이 붙은 채널은 채팅채널이고, " \
               "`\U0001F50A General` 과 같이 \n\U0001F50A 이 붙은 채널은 음성채널입니다. \n\n음성 채널에 입장한 후 `화면` 버튼을 클릭해서" \
               " 같은 음성채널에 있는 사람들에게 화면을 공유할 수 있습니다. 음성 세팅은 아래 그림을 참고해주세요.\n\n" \
               "토리 봇은 채팅 채널에서의 명령어 입력을 통해 작동합니다. `#toriBot` 채팅 채널에서 `토리야 도움말`을 입력해보세요."
        embed = discord.Embed(title="\U0001F4D6  디스코드 가이드!", description=text)
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File('./cogs/가이드.jpg'))

    @commands.command()
    async def 청소(self,ctx):
        channel = ctx.channel
        embed = discord.Embed(title="🧹  청소 [서버장 기능]",
                              description="청소할 메세지 갯수를 입력해주세요. ex) 10개\n'#취소' 입력시 취소.",
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
                if ctx.author.id != ctx.guild.owner_id:
                    embed = discord.Embed(title="🚫  청소 실패", description=ctx.author.name + "님은 서버장이 아닙니다.")
                    await ctx.send(embed=embed)
                    return
                else:
                    amount = msg2.content.split("개")[0]
                    amount = amount.strip()
                    try:
                        await ctx.channel.purge(limit=int(amount))
                        embed = discord.Embed(title="🧹  청소",
                                              description="서버장 " + ctx.author.name + "님에 의해 " + amount + " 개의 메세지가 삭제되었습니다.",
                                              color=0x00aaaa)
                        await ctx.send(embed=embed)
                    except discord.Forbidden:
                        embed = discord.Embed(title="🚫  청소실패",
                                              description=str(ctx.channel) + "에서의 권한이 부족합니다.\n '메세지 관리'권한을 부여해주세요.",
                                              color=0x00aaaa)
                        await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)10개")
                await ctx.send(embed=embed)
    @commands.command()
    async def 문의(self,ctx):
        channel = ctx.channel
        embed = discord.Embed(title="📪  문의, 건의 사항을 입력해주세요. 개발자에게 전송됩니다.", description="취소하시려면 #취소를 입력해주세요.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("시간초과")
        else:
            await msg.delete()
            sendText = str(msg2.content)  # 보낸 내용
            sendUser = ctx.author  # 보낸 유저

            if sendText == "#취소":
                embed = discord.Embed(title="🚫  문의전송이 취소되었습니다.")
                await ctx.send(embed=embed)
                return
            else:
                smtp = smtplib.SMTP('smtp.naver.com', 587)  # smtp url과 port

                smtp.ehlo()  # 서버와 handshaking
                smtp.starttls()  # TLS를 이용하여 암호화.
                pw = pickle.load(open('./cogs/pw.pickle', 'rb'))  # 유출방지를 위해 pickle 사용
                smtp.login('', pw)

                message = MIMEText(sendText)
                message['Subject'] = str(sendUser) + '님의 문의사항입니다.'  # 제목
                message['From'] = ''  # 보내는사람
                message['To'] = ''  # 받는사람

                smtp.sendmail('', '', message.as_string())

                smtp.quit()
                embed = discord.Embed(title="정상적으로 문의, 건의가 전송되었습니다.", description="내용=" + sendText)
                await ctx.send(embed=embed)
    @commands.command()
    async def 사다리타기(self,ctx):
        global bot
        embed = discord.Embed(title="사다리 타기", description="상단/하단 옵션을 입력해주세요. ex)토끼,거북이,호랑이/1,2,3\n"
                                                          "'#취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            try:
                await msg.delete()
                if msg2.content == '#취소':
                    embed = discord.Embed(title="🚫  취소되었습니다.")
                    await ctx.send(embed=embed)
                    return
                top = msg2.content.split("/")[0]
                bott = msg2.content.split("/")[1]
                topOption = top.split(",")
                botOption = bott.split(",")
                result = ""
                if len(topOption) != len(botOption):
                    await ctx.send("상단옵션과 하단옵션의 개수가 다릅니다.")
                    return
                else:
                    for i in range(len(topOption)):
                        topOption[i] = topOption[i].strip()
                        botOption[i] = botOption[i].strip()
                random.shuffle(botOption)
                embed = discord.Embed(title="\U0001FA9C 사다리타기 결과!")
                await ctx.send(embed=embed)
                for i in range(len(topOption)):
                    result += topOption[i] + '  \U000027A1  ' + botOption[i] + '\n'
                await ctx.send(result)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)토끼,거북이,호랑이"
                                                                         "/1,2,3")
                await ctx.send(embed=embed)
    @commands.command()
    async def 룰렛(self,ctx):
        embed = discord.Embed(title="🎰 룰렛 옵션의 개수와 룰렛의 옵션 내용을 입력합니다.", description="룰렛 옵션의 개수를 입력해주세요."
                                                                                   "'#취소'를 입력하면 취소됩니다.")
        msg = await ctx.send(embed=embed)

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
                option_num = int(msg2.content)
                embed = discord.Embed(title="🎰  룰렛의 옵션 내용을 ,(쉼표) 와 함께 입력해주세요.", description="ex)사과, 바나나, 포도")
                msg = await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫  잘못된 입력입니다.", description="숫자를 입력해주세요. ex) 5")
                await ctx.send(embed=embed)
                return

            try:
                msg3 = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send("입력 제한 시간 초과")
            else:
                await msg.delete()
                option = str(msg3.content)  # 룰렛의 옵션
                option_arr = option.split(",")

                if len(option_arr) != option_num:
                    embed = discord.Embed(title="🚫 입력하신 개수와 실제 옵션의 개수가 다릅니다.", description="ex)5 입력시 5개의 옵션 입력.")
                    await ctx.send(embed=embed)
                    return
                try:
                    for i in range(len(option_arr)):
                        option_arr[i] = option_arr[i].strip()  # 공백제거

                    idx_option = random.randint(0, option_num - 1)  # 랜덤으로 숫자 하나를 고름.
                    result = option_arr[idx_option]  # 그 숫자에 해당하는 옵션이 당첨.

                    embed = discord.Embed(title="🎰  룰렛 돌리는 중...")
                    embed.add_field(name=option_arr[0], value="과연 결과는...?")
                    msg = await ctx.send(embed=embed)
                    tmpNum = 0

                    for i in range(option_num * 3):  # 룰렛 돌리는거 비주얼 구현.
                        await asyncio.sleep(0.3)
                        if tmpNum == option_num - 1:
                            tmpNum = 0
                        else:
                            tmpNum = tmpNum + 1

                        embed2 = discord.Embed(title="🎰  룰렛 돌리는 중...")
                        embed2.add_field(name=option_arr[tmpNum], value="과연 결과는...?")
                        await msg.edit(embed=embed2)

                    for i in range(idx_option + 1):
                        await asyncio.sleep(0.8)
                        embed2 = discord.Embed(title="🎰  룰렛 돌리는 중...")
                        embed2.add_field(name=option_arr[i], value="과연 결과는...?")
                        await msg.edit(embed=embed2)

                    resultEmbed = discord.Embed(title="🎉  룰렛 결과", description="룰렛을 돌린 결과 " + result + "이(가) 당첨되었습니다.")
                    await msg.edit(embed=resultEmbed)
                except:
                    embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)사과, 바나나, 포도")
                    await ctx.send(embed=embed)

    @commands.command()
    async def 역할부여(self, ctx):
        check = 0
        embed = discord.Embed(title='\U0001F527  역할 부여', description='대상의 ID/부여할 역할 형식으로 입력해주세요.')
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            addrole = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")

        else:
            await msg.delete()
            msglist = addrole.content.split('/')
            target = msglist[0]
            giverole = msglist[1]

            get_role = get(ctx.message.guild.roles, name=giverole)
            if get_role is None:
                await ctx.message.guild.create_role(name=giverole)
                await ctx.send('\U0001F527	역할이 없습니다. 역할을 생성합니다.')
                check = 1

            get_role = get(ctx.message.guild.roles, name=giverole)
            get_target = get(ctx.message.guild.members, name=target)
            await get_target.add_roles(get_role)
            if check == 0:
                embed = discord.Embed(title='\U0001F527  역할 부여 성공', description= \
                    f'{ctx.message.author} 님이 {get_role} 역할을 {get_target} 님에게 적용했습니다.')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='\U0001F527  역할 부여 성공', description= \
                    f'{ctx.message.author} 님이 {get_role} 역할을 생성한 후 {get_target} 님에게 적용했습니다.')
                await ctx.send(embed=embed)
            check = 0

    @commands.command()
    async def 서버목록(self, ctx):
        server_cnt = 0  # 서버개수
        guild_list = self.bot.guilds
        if str(ctx.author.id) == '':
            for i in guild_list:  # 현재 봇이 들어가있는 서버 ID와 서버 이름 출력.
                server_cnt = server_cnt + 1
                await ctx.send(f"서버 이름:{i.name}\n")
            await ctx.send(f"{server_cnt}개의 서버에서 사용중.\n")
        else:
            return
def setup(bot):
    bot.add_cog(Util(bot))