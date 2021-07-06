import asyncio #비동기 프로그래밍
import re
import pymysql #mysql 데이터베이스
import discord #디스코드 기능
from pymysql import IntegrityError
import json
import urllib.request
import datetime
from discord.ext import commands

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dateCheck(self,date):
        dateArr = date.split('.')
        if len(dateArr[0]) == 2:  # Year
            dateArr[0] = "20" + dateArr[0]
        else:
            pass
        if len(dateArr[1]) == 1:  # Month
            dateArr[1] = "0" + dateArr[1]
        else:
            pass
        if len(dateArr[2]) == 1:  # Day
            dateArr[2] = "0" + dateArr[2]
        else:
            pass
        rtrDate = '-'.join(dateArr)  # Date 형태로 변환
        return rtrDate
    async def show_DB(self,message):
        now = datetime.datetime.now()
        channel = message.channel
        guildID = str(message.guild)
        conn = pymysql.connect()
        cur = conn.cursor()
        author = []
        toDo = []
        deadline = []
        cur.execute("SELECT * FROM scheduleTBL WHERE guildID ='" + guildID + "';")
        while (True):
            row = cur.fetchone()  # 한 행씩 추출
            if row == None:
                break
            author.append(row[2])
            toDo.append(row[4])
            deadline.append(str(row[5]))
        embed = discord.Embed(title="\U00002611 " + guildID + "의 일정입니다.")
        for i in range(len(author)):
            dl = datetime.datetime.strptime(deadline[i], "%Y-%m-%d")
            remain = dl - now
            embed.add_field(name=toDo[i], value=f"맡은사람: `{author[i]}`\n마감기한: `{deadline[i]}`\n남은기간: `{remain.days} 일`",
                            inline=False)
        await channel.send(embed=embed)
        conn.commit()
        conn.close()

    @commands.command()  # 수정
    async def 일정추가(self,ctx):
        channelID = str(ctx.channel.id)
        guildID = str(ctx.guild)
        embed = discord.Embed(title="📆  날짜(년.월.일),할 일 [필수]/ @지정대상닉네임 [선택]",
                              description="ex)20.7.24, 생일/@DotoriMuk\n'#취소'를 입력하면 취소됩니다.")
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
                conn = pymysql.connect()
                cur = conn.cursor()

                date = re.split(r',|/', msg2.content)[0]
                date = date.strip()
                date = await self.dateCheck(date)
                toDo = re.split(r',|/', msg2.content)[1]
                toDo = toDo.strip()
                if len(re.split(r',|/', msg2.content)) == 3:  # 수행대상 입력시
                    target = re.split(r',|/', msg2.content)[2]
                    authorID = re.findall("\d+", target)[0]
                    user = self.bot.get_user(int(authorID))
                    if user == None:
                        embed = discord.Embed(title="🚫  지정대상이 존재하지않습니다.")
                        await ctx.send(embed=embed)
                        return
                    else:
                        authorName = user.name
                        cur.execute(
                            "INSERT INTO scheduleTBL VALUES('" + guildID + "', '" + channelID + "', '" + authorName + "', '" + authorID + "', '" + toDo + "', '" + date + "')")
                        conn.commit()
                        conn.close()
                elif len(re.split(r',|/', msg2.content)) == 2:  # 수행대상 미 입력시
                    authorName = str(ctx.author)
                    authorID = str(ctx.author.id)
                    cur.execute(
                        "INSERT INTO scheduleTBL VALUES('" + guildID + "', '" + channelID + "', '" + authorName + "', '" + authorID + "', '" + toDo + "', '" + date + "')")
                    conn.commit()
                    conn.close()
                else:
                    return
                embed = discord.Embed(title="📆  일정이 추가되었습니다.",
                                      description=f"일정 이름: `{toDo}`\n일정 기한: `{date}`\n맡은 사람: `{authorName}`")
                await ctx.send(embed=embed)
            except IntegrityError as e:
                embed = discord.Embed(title="🚫 잘못된 입력입니다. 중복된 이름 불가.")
                await ctx.send(embed=embed)
                await self.show_DB(ctx.message)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다. 중복된 이름 불가.",
                                      description="옳은 입력 방식  ➡  년.월.일, 일정이름\tex)20.7.24, 생일")
                await ctx.send(embed=embed)

    @commands.command()
    async def 일정표(self,ctx):
        await self.show_DB(ctx.message)

    @commands.command()
    async def 일정삭제(self,ctx):
        channel = ctx.channel
        await self.show_DB(ctx.message)
        msg = await ctx.send("📝  삭제할 일정 이름을 입력해주세요. '#취소'를 입력하면 취소됩니다.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            scName = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("입력 제한 시간 초과")
        else:
            await msg.delete()
            if scName.content == '#취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            conn = pymysql.connect()
            cur = conn.cursor()
            guildID = str(ctx.guild)

            cur.execute(
                "SELECT EXISTS (SELECT * FROM scheduleTBL WHERE guildID = '" + guildID + "' AND scheduleName='" + scName.content + "') as success;")
            while (True):
                row = cur.fetchone()  # 한 행씩 추출
                if row == None:
                    break
                existChecked = row[0]

            if existChecked == 0:  # 데이터베이스에 값이 없으면
                embed = discord.Embed(title="🚫 존재하지않는 일정입니다.")
                await ctx.send(embed=embed)
            else:
                cur.execute(
                    "DELETE FROM scheduleTBL WHERE guildID='" + guildID + "' AND scheduleName='" + scName.content + "';")
                conn.commit()
                conn.close()
                await ctx.send('일정이 삭제되었습니다.')
                await self.show_DB(ctx.message)
    @commands.command()
    async def 약속장소(self, ctx):
        list_of_lat = []
        list_of_lon = []
        embed = discord.Embed(title="🗺  여러 지점의 중간지점을 구해드립니다.",
                              description="지점의 개수를 먼저 입력해주세요. ex) 3 지점의 중간지점이 궁금할 경우 - 3\n"
                                          "취소는 '@취소' 입력.")
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
            if msg2.content == '@취소':
                embed = discord.Embed(title="🚫  취소되었습니다.")
                await ctx.send(embed=embed)
                return
            try:
                cnt = 0
                num_of_point = int(msg2.content)
                while(cnt < num_of_point):
                    embed = discord.Embed(title=f"🗺  총 {num_of_point}개 지점의 주소를 입력합니다.",
                                          description=f"{cnt + 1} 번째 지점의 주소를 입력해주세요.")
                    msg = await ctx.send(embed=embed)
                    try:
                        point = await self.bot.wait_for("message", timeout=40.0, check=check)
                        await msg.delete()
                        user = self.search_map(point.content)
                        user = json.loads(user)
                        user = user['addresses'][0]
                        list_of_lat.append(float(user['y']))
                        list_of_lon.append(float(user['x']))
                        cnt += 1
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send("입력 제한 시간 초과")
                        return
                    except:
                        embed = discord.Embed(title="🚫 잘못된 입력입니다. 다시 시도해주세요.",
                                              description="옳은 입력 방식  ➡  ex) 서울특별시 금천구 독산로 53")
                        await ctx.send(embed=embed)
                        return
                middle_of_lat = float(sum(list_of_lat)/num_of_point)
                middle_of_lon = float(sum(list_of_lon)/num_of_point)

                address = self.search_address(middle_of_lat,middle_of_lon)
                address = json.loads(address)
                address = address['results'][1]
                address = address['region']
                result_address = ""
                len_add = len(address)
                i = 1
                while(i < len_add ):
                    name = address[f"area{i}"]
                    result_address += name['name'] + " "
                    i+= 1
                url = f"http://maps.google.com/?q={middle_of_lat},{middle_of_lon}&z=15"
                embed = discord.Embed(title=f"🗺     {num_of_point} 지점의 중간지점",
                                      description=f"중간 지점은 {result_address}입니다.\n\n 추가 정보 : {url}")

                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.",
                                      description="옳은 입력 방식  ➡  ex) 3 지점의 중간지점이 궁금할 경우 - 3")
                await ctx.send(embed=embed)
    def search_address(self, lat, lon):
        client_id = 'id'  # 클라이언트 ID값
        client_secret = 'secret'  # 클라이언트 Secret값
        url = f"https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc?request=coordsToaddr&coords={lon},{lat}&sourcecrs=epsg:4326&output=json&orders=addr,admcode,roadaddr"
        request = urllib.request.Request(url)
        request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
        request.add_header('X-NCP-APIGW-API-KEY', client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            return response_body.decode('utf-8')
        else:
            print("Error Code:" + rescode)
    def search_map(self, search_text):
        client_id = 'id'  # 클라이언트 ID값
        client_secret = 'secret'  # 클라이언트 Secret값
        encText = urllib.parse.quote(search_text)
        url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query=' + encText
        request = urllib.request.Request(url)
        request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
        request.add_header('X-NCP-APIGW-API-KEY', client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            return response_body.decode('utf-8')
        else:
            print("Error Code:" + rescode)
def setup(bot):
    bot.add_cog(Schedule(bot))