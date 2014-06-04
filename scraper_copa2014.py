from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient
from pandas import DataFrame

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
        try:
            campos = p.split("~")
            jogo = {}
            time1 = campos[0].split("^")
            time2 = campos[1].split("^")
            jogo["time1"] = time1[0]
            jogo["time1_cod"] = time1[1]
            jogo["time2"] = time2[0]
            jogo["time2_cod"] = time2[1]
            gols = campos[3].split("^")
            jogo["gols_time1"] = gols[0]
            jogo["gols_time2"] = gols[1]
            jogo["hora"] = campos[5].replace(" HRS","")
            jogo["estadio"] = campos[6]
            jogo["codigo_partida"] = campos[8]
            jogo["data"] = campos[13]
            resultado.append(jogo)
        except:
            pass
    
    #adiciona ao banco de dados
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["partidas"]
    
    #retira as partidas antigas
    partidas_antigas = [c["codigo_partida"] for c in list(my_collection.find())]

    for r in resultado:
        if r["codigo_partida"] not in partidas_antigas:    
            my_collection.insert(r)
            print(r)
    

def infoTime():
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_team_7265.txt&timezone=ET&pad=y&callback=cb"
    page = BeautifulSoup(urlopen(url).read())
    campos = page.getText().split(";")
    for c in campos:
        print(c)

def guardaURLs():
    tecnicos = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_coaches.txt&timezone=ET&pad=y&callback=cb"
    escalacao_por_partida = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_formatn_2014053110801.txt&timezone=ET&pad=y&callback=cb"
    escalacao_completa_gols_cartoes = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_lineups_2014053110801.txt&timezone=ET&pad=y&callback=cb"
    gols_publico_juiz = "http://hosted.stats.com/ifb2009/data.asp?file=en/braz_score_2014053110801.txt&timezone=ET&pad=y&callback=cb"
    timeline = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_timeline_2012081111387.txt&timezone=ET&pad=y&callback=cb"
    chutes_gols_posicao = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_shotchrt_2012081111387.txt&timezone=ET&pad=y&callback=cb"
    
def atualizaPartidas():
    datas = ['20140501','20140506',	'20140511',	'20140516',	'20140521',	'20140526',
            '20140502',	'20140507',	'20140512',	'20140517',	'20140522',	'20140527',
            '20140503',	'20140508',	'20140513',	'20140518',	'20140523',	'20140528',
            '20140504',	'20140509',	'20140514',	'20140519',	'20140524',	'20140529',
            '20140505',	'20140510',	'20140515',	'20140520',	'20140525',	'20140530']
    for d in datas:
        partidasDia(d)

def eventosJogo(codigo):
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_shotchrt_"+codigo+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    #retira símbolos do final
    evento = str(page).split("&")[0]
    evento = evento.split("|")
    
    #retira simbolos do inicio
    evento[0] = evento[0].replace('cb({"data":"pbpEvents=',"")
    
    #separa os eventos
    resultado = []
    for e in evento:
        lance = {}
        campos = e.split("~")
        lance["time"] = campos[0]
        lance["evento"] = campos[1].split("^")[0]
        lance["local"] = campos[2]
        lance["camisa_jogador"] = campos[3]
        lance["minuto"] = campos[4]
        lance["jogador"] = campos[5]
        lance["num_evento"] = campos[7]
        resultado.append(lance)

    print(DataFrame(resultado))
    #keys = list(lance.keys())
    #f = open("eventos.csv", 'w')
    #dict_writer = csv.DictWriter(f, keys)
    #dict_writer.writer.writerow(keys)
    #dict_writer.writerows(resultado)
    
    
def consultaBase(base):
    #faz a consulta
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    items = list(my_collection.find())
    print(items)
    
    #exporta pro csv
    keys = list(items[0].keys())
    f = open(base+'.csv', 'w')
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(items)
 
eventosJogo("2012080412940")   
#consultaBase("partidas")
#mycollection.update({'_id':mongo_id}, {"$set": post})

