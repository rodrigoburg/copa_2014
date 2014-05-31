from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient


def partidasDia(dia):
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_results_"+dia+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    #separa cada partida
    partidas = str(page).split("|")
    
    #retira simbolos do inicio e do final
    partidas[0] = partidas[0].replace("matches=","")
    partidas[len(partidas)-1] = partidas[len(partidas)-1].replace("&amp;updte;=no&amp;Endstr;=End","")
    
    #separa os campos de cada partida
    resultado = []

    #monta o resultado final
    for p in partidas:
        campos = p.split("~")
        jogo = {}
        time1 = campos[0].split("^")
        time2 = campos[1].split("^")
        jogo["time1"] = time1[0]
        jogo["time1_cod"] = time1[1]
        jogo["time2"] = time2[0]
        jogo["time2_cod"] = time2[1]
        jogo["placar"] = campos[3]
        jogo["hora"] = campos[5].replace(" HRS","")
        jogo["estadio"] = campos[6]
        jogo["codigo_partida"] = campos[8]
        jogo["data"] = campos[13]
        resultado.append(jogo)
    
    return resultado


#partidasDia("20140521")
 
client = MongoClient()

print(client.database_names())
    