from urllib import request
from bs4 import BeautifulSoup
from urllib.request import Request

# def rank_str(ign):
#     URL = str('https://na.op.gg/summoner/userName=' + ign.replace(' ', ''))
#     hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
#     req = Request(URL, headers=hdr)
#     html = request.urlopen(req)
#     soup = BeautifulSoup(html, 'lxml')
#     rank_find = soup.find_all('div', class_='tier')
#     rank_str = rank_find[0].text
#     if rank_str == "\n\t\t\tUnranked\n\t\t":
#         rank_str = rank_str.strip('\n\t')
#     return rank_str

# def osu(ign):
#     URL = str('https://osu.ppy.sh/users/' + ign.replace(' ', ''))
#     hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
#     req = Request(URL, headers=hdr)
#     html = request.urlopen(req)
#     soup = BeautifulSoup(html, 'lxml')
#     rank_find = soup.find_all('div', class_='value-display__value')
#     rank_str = rank_find[0].text
#     # if rank_str == "\n\t\t\tUnranked\n\t\t":
#     #     rank_str = rank_str.strip('\n\t')
#     return rank_str

def osu():
    URL = str('https://osu.ppy.sh/users/12687897')
    hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    req = Request(URL, headers=hdr)
    html = request.urlopen(req)
    soup = BeautifulSoup(html, 'lxml')
    rank_find = soup.find_all('div', class_='value-display__value')
    # rank_str = rank_find[0].text
    # if rank_str == "\n\t\t\tUnranked\n\t\t":
    #     rank_str = rank_str.strip('\n\t')
    return rank_find


def main():
    # player_ing = input("Enter the player's main account ign: ")
    # rank_string = osu(player_ing)
    print(osu())


main()