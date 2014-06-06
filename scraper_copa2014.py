import xlsxwriter
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient
from pandas import DataFrame, pivot_table, merge,concat, Series
import numpy as np
from re import match

def partidasDia(dia):
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_results_"+dia+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    #separa cada partida
    partidas = str(page).split("|")
    
    #retira simbolos do inicio e do final
    partidas[0] = partidas[0].replace("matches=","")
    partidas[len(partidas)-1] = partidas[len(partidas)-1].replace("&amp;updte;=no&amp;Endstr;=End","")
    
    #adiciona items ao banco de dados
    for p in partidas:
        jogo = adicionaPartidas(p)
        if jogo:
            adicionaEventos(jogo)
            adicionaJogadores(jogo)

def adicionaPartidas(partida):  
    #separa os campos de cada partida e monta o resultado final
    try:
        campos = partida.split("~")
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
    except:
        pass
    
    #adiciona ao banco de dados
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["partidas"]
    
    #retira as partidas antigas
    partidas_antigas = [c["codigo_partida"] for c in list(my_collection.find())]
    
    if jogo["codigo_partida"] not in partidas_antigas:    
        my_collection.insert(jogo)
        return jogo
    else:
        return False

def adicionaJogadores(partida):
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_lineups_2012081111387.txt&timezone=ET&pad=y&callback=cb"
    #codigo = partida['codigo_partida']
    #url = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_lineups_"+codigo+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    jogadores = str(page).split("=")
    titulares = jogadores[2].split("&")[0]+jogadores[3].split("&")[0]
    reservas = jogadores[4].split("&")[0]+jogadores[5].split("&")[0]
    eventos = jogadores[6].split("&")[0]+jogadores[7].split("&")[0]
    
    print(reservas)
    
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
    datas = ['20120726','20120729','20120801','20120804','20120807','20120810','20120811']
    for d in datas:
        partidasDia(d)

def adicionaEventos(partida):
    codigo = partida['codigo_partida']
    time1 = partida['time1']
    time2 = partida['time2']
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/oly_msoc_shotchrt_"+codigo+".txt"
    page = BeautifulSoup(urlopen(url).read())

    #retira símbolos do final
    evento = str(page).split("&")[0]
    evento = evento.split("|")
    
    #retira simbolos do inicio
    evento[0] = evento[0].replace('cb({"data":"pbpEvents=',"")
    evento[0] = evento[0].replace('pbpEvents=',"")
    
    #separa os eventos
    resultado = []
    for e in evento:
        lance = {}
        campos = e.split("~")
        lance["codigo_partida"] = codigo
        lance["time"] = time1 if (campos[0] == "home") else time2
        lance["evento"] = campos[1].split("^")[0]
        lance["local"] = campos[2].split(",")[0]
        lance["quadrante"] = achaQuadrante(lance["local"],campos[0])
        lance["camisa_jogador"] = campos[3]
        lance["minuto"] = campos[4]
        lance["intervalo"] = achaIntervalo(lance["minuto"])
        lance["jogador"] = campos[5]
        lance["num_evento"] = campos[7]
        resultado.append(lance)
    
    #adiciona ao banco de dados
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["eventos"]
    
    for r in resultado:
        my_collection.insert(r)
    
def consultaBase(base):
    #faz a consulta
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    items = list(my_collection.find())
    return DataFrame(items)
    
    #exporta pro csv
    #keys = list(items[0].keys())
    #f = open(base+'.csv', 'w')
    #dict_writer = csv.DictWriter(f, keys)
    #dict_writer.writer.writerow(keys)
    #dict_writer.writerows(items)

def limpaBase(base):
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    my_collection.remove()
    
def calculaGols(eventos):
    #ignora se o lance foi no ataque ou na defesa
    eventos["quadrante"] = eventos["quadrante"].apply(lambda t: t[4:len(t)])
    
    #calcula gols por time
    gols = eventos[eventos.evento == "Goal"]
    gols_por_time = pivot_table(gols, values='evento', rows="time", aggfunc="count")
    gols_por_time = gols_por_time.order(ascending=False)
    
    #calcula aproveitamento total
    chutes = eventos[(eventos.evento == "Shot on Target") | (eventos.evento == "Shot off Target")]
    chutes_por_time = pivot_table(chutes, values='evento', rows="time", aggfunc="count")
    aproveitamento = concat([gols_por_time,chutes_por_time], axis=1)
    aproveitamento.columns = ["gols","chutes"]
    aproveitamento = aproveitamento.fillna(0)
    aproveitamento["aproveitamento"] = (aproveitamento["gols"]/aproveitamento["chutes"])*100
    aproveitamento = aproveitamento.apply(lambda t: np.round(t,1))
    
    #calcula aproveitamento por quadrante
    gols_por_quadrante = pivot_table(gols, values='evento', columns="quadrante", rows="time", aggfunc="count")
    gols_por_quadrante.columns = ["gol^"+nome for nome in gols_por_quadrante.columns]
    chutes_por_quadrante = pivot_table(chutes, values='evento', columns="quadrante", rows="time", aggfunc="count")
    chutes_por_quadrante.columns = ["chute^"+nome for nome in chutes_por_quadrante.columns]
    aproveitamento_por_quadrante = concat([gols_por_quadrante,chutes_por_quadrante], axis=1)
    #se a coluna existir tanto nos chutes qnt nos gols, divida um pelo outro 
    for coluna in chutes_por_quadrante.columns:
        nome = coluna.split("^")[1]
        if ("gol^"+nome) in gols_por_quadrante.columns:
            aproveitamento_por_quadrante["aprov^"+nome] = (aproveitamento_por_quadrante["gol^"+nome]/aproveitamento_por_quadrante["chute^"+nome])*100
        #se não existir gol, é zero
        else:
            aproveitamento_por_quadrante["aprov^"+nome] = 0
    aproveitamento_por_quadrante = aproveitamento_por_quadrante.fillna(0)
    aproveitamento_por_quadrante = aproveitamento_por_quadrante.apply(lambda t: np.round(t,1))
    
    #calcula gol por intervalo
    gols_por_intervalo = pivot_table(gols, values='evento', columns="intervalo", rows="time", aggfunc="count")
    gols_por_intervalo = gols_por_intervalo.fillna(0)
    #acha o total de gols
    gols_por_intervalo['total_gols']=gols_por_intervalo.sum(axis=1)
    #cria colunas de % para cada intervalo de tempo
    gols_por_intervalo = gols_por_intervalo.join(gols_por_intervalo.div(gols_por_intervalo['total_gols'], axis=0)*100, rsuffix='_porc')
    del gols_por_intervalo['total_gols']
    del gols_por_intervalo['total_gols_porc']
    gols_por_intervalo = gols_por_intervalo.fillna(0)
    gols_por_intervalo = gols_por_intervalo.apply(lambda t: np.round(t,1))
    
    #junta todos os arquivos em um só e exporta para csv
    resultado = concat([aproveitamento,aproveitamento_por_quadrante,gols_por_intervalo], axis=1)
    resultado.to_csv("calcula_gols.csv")

def calculaFaltas(eventos):
    #calcula faltas por time
    faltas = eventos[eventos.evento == "Foul"]
    faltas_por_time = pivot_table(faltas, values='evento', rows="time", aggfunc="count")
    
    #calcula faltas por quadrante
    faltas_por_quadrante = pivot_table(faltas, values='evento', columns="quadrante", rows="time", aggfunc="count")
    
    #calcula faltas por intervalo
    faltas_por_intervalo = pivot_table(faltas, values='evento', columns="intervalo", rows="time", aggfunc="count")
    faltas_por_intervalo = faltas_por_intervalo.fillna(0)
    #acha o total de faltas
    faltas_por_intervalo['total_faltas']=faltas_por_intervalo.sum(axis=1)
    #cria colunas de % para cada intervalo de tempo
    faltas_por_intervalo = faltas_por_intervalo.join(faltas_por_intervalo.div(faltas_por_intervalo['total_faltas'], axis=0)*100, rsuffix='_porc')
    del faltas_por_intervalo['total_faltas']
    del faltas_por_intervalo['total_faltas_porc']
    faltas_por_intervalo = faltas_por_intervalo.fillna(0)
    faltas_por_intervalo = faltas_por_intervalo.apply(lambda t: np.round(t,1))
    
    #junta todos os arquivos em um só e exporta para csv
    resultado = concat([faltas_por_time,faltas_por_quadrante,faltas_por_intervalo], axis=1)
    resultado.to_csv("calcula_faltas.csv")
    
def achaQuadrante(local,lado):
    #se o local for válido
    if local:
        #acha se o local é no ataque ou na defesa
        if (lado == "away"):
            lado_campo = "atq_" if (local[0] == "H") else "def_" 
        else:
            lado_campo = "atq_" if (local[0] == "V") else "def_" 
             
        #retira a primeira letra
        local = local[1:len(local)]
        
        #separa letras e números
        letra = local[0]
        numero = int(local[1:len(local)])
        
        #descobre onde está
        if numero > 17:
            return lado_campo+"longe"
        elif match("[A-F]|[U-Z]",letra):
            return lado_campo+"zona_morta"
        elif numero > 8:
            return lado_campo+"fora_area"
        elif (numero < 4) & bool(match("[K-P]",letra)):
            return lado_campo+"pequena_area"
        else:
            return lado_campo+"grande_area"
    else: #se não tiver local
        return "____indefinido"

def achaIntervalo(minuto):
    #se o minuto for válido
    if minuto:
        minuto = int(minuto)
        if minuto < 16:
            return "1o_15"
        elif minuto < 31:
            return "1o_30"
        elif minuto < 46:
            return "1o_45"
        elif minuto < 61:
            return "2o_15"
        elif minuto < 76:
            return "2o_30"
        else:
            return "2o_45"
    else:
        return "indefinido"

def desenhaExcel():
    eventos = consultaBase("eventos")
    workbook = xlsxwriter.Workbook('faltas.xlsx')
    worksheet = workbook.add_worksheet()
    gols = eventos[eventos.evento == "Foul"]
    locais = list(gols["local"])

    #cria um dicionário em que as keys são os locais e os valores o número de eventos dali
    soma = {}
    for l in locais:
        l = l[1:len(l)] #retira a primeira letra
        if l in soma.keys():
            soma[l] = soma[l] + 1
        else:
            soma[l] = 1
    
    #escreve o resultado
    for s in soma.keys():
        worksheet.write(s, soma[s])


#desenhaExcel()
#limpaBase("partidas")
#limpaBase("eventos")
#print(consultaBase("partidas"))
#eventos = print(consultaBase("eventos"))
#calculaFaltas(consultaBase("eventos"))
#atualizaPartidas()
adicionaJogadores("ble")
