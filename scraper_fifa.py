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
from urllib.request import Request

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

def consultaJogo(codigo,segunda_fase):
    if segunda_fase:
        url = "http://pt.fifa.com/worldcup/matches/round=255955/match="+codigo+"/statistics.html"        
    else:
        url = "http://pt.fifa.com/worldcup/matches/round=255955/match=300186490/statistics.html"
        
    scrape_pagina(url)

def scrape_pagina(url):
    print(url)
    headers = {'User-Agent':'Mozilla/5.0'}
    req = Request(url,headers=headers)
    
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["jogos_fifa"]
    
    #abre o link
    page = BeautifulSoup(urlopen(req).read())
    
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
        try: 
            jogo["42carrinho1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["43carrinho2"] = pai.findChild("td",{"data-statref":"away"}).getText()
        except:
            jogo["42carrinho1"] = 0
            jogo["43carrinho2"] = 0
    
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
            pai = page.find("tr",{"data-codeid":"2000098"})
            jogo["48cartao_vermelho1"] = pai.findChild("td",{"data-statref":"home"}).getText()
            jogo["49cartao_vermelho2"] = pai.findChild("td",{"data-statref":"away"}).getText()
        except AttributeError:
            jogo["48cartao_vermelho1"] = 0
            jogo["49cartao_vermelho2"] = 0
    
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

def arrumaTime(row):
    if row['time1'] != 0:
        return row["time1"]
    else:
        return row["time2"]

def calculaTime():
    eventos = consultaBase("jogos_fifa")
    
    #arruma vitórias, empates e derrotas
    eventos["vitorias1"] = eventos.apply(lambda row:1 if row["gols1"] > row["gols2"] else 0,axis=1)
    eventos["vitorias2"] = eventos.apply(lambda row:1 if row["gols2"] > row["gols1"] else 0,axis=1)

    eventos["empates1"] = eventos.apply(lambda row:1 if row["gols1"] == row["gols2"] else 0,axis=1)
    eventos["empates2"] = eventos.apply(lambda row:1 if row["gols1"] == row["gols2"] else 0,axis=1)
    
    eventos["derrotas1"] = eventos.apply(lambda row:1 if row["gols1"] < row["gols2"] else 0,axis=1)
    eventos["derrotas2"] = eventos.apply(lambda row:1 if row["gols2"] < row["gols1"] else 0,axis=1)
    
    #arruma gols contra
    
    eventos["gols_sofridos1"] = eventos["gols2"]
    eventos["gols_sofridos2"] = eventos["gols1"]
    
    colunas = list(eventos.columns)
    #retira o código do jogo
    colunas.pop(0) 
    #cria o nome das colunas e dataframes para cada um dos times
    colunas1 = [campo for campo in colunas if campo[-1] == "1"]
    colunas2 = [campo for campo in colunas if campo[-1] == "2"]
    eventos1 = eventos[colunas1]
    eventos2 = eventos[colunas2]

    #faz uma tabela só com uma das colunas - cada linha continua sendo um jogo
    resultado = eventos1.append(eventos2)
    resultado = resultado.fillna(0)
    
    #arruma o nome do time
    resultado["time"] = resultado.apply(arrumaTime,axis=1)
    del resultado["time1"]
    del resultado["time2"]    

    #calcula a soma de todos os indicadores
    colunas = [c[:-1] for c in colunas1] #tira o 1 dos nomes de coluna
    colunas.pop(0) #tira o nome dos times
    
    for c in colunas:
        resultado[c] = resultado[c+"1"] + resultado[c+"2"]
        del resultado[c+"1"]
        del resultado[c+"2"]
        
    #agora com a tabela pronta (cada linha um time), calculamos as tabelas dinamicas
    saida = resultado.groupby("time").sum()

    #acha o número de jogos
    conta_vezes = resultado.groupby("time").count()
    jogos = conta_vezes[[1]]
    jogos.columns = ["jogos"]
    saida = saida.join(jogos)

    return saida

def calculaJogador():
    eventos = consultaBase("jogadores_fifa")
    del eventos["adversario"]
    del eventos["velocidade_maxima"]
    
    #transforma tudo em inteiro
    colunas = list(eventos.columns)
    #retira os três nomes de texto
    colunas.pop(0)
    colunas.pop(0)
    colunas.pop(0)
    for c in colunas:
        eventos[c] = eventos[c].apply(float)

    resultado = eventos.groupby("nome").sum()
    
    #acha o numero de jogos
    conta_vezes = eventos.groupby("nome").count()
    jogos = conta_vezes[[1]]
    jogos.columns = ["jogos"]
    resultado = resultado.join(jogos)
    
    #adiciona o nome dos times
    eventos = eventos.set_index("nome")
    resultado = resultado.join(eventos["time"])

    return resultado

def calculaGrafico(times):
    
    #cria novas colunas
    times["pontos"] = 3*times["vitorias"] + 1*times["empates"]
    times["saldo_gols"] = times["gols"] - times["gols_sofridos"]
    
    #calcula as médias
    for column in times:
        if column not in ["vitorias","empates","derrotas","jogos","pontos","saldo_gols","gols","gols_sofridos"]:
            times[column] = times[column]/times["jogos"]
            times[column] = times[column].apply(lambda value:round(value,1))
    
    del times["chutes"]
    del times["passes_area"]
    del times["chutes_bloqueados"]
    del times["chutes_defendidos"]
    del times["chutes_trave"]
    del times["carrinho"]
    del times["dist_total"]
    del times["passes"]
    del times["vitorias"]
    del times ["empates"]
    del times ["derrotas"]

    times.columns = ["Gols","Ataques","Desarmes","Passes completados","Posse de bola","Chutes certos","Chutes para fora","Jogadas de bola parada","Cruzamentos","Escanteios","Impedimentos","Defesas","Bolas recuperadas","Bolas perdidas","Faltas cometidas","Cartões amarelos","Cartões vermelhos","Distância corrida com bola","Distância corrida sem bola","Passes curtos","Passes médios","Passes longos","Porcentagem de passes completos","Gols Sofridos","jogos","Pontos","Saldo de Gols"]
    
    times["Mordidas"] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
    
    #acha ranking
    times = times.sort(["Pontos","Saldo de Gols","Gols"],ascending=[0,0,0])
    times["Ranking"] = range(1,33)
    
    #iguala o ranking se os pontos, saldo e gols pró forem iguais
    times["pontuacao"] = times["Pontos"]*100 + times["Saldo de Gols"] + times["Gols"]*0.01
    
    #para cada um dos times
    for t in times.index:
        #cria lista com nome dos times que têm pontuação igual ao do que estamos vendo agora
        times_mesma_pontuacao = list(times[times.pontuacao == float(times[times.index == t]["pontuacao"])].index)
        #se houver mais um time nessa situação - ou seja, um empate
        if len(times_mesma_pontuacao) > 1:
            #acha o ranking do time que está acima (será o primeiro)
            ranking = times.loc[t,"Ranking"]
            #coloca o ranking igual para todos os outros times da nossa lista de mesmos pontos
            for outro_t in times_mesma_pontuacao:
                times.loc[outro_t,"Ranking"] = ranking

    del times ["pontuacao"]
    
    #calcula índice de chutes a gol por minuto de posse de bola
    times["prorrogacao"] = 0
    times.loc["Alemanha","prorrogacao"] = 1
    times.loc["Argélia","prorrogacao"] = 1
    times.loc["Brasil","prorrogacao"] = 1
    times.loc["Chile","prorrogacao"] = 1
    times.loc["Costa Rica","prorrogacao"] = 1
    times.loc["Grécia","prorrogacao"] = 1
    times.loc["Argentina","prorrogacao"] = 1
    times.loc["Suíça","prorrogacao"] = 1
    times.loc["Bélgica","prorrogacao"] = 1 
    times.loc["EUA","prorrogacao"] = 1 
    
    times["minutos_jogados"] = times["jogos"]*90 + times["prorrogacao"]*30
    times["minutos_posse_bola"] = times["minutos_jogados"]*times["Posse de bola"]/100
    times["Chutes por 100 min"] = 100*(times["Chutes certos"]+times["Chutes para fora"])/times["minutos_posse_bola"]
    times["Chutes certos por 100 min"] = 100*times["Chutes certos"]/times["minutos_posse_bola"]
    times["Gols por 100 min"] = 100*(times["Gols"])/times["minutos_posse_bola"]
    times["Ataques por 100 min"] = 100*(times["Ataques"])/times["minutos_posse_bola"]
    times["Minutos para cada gol"] = times["minutos_posse_bola"]/times["Gols"]
    
    del times["jogos"]
    del times["minutos_jogados"]
    del times["minutos_posse_bola"]
    del times["prorrogacao"]
    
    return times

def calculaGolsMinuto():
    jogos = consultaBase("jogos_fifa")
    jogos.index = jogos.codigo
    del jogos["codigo"]
    
    jogos["prorrogacao"] = 0
    jogos.ix[300186503,"prorrogacao"] = 1
    jogos.ix[300186460,"prorrogacao"] = 1
    jogos.ix[300186459,"prorrogacao"] = 1
    jogos.ix[300186487,"prorrogacao"] = 1 
    
    jogos["minutos_posse1"] = jogos["posse_bola1"]*(90+30*jogos["prorrogacao"])/100
    jogos["minutos_posse2"] = jogos["posse_bola2"]*(90+30*jogos["prorrogacao"])/100
    
    jogos["Minuto_gol1"] = jogos["minutos_posse1"]/jogos["gols1"]
    jogos["Minuto_gol2"] = jogos["minutos_posse2"]/jogos["gols2"]

    eventos = jogos
    
    #cria o nome das colunas e dataframes para cada um dos times
    colunas = list(eventos.columns)
    
    colunas1 = [campo for campo in colunas if campo[-1] == "1"]
    colunas2 = [campo for campo in colunas if campo[-1] == "2"]
    eventos1 = eventos[colunas1]
    eventos2 = eventos[colunas2]

    #faz uma tabela só com uma das colunas - cada linha continua sendo um jogo
    resultado = eventos1.append(eventos2)
    resultado = resultado.fillna(0)
    
    #arruma o nome do time
    resultado["time"] = resultado.apply(arrumaTime,axis=1)
    del resultado["time1"]
    del resultado["time2"]    

    #calcula a soma de todos os indicadores
    colunas = [c[:-1] for c in colunas1] #tira o 1 dos nomes de coluna
    colunas.pop(0) #tira o nome dos times
    
    for c in colunas:
        resultado[c] = resultado[c+"1"] + resultado[c+"2"]
        del resultado[c+"1"]
        del resultado[c+"2"]
    
    resultado.to_csv("graficoGolsMinuto.csv")
    
def graficoJogos(eventos):
    eventos.index = eventos["codigo"]
    del eventos["codigo"]
        
    #cria o nome das colunas e dataframes para cada um dos times
    colunas = list(eventos.columns)
    
    #tira o nome dos times do loop
    colunas.pop(0)
    colunas.pop(0)
    
    #pega os nomes únicos de cada coluna
    colunas = set([c[:-1] for c in colunas])
    
    #soma todas as colunas
    for c in colunas:
        eventos[c+"1"] = eventos[c+"1"].apply(int)
        eventos[c+"2"] = eventos[c+"2"].apply(int)
        eventos[c] = eventos[c+str(1)] + eventos[c+str(2)]
    
    #tira indices que não fazem sentido
    del eventos["posse_bola"]
    del eventos["porc_passes_completos"]
    
    #junta os times
    eventos["times"] = eventos["time1"] + " x " + eventos["time2"]
    
    #arruma os nomes
    eventos = eventos.rename_axis(nomeJogos,axis=1)

    return eventos
    
def nomeJogos(nome):
    traducao = {
        'escanteios':"Escanteios",
        'chutes_fora':"Chutes para fora",
        'passes_curtos':"Passes curtos",
        'dist_sem_bola':"Distância corrida sem bola",
        'carrinho':"Carrinhos",
        'cruzamentos':"Cruzamentos",
        'defesas':"Defesas",
        'dist_com_bola':"Distância corrida com bola",
        'chutes_certos':"Chutes certos",
        'chutes_bloqueados':"Chutes bloqueados",
        'chutes_defendidos':"Chutes defendidos",
        'cartao_amarelo':"Cartões amarelos",
        'bolas_perdidas':"Bolas perdidas",
        'passes_longos':"Passes longos",
        'ataque':"Ataques",
        'dist_total':"Distância corrida - Total",
        'bola_parada':"Jogadas de bola parada",
        'chutes':"Chutes a gol - Total",
        'bolas_recuperadas':"Bolas recuperadas",
        'passes':"Passes - Total",
        'impedimentos':"Impedimentos",
        'passes_area':"Passes dentro da área",
        'desarmes':"Desarmes",
        'passes_completados':"Passes completados",
        'cartao_vermelho':"Cartões vermelhos",
        'passes_medios':"Passes médios",
        'faltas_cometidas':"Faltas",
        'chutes_trave':"Chutes na trave",
        'gols':"Gols",
        'times':"Times"
    }
    
    if nome in traducao:
        return traducao[nome]
    elif nome[:-1] in traducao:
        if nome[-1] == "1": 
            return traducao[nome[:-1]]+"1"
        else:
            return traducao[nome[:-1]]+"2"
    else:
        return nome
    
def limpaBase(base):
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    my_collection.remove()

def limpaBases():
    limpaBase("jogos_fifa")
    limpaBase("jogadores_fifa")

def fazCalculos():
    consultaBase("jogadores_fifa").to_csv("jogadores_fifa_cadajogo.csv")
    jogos = consultaBase("jogos_fifa")
    jogos.to_csv("jogos_fifa.csv")
    graficoJogos(jogos).to_csv("grafico_jogos.csv")
    times = calculaTime()
    times.to_csv("times_fifa.csv")
    calculaGrafico(times).to_csv("grafico_times.csv")
    calculaJogador().to_csv("jogadores_fifa_total.csv")


#limpaBases()
#consultaData("20140612")
#consultaData("20140613")
#consultaData("20140614")
#consultaData("20140615")
#consultaData("20140616")
#consultaData("20140617")
#consultaData("20140618")
#consultaData("20140619")
#consultaData("20140620")
#consultaData("20140621")
#consultaData("20140622")
#consultaData("20140624")
#consultaData("20140625")
#consultaData("20140626")
#consultaJogo("300186488",True)

consultaJogo("300186490",False)
#consultaJogo("300186506")
fazCalculos()
#calculaGolsMinuto()
#eventos = consultaBase("jogos_fifa")
#print(eventos[eventos.time1 == "Argentina"])
#print(eventos[eventos.time2 == "Argentina"])
#consultaBase("jogos_fifa").to_csv("teste_fifa.csv",index=False)
#consultaBase("jogadores_fifa").to_csv("teste_fifa.csv")