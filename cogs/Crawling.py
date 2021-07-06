import asyncio #비동기 프로그래밍
import discord #디스코드 기능
import requests #크롤링
import os
from urllib.request import urlopen #크롤링(url open)
from bs4 import BeautifulSoup #크롤링(BeautifulSoup)
from urllib.error import URLError, HTTPError #크롤링(url 접근에러 처리)
from discord.ext import commands

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}  # 유저 에이전트정보, url접근

W_Color = int(0xFFFF00)  # 날씨에 따른 색깔 변화
T_Color = int(0xFFFF00)  # 온도에 따른 색깔 변화

Sunny = False
Rainy = False
Cloudy = False
Snowy = False

Rise = False  # 기온상승
Drop = False  # 기온하락

class Crawling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def split_data(self,data, arr):  # 크롤링한 데이터를 나눔.
        global Sunny, Rainy, Cloudy, Snowy, Drop, Rise
        if arr == 0:
            if data == "맑음":
                Sunny = True
            elif data == "비":
                Rainy = True
            elif data == "구름많음":
                Cloudy = True
            elif data == "눈":
                Snowy = True
            else:
                print("모든 날씨 해당하지 않음. 코드 수정 필요")
                return
        if arr == 1:
            if data[-3:] == "낮아요":
                Drop = True
                print(data[-3:])
            elif data[-3:] == "높아요":
                Rise = True
                print(data[-3:])
            else:
                print("모든 온도 해당하지 않음. 코드 수정 필요")
                return
            
    async def showGraph(self,message):
        try:
            await message.channel.send(file=discord.File('./cogs/savefig.png'))
            print("출력성공.")
            path = os.getcwd()
            file_list = os.listdir(path)
            print("file list: {}".format(file_list))
        except:
            print("출력불가.")
            path = os.getcwd()
            file_list = os.listdir(path)
            print("file list: {}".format(file_list))
            
    @commands.command()
    async def 오늘확진자(self,ctx):
        #global bot
        embed = discord.Embed(title="🌍  지역을 입력해주세요.", color=0x4b280a)
        embed.add_field(name="지역", value="`합계`, `서울`, `부산`, `대구`, `인천`, `광주`, `대전`, `울산`, "
                                         "`세종`, `경기`, `강원`, `충북`, `충남`, `전북`, `전남`, `경북`, `경남`, `제주`, `검역`")

        msg = await ctx.send("지역을 입력해주시면 진행됩니다.", embed=embed)

        def check(m):  # 유저의 다음 입력을 받고 체크하는 함수.
            return m.author == ctx.author and m.channel == ctx.channel

        try:  # 유저의 다음 입력을 받음.
            msg2 = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("시간초과")
        else:
            await msg.delete()  # 입력을 받으면 이전 메세지를 삭제
            try:
                html = urlopen("http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13")
                bsObject = BeautifulSoup(html, "html.parser")
                all_data = bsObject.find('div', 'data_table midd mgt24')

                place_name = all_data.find_all('th')
                place_data = all_data.find_all('td')
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

                daily_covid = {}  # 딕셔너리
                for i in range(len(place_name_list)):
                    daily_covid[place_name_list[i]] = place_data_list[i]  # 장소이름이랑 데이터 맵핑해서 딕셔너리에 넣음.

                key = str(msg2.content)  # 딕셔너리의 키
                if key in daily_covid:
                    data = daily_covid.get(key)  # 키와 대응되는 value 값을 구함.
                    if key == "합계":
                        send_msg = "😷  오늘의 합계 확진자 수는 " + data + "명 입니다."
                        embed = discord.Embed(title=send_msg,
                                              description="출처: 보건복지부 COVID-19\n(http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13)",
                                              color=0x4b280a)
                    else:
                        send_msg = "😷  " + key + "의 오늘 확진자 수는 " + data + "명 입니다."
                        embed = discord.Embed(title=send_msg,
                                              description="출처: 보건복지부 COVID-19\n(http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13)",
                                              color=0x4b280a)
                    await ctx.send(embed=embed)
                    await self.showGraph(ctx.message)
                else:
                    embed = discord.Embed(title="🚫 잘못된 입력입니다.",
                                          description="옳은 입력 방식  ➡  ex)" + ','.join(place_name_list))
                    await ctx.send(embed=embed)
                return
            except HTTPError as e:
                embed = discord.Embed(title="🚫 현재 점검으로 인해 사이트를 이용할 수 없습니다. 다음에 이용해주세요.")
                await ctx.send(embed=embed)

    # @commands.command()
    # async def 실시간검색어(self,ctx):
    #     url = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
    #     # User 설정
    #     try:
    #         res = requests.get(url, headers=headers)
    #     # res.content 주의
    #     except HTTPError as e:
    #         embed = discord.Embed(title="🚫 현재 점검으로 인해 사이트를 이용할 수 없습니다. 다음에 이용해주세요.")
    #         await ctx.send(embed=embed)
    #     else:
    #         soup = BeautifulSoup(res.content, 'html.parser')
    #         # span.item_title 정보를 선택
    #         data = soup.select('span.item_title')
    #         # for 문으로 출력해준다.
    #         embed = discord.Embed(title='📈  네이버 실시간 검색어', description='현재 실시간 검색어입니다.', color=0x54ea74)
    #         i = 0
    #         txt = "바로가기"
    #         search_url = "https://search.naver.com/search.naver?where=nexearch&query="
    #         for item in data:
    #             embed.add_field(name=str(i + 1) + '.\t' + item.get_text(), value='[%s](<%s>)' %
    #                                                                              (txt,
    #                                                                               search_url + item.get_text().replace(
    #                                                                                   " ",
    #                                                                                   "+")),
    #                             inline=False)
    #             i += 1
    #         await ctx.send(embed=embed)
    #
    # @commands.command()
    # async def 게임할인(self,ctx):
    #     channel = ctx.channel
    #     site = "http://itcm.co.kr/index.php?mid=game_news&category=1070"
    #     try:
    #         res = requests.get(site, headers=headers)
    #     except HTTPError as e:
    #         embed = discord.Embed(title="🚫 현재 점검으로 인해 사이트를 이용할 수 없습니다. 다음에 이용해주세요.")
    #         await ctx.send(embed=embed)
    #     else:
    #         soup = BeautifulSoup(res.content, "html.parser")
    #         tbody = soup.find("table", {"class": "bd_lst bd_tb_lst bd_tb"})  # table에서 해당 class를 찾음.
    #
    #         a = tbody.select('tr > td > a')  # tr>td>a 를 찾음.
    #         href_data = []
    #         title_data = []
    #         num = 0
    #         for i in a:
    #             if num % 2 == 1:
    #                 href_data.append(
    #                     'http://itcm.co.kr/index.php?mid=game_news&category=1070' + str(i.get('href')))  # 링크 데이터
    #                 title_data.append(i.get('title'))  # 제목 데이터.
    #             num += 1
    #
    #         num = 0
    #         embed = discord.Embed(title='📃  게임 할인 목록', description='진행 기간은 링크 참조\n 출처: ITCM(http://itcm.co.kr/)')
    #         for item in range(len(href_data)):
    #             print(title_data[num])
    #             embed.add_field(name=str(num + 1) + '. ' + title_data[num], value=href_data[num], inline=False)
    #             num += 1
    #         await ctx.send(embed=embed)

    @commands.command()
    async def 오늘날씨(self,ctx):
        global bot
        channel = ctx.channel
        embed = discord.Embed(title='지역을 입력해주세요.', description='ex)서울특별시 강동구, 경기도 안양시...', color=0x4b280a)
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg2 = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("시간초과")
        else:
            await msg.delete()
            try:
                key = str(msg2.content)
                search_key = key.replace(' ', '+')  # 검색을위해 공백을 '+'로 변환.
                site = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=" + search_key + "날씨"  # 네이버검색
                res = requests.get(site, headers=headers)
                soup = BeautifulSoup(res.content, "html.parser")
                total_data = soup.find('div', {'class': 'weather_box'})  # 날씨 정보를 갖고있는 weather_box
                temp = total_data.find('span', {'class': 'todaytemp'}).text + total_data.find('span',
                                                                                              {
                                                                                                  'class': 'tempmark'}).text[
                                                                              2:]  # 온도
                WeatherCast = total_data.find('p', {'class': 'cast_txt'}).text  # WeatherCast
                MorningTemp = total_data.find('span', {'class': 'min'}).text  # 오전온도
                AfternoonTemp = total_data.find('span', {'class': 'max'}).text  # 오후온도
                FeelTemp = total_data.find('span', {'class': 'sensible'}).text[5:]  # 체감온도
                # TodayUV = total_data.find('span', {'class': 'indicator'}).text[4:-2] + " " + total_data.find('span', {#자외선
                #    'class': 'indicator'}).text[-2:]
                sub_data = total_data.find_all('dd')
                dust = sub_data[0].find('span', {'class': 'num'}).text  # 미세먼지
                ultra_dust = sub_data[1].find('span', {'class': 'num'}).text  # 초미세먼지
                ozone = sub_data[2].find('span', {'class': 'num'}).text  # 오존농도

                W_data = WeatherCast.split(',')[0]  # 날씨 정보
                T_data = WeatherCast.split(',')[1]  # 온도 정보

                await self.split_data(W_data, 0)  # 맑음, 비, 구름많음, 눈 구분
                await self.split_data(T_data, 1)  # 낮아요, 높아요 구분

                if Rise:
                    T_Color = 0xFF0000
                    print(T_Color)
                elif Drop:
                    T_Color = 0x0033FF
                    print(T_Color)
                else:
                    T_Color = 0xFFFFFF

                txt = "네이버 날씨"
                embed = discord.Embed(title=WeatherCast, color=T_Color)
                print(T_Color)
                embed.set_author(name='\U00002601  ' + key + '의 날씨')
                embed.add_field(name='\U0001F321  오전 날씨', value=MorningTemp, inline=True)
                embed.add_field(name='\U0001F321  오후 날씨', value=AfternoonTemp, inline=True)
                embed.add_field(name='\U0001F321  현재 기온', value=temp, inline=True)
                embed.add_field(name='.', value='.', inline=True)
                embed.add_field(name='.', value='.', inline=True)
                embed.add_field(name='\U0001F321  체감 날씨', value=FeelTemp, inline=True)
                embed.add_field(name='\U0001F32B  미세먼지', value=dust, inline=True)
                embed.add_field(name='\U0001F32B  초미세먼지', value=ultra_dust, inline=True)
                embed.add_field(name='\U00002600  오존', value=ozone, inline=True)
                # embed.add_field(name='자외선 지수', value=TodayUV, inline=False)
                embed.add_field(name='출처', value='[%s](<%s>)' % (txt, site))

                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="🚫 잘못된 입력입니다.", description="옳은 입력 방식  ➡  ex)서울특별시 강동구, 경기도 안양시...")
                await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Crawling(bot))
