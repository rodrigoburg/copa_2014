#TODO: calcular média dos jogadores
#TODO: calcular média das estatístias do time
#TODO: botar os campos do scraper_copa na ordem

import collections
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient
from pandas import DataFrame, pivot_table, merge,concat, Series
import numpy as np
from re import match
from datetime import date, datetime, timedelta as td

def consultaData(data):
    url = "http://pt.fifa.com/worldcup/matches/"
    page = BeautifulSoup(urlopen(url).read())
    
    #acha todos os links para cada dia
    dia = page.find("div",{"id":data})
    link = dia.findAll("a",{"class":"mu-m-link" })
    
    #para cada um dos dias
    for l in link:
        #acha o código
        codigo = find_between(l['href'],"match=","/")
        #se não tiver esse jogo na base:
        antigos = jogosAntigos()
        if codigo not in antigos:
            url = "http://pt.fifa.com"+l['href']
            url = url.replace("index","statistics")
            scrape_pagina(url)

def consultaJogo(codigo):
    url = "http://pt.fifa.com/worldcup/matches/round=255931/match="+codigo+"/statistics.html"
    scrape_pagina(url)

def scrape_pagina(url):
    print(url)
    #abre o link
    page = BeautifulSoup(urlopen(url).read())
    
    #monta estatísticas dos times
    jogo = collections.OrderedDict()
    jogo["01codigo"] = find_between(url,"match=","/")
    
    #acha os times
    div = page.find("div",{"class":"mh-m"})
    times = div.findChildren("span",{"class":"t-nText"})
    jogo["02time1"] = times[0].getText()
    jogo["03time2"] = times[1].getText()
    
    #resultados
    try: #vê se o jogo já começou
        resultado = div.findChild("span",{"class":"s-scoreText"})
        jogo["04gols1"] = resultado.getText().split("-")[0]
        jogo["05gols2"] = resultado.getText().split("-")[1]
    
        #ataques perigosos
        pai = page.find("tr",{"data-codeid":"4000045"})
        jogo["06ataque1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["07ataque2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #chutes a gol
        pai = page.find("tr",{"data-codeid":"5000036"})
        jogo["08chutes1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["09chutes2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #passe dentro da área
        pai = page.find("tr",{"data-codeid":"4000053"})
        jogo["10passes_area1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["11passes_area2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #desarmes
        pai = page.find("tr",{"data-codeid":"3000063"})
        jogo["12desarmes1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["13desarmes2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #passes completados
        pai = page.find("tr",{"data-codeid":"8000077"})
        jogo["14passes_completados1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["15passes_completados2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #posse de bola
        pai = page.find("div",{"class":"chart-container-donut-doubleside"})
        filho = pai.findChild("div",{"class":"chart-leftlabel"})
        jogo["16posse_bola1"] = filho.findChild("span").getText()
        filho = pai.findChild("div",{"class":"chart-rightlabel"})
        jogo["17posse_bola2"] = filho.findChild("span").getText()

        #chutes_certos
        pai = page.find("tr",{"data-codeid":"5000054"})
        jogo["18chutes_certos1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["19chutes_certos2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #chutes_bloqueados
        pai = page.find("tr",{"data-codeid":"5000059"})
        jogo["20chutes_bloqueados1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["21chutes_bloqueados2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #chutes_defendidos
        pai = page.find("tr",{"data-codeid":"5000058"})
        jogo["22chutes_defendidos1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["23chutes_defendidos2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #chutes_fora
        pai = page.find("tr",{"data-codeid":"5000055"})
        jogo["24chutes_fora1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["25chutes_fora2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #chutes_trave
        pai = page.find("tr",{"data-codeid":"5000076"})
        jogo["26chutes_trave1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["27chutes_trave2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #jogadas_bola_parada
        pai = page.find("tr",{"data-codeid":"5000072"})
        jogo["28bola_parada1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["29bola_parada2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #cruzamentos
        pai = page.find("tr",{"data-codeid":"8000136"})
        jogo["30cruzamentos1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["31cruzamentos2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #escanteios
        pai = page.find("tr",{"data-codeid":"8000072"})
        jogo["32escanteios1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["33escanteios2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #impedimentos
        pai = page.find("tr",{"data-codeid":"4000042"})
        jogo["34impedimentos1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["35impedimentos2"] = pai.findChild("td",{"data-statref":"away"}).getText()

        #defesas
        pai = page.find("tr",{"data-codeid":"3000105"})
        jogo["36defesas1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["37defesas2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #bolas recuperadas
        pai = page.find("tr",{"data-codeid":"2000103"})
        jogo["38bolas_recuperadas1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["39bolas_recuperadas2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #bolas perdidas
        pai = page.find("tr",{"data-codeid":"4000109"})
        jogo["40bolas_perdidas1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["41bolas_perdidas2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #carrinhos
        pai = page.find("tr",{"data-codeid":"3000111"})
        jogo["42carrinho1"] = pai.findChild("td",{"data-statref":"home"}).getText()
        jogo["43carrinho2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #faltas cometidas
        pai = page.find("div",{"class":"chart-container-donut-doubleside","data-exception":"disciplinary"})
        filho = pai.findChild("div",{"class":"chart-leftlabel"})
        jogo["44faltas_cometidas1"] = filho.findChild("span").getText()
        filho = pai.findChild("div",{"class":"chart-rightlabel"})
        jogo["45faltas_cometidas2"] = filho.findChild("span").getText()
    
        #cartões amarelos
        try:
            pai = page.find("tr",{"data-codename":"yellowcard"})
            jogo["46cartao_amarelo1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["47cartao_amarelo2"] = pai.findChild("td",{"data-statref":"away"}).getText()
        except AttributeError:
            pai = page.find("tr",{"data-codeid":"2000097"})
            jogo["46cartao_amarelo1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["47cartao_amarelo2"] = pai.findChild("td",{"data-statref":"away"}).getText()
        
        #cartões vermelhos
        try:
            pai = page.find("tr",{"data-codename":"redcard"})
            jogo["48cartao_vermelho1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["49cartao_vermelho2"] = pai.findChild("td",{"data-statref":"away"}).getText()
        except AttributeError:
            pai = page.find("tr",{"data-codeid":"2000098"})
            jogo["48cartao_vermelho1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["49cartao_vermelho2"] = pai.findChild("td",{"data-statref":"away"}).getText()
    
        #distância time casa
        pai = page.find("div",{"id":"distance"})
        filho = pai.findChild("div",{"class":"stats home"})
        espirito_santo = filho.findAll("li")
        try: #resolve se tiver mudança no método de dar essa info
            jogo["50dist_total1"] = int(find_between(str(espirito_santo[0]),"span>","m").strip())
            jogo["51dist_com_bola1"] =int(find_between(str(espirito_santo[1]),"span>","m").strip())
            jogo["52dist_sem_bola1"] = int(find_between(str(espirito_santo[2]),"span>","m").strip())
        except ValueError:
            espirito_santo = filho.findAll("span",{"data-statref":"home"})
            jogo["50dist_total1"] = int(espirito_santo[0].getText())
            jogo["51dist_com_bola1"] = int(espirito_santo[1].getText())
            jogo["52dist_sem_bola1"] = int(espirito_santo[2].getText())
        
        #distância time fora
        pai = page.find("div",{"id":"distance"})
        filho = pai.findChild("div",{"class":"stats away"})
        espirito_santo = filho.findAll("li")
        
        try: #resolve se tiver mudança no método de dar essa info
            jogo["53dist_total2"] = int(find_between(str(espirito_santo[0]),"span>","m").strip())
            jogo["54dist_com_bola2"] =int(find_between(str(espirito_santo[1]),"span>","m").strip())
            jogo["55dist_sem_bola2"] = int(find_between(str(espirito_santo[2]),"span>","m").strip())
        except ValueError:
            espirito_santo = filho.findAll("span",{"data-statref":"away"})
            jogo["53dist_total2"] = int(espirito_santo[0].getText())
            jogo["54dist_com_bola2"] = int(espirito_santo[1].getText())
            jogo["55dist_sem_bola2"] = int(espirito_santo[2].getText())
        
        #passes time casa
        pai = page.find("div",{"id":"passes"})
        filho = pai.findChild("table",{"class":"chart-leftSide"})
        espiritos_santos = filho.findChildren("tr")
        tds = espiritos_santos[0].findChildren("td")
        passes = []
        for t in tds:
            if is_int(t.getText()):
                passes.append(int(t.getText()))
        jogo["56passes1"] = sum(passes)
        jogo["57passes_curtos1"] = passes[0]
        jogo["58passes_medios1"] = passes[1]
        jogo["59passes_longos1"] = passes[2]
    
        #passes time fora
        filho = pai.findChild("table",{"class":"chart-rightSide"})
        espiritos_santos = filho.findChildren("tr")
        tds = espiritos_santos[0].findChildren("td")
        passes = []
        for t in tds:
            if is_int(t.getText()):
                passes.append(int(t.getText()))
        jogo["60passes2"] = sum(passes)
        jogo["61passes_curtos2"] = passes[0]
        jogo["62passes_medios2"] = passes[1]
        jogo["63passes_longos2"] = passes[2]
    
        #porcentagem de passes completos
        passe1 = page.find("div",{"class":"passes-perc-home"}).getText()
        passe2 = page.find("div",{"class":"passes-perc-away"}).getText()
        #retira o símbolo de %
        jogo["64porc_passes_completos1"] = passe1[0:len(passe1)-1]
        jogo["65porc_passes_completos2"] = passe2[0:len(passe2)-1]
        
        #transforma tudo em número
        for j in jogo:
            if ("time" not in j):
                jogo[j] = int(jogo[j])
        
        #adiciona jogo na base
        client = MongoClient()
        my_db = client["copa"]
        my_collection = my_db["jogos_fifa"]
        my_collection.insert(jogo)
        print("Inserido na base: "+jogo["02time1"]+" x "+jogo["03time2"])
    
    except IndexError: #se o jogo não tiver começado
        pass
    
    #agora, montamos as estatísticas dos jogadores
    plantel = []
    
    #para os do time1
    pai = page.find("select",{"id":"playerlineup-home"})
    filhos = pai.findChildren("option")
    for f in filhos:
        if f.getText() != "Formação tática":
            jogador = {}
            jogador["03time"] = jogo["02time1"]
            jogador["01nome"] = f.getText()
            jogador["02codigo"] = f['value']
            infos = page.find("table",{"data-idplayer":jogador["02codigo"]})
            campos = [c.findChild("span").getText() for c in infos.findChildren("tr")]
            jogador["04chutes"] = campos[0]
            jogador["05passes_completados"] = campos[1]
            jogador["06bolas_recuperadas"] = campos[2]
            jogador["07desarmes"] = campos[3]
            jogador["08defesas"] = campos[4]
            jogador["09velocidade_maxima"] = campos[5]
            jogador["10distancia"] = campos[6]
            jogador["11adversario"] = jogo["03time2"]
            plantel.append(jogador)

    #para os do time2
    pai = page.find("select",{"id":"playerlineup-away"})
    filhos = pai.findChildren("option")
    for f in filhos:
        if f.getText() != "Formação tática":
            jogador = {}
            jogador["03time"] = jogo["03time2"]
            jogador["01nome"] = f.getText()
            jogador["02codigo"] = f['value']
            infos = page.find("table",{"data-idplayer":jogador["02codigo"]})
            campos = [c.findChild("span").getText() for c in infos.findChildren("tr")]
            jogador["04chutes"] = campos[0]
            jogador["05passes_completados"] = campos[1]
            jogador["06bolas_recuperadas"] = campos[2]
            jogador["07desarmes"] = campos[3]
            jogador["08defesas"] = campos[4]
            jogador["09velocidade_maxima"] = campos[5]
            jogador["10distancia"] = campos[6]
            jogador["11adversario"] = jogo["02time1"]
            plantel.append(jogador)
    
    my_collection = my_db["jogadores_fifa"]
    for jogador in plantel:
        my_collection.insert(jogador)

def jogosAntigos():
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["jogos_fifa"]
    antigos = my_collection.find()
    return [a["01codigo"] for a in antigos]
    
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def consultaBase(base):
    #faz a consulta
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    items = list(my_collection.find())
    final = DataFrame(items)

    #tira o campo id
    del final["_id"]
    
    #tira os dois digitos
    nomes = list(final.columns)
    nomes_fim = [n[2:] for n in nomes]
    final.columns = nomes_fim
    return final

def calculaTime(base):
    eventos = consultaBase("jogos_fifa")

    colunas = list(eventos.columns)
    #retira o código do jogo
    colunas.pop(0) 
    #cria o nome das colunas e dataframes para cada um dos times
    colunas1 = [campo for campo in colunas if campo[-1] == "1"]
    colunas2 = [campo for campo in colunas if campo[-1] == "2"]
    eventos1 = eventos[colunas1]
    eventos2 = eventos[colunas2]
    
    #retira o nome do time do nome das colunas
    colunas1.pop(0)
    colunas2.pop(0)
    
    #calcula a tabela dinâmica e junta as duas
    resultado1 = pivot_table(eventos1, values=colunas1, rows="time1", aggfunc="sum")
    resultado2 = pivot_table(eventos2, values=colunas2, rows="time2", aggfunc="sum")
    resultado = resultado1.append(resultado2)
    
    #acha o número de jogos
    resultado1_jogos = pivot_table(eventos1, values="gols1", rows="time1", aggfunc="count")
    resultado2_jogos = pivot_table(eventos2, values="gols2", rows="time2", aggfunc="count")
    jogos = DataFrame(resultado1_jogos.append(resultado2_jogos))
    jogos.columns = ["num_jogos"]

    #tira NAs
    resultado = resultado.fillna(0)
    
    #junta colunas
    colunas = resultado.columns
    novas_colunas = set([c[0:len(c)-1] for c in colunas])
    for c in novas_colunas:
        resultado[c] = resultado[c+"1"] + resultado[c+"2"]
        del resultado[c+"1"]
        del resultado[c+"2"]

    #junta número de jogos
    final = resultado.join(jogos)
    
    return final

def limpaBase(base):
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    my_collection.remove()

def limpaBases():
    limpaBase("jogos_fifa")
    limpaBase("jogadores_fifa")

def fazCalculos():
    consultaBase("jogadores_fifa").to_csv("jogadores.csv")
    consultaBase("jogos_fifa").to_csv("jogos.csv")
    calculaTime("jogos_fifa").to_csv("times.csv")

limpaBases()
consultaData("20140612")
consultaData("20140613")
fazCalculos()
#consultaBase("jogos_fifa").to_csv("teste_fifa.csv",index=False)
#consultaBase("jogadores_fifa").to_csv("teste_fifa.csv")