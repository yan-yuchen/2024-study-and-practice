import requests
import json
import csv
import random
import time
import WGS1984
import citybus
import conversion_geo
import os
import pandas as pd
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

def station(html, keywords, bus_station, buslines_information, buslines_polyline, city, station_frequency):
    buslines = html["buslines"]
    count = 0
    for i in buslines:
        count += 1
        busstops = i["busstops"]

        """站点信息"""
        for T in busstops:
            station_id = T["id"]
            if station_id in station_frequency:
                station_frequency[station_id] += 1
            else:
                station_frequency[station_id] = 1

            lng1, lat1 = T["location"].split(",")
            cell = [city, T["name"], WGS1984.main(lng1, lat1)[0], WGS1984.main(lng1, lat1)[1], station_id, i["name"],
                    count, station_frequency[station_id]]
            with open(bus_station, 'a', newline='', encoding='utf-8') as f:
                write = csv.writer(f)
                write.writerow(cell)

        """线路信息"""
        information = [city, count, keywords[0:4], i["name"], i["basic_price"], i["total_price"], i["distance"],
                       i["start_stop"], i["end_stop"], i["type"], i["start_time"], i["end_time"]]
        with open(buslines_information, 'a', newline='', encoding='utf-8') as f:
            write = csv.writer(f)
            write.writerow(information)

        """线路路线"""
        polyline = i["polyline"]
        split_polyline = polyline.split(";")
        cou = 0
        buslines_name2 = i["name"]
        for i in split_polyline:
            cou += 1
            excessive = i.split(",")
            bus_polyline = [city, cou, buslines_name2, keywords[0:4], WGS1984.main(excessive[0], excessive[1])[0],
                            WGS1984.main(excessive[0], excessive[1])[1]]
            with open(buslines_polyline, 'a', newline='', encoding='utf-8') as f:
                write = csv.writer(f)
                write.writerow(bus_polyline)

def research(city, keywords, key, bus_station, buslines_information, buslines_polyline, station_frequency):
    url = "https://restapi.amap.com/v3/bus/linename?parameters"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"}
    keyword = {"s": "rsv3", "extensions": "all", "key": key, 'jscode': jscode, "output": "json", "city": city, "offset": "2",
               "keywords": keywords, "platform": "JS"}
    a = requests.get(url, headers=headers, params=keyword)
    html = a.text
    data = json.loads(html)
    if data["status"] == "1":
        station(data, keywords, bus_station, buslines_information, buslines_polyline, city, station_frequency)
    else:
        print("未查询到{}市的{}信息".format(city, keywords))

def main(city, key, province):
    if not os.path.isdir(os.getcwd() + "/data"):
        os.mkdir(os.getcwd() + "/data")
    if not os.path.isdir(os.getcwd() + "/data/" + province):
        os.mkdir(os.getcwd() + "/data/" + province)
    now_path = os.getcwd() + "/data/" + province + "/csv/"
    if not os.path.isdir(now_path):
        os.mkdir(now_path)

    bus_station = now_path + city + "公交站点.csv"
    buslines_information = now_path + city + "公交线路信息.csv"
    buslines_polyline = now_path + city + "公交线路.csv"
    station_frequency = {}

    with open(bus_station, 'a', newline='', encoding='utf_8_sig') as f:
        write = csv.writer(f)
        write.writerow(["城市", "站点名称", "lng", "lat", "id", "线路名称", "正反线路", "线路频次"])

    with open(buslines_information, 'a', newline='', encoding='utf_8_sig') as f:
        write = csv.writer(f)
        write.writerow(["城市", "正反线路", "简称", "全称", "上车票价", "全程票价", "距离", "起点站", "终点站", "线路类型", "首班时间", "末班时间"])

    with open(buslines_polyline, 'a', newline='', encoding='utf_8_sig') as f:
        write = csv.writer(f)
        write.writerow(["城市", "序号", "全称", "简称", "lng", "lat"])

    citybus_name = citybus.main(city)

    print("【正在获取{}公交线路数据】\n".format(city))

    for i in tqdm(citybus_name):
        keywords = i["name"]
        research(city, keywords, key, bus_station, buslines_information, buslines_polyline, station_frequency)


    df = pd.read_csv(bus_station)
    df = df.groupby('站点名称').agg({
    'lng': 'first',  # 选择每个组的第一个lng值
    'lat': 'first',  # 选择每个组的第一个lat值
    '正反线路': 'first',  # 选择每个组的第一个正反线路值
    '线路名称': lambda x: ', '.join(x),  # 将线路名称用逗号连接起来
    '线路频次': 'sum'  # 对线路频次进行求和
    })
    df.reset_index(inplace=True)
    df.to_csv(now_path + city + "公交站点.csv", index=False, encoding='utf_8_sig')

    conversion_geo.main(bus_station, buslines_information, buslines_polyline, city, province)

key = '223b73f9c6529a7c9b5df21d98f51962' #您的高德key——注意：一定是申请web端
jscode = 'ff21e90565e73b1edee6e08e708641a8' #对应web端的秘钥
province = "黑龙江"
city = "哈尔滨" #不要带市、县

main(city, key, province)