import xlsxwriter
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from datetime import date
import csv
from pymongo import MongoClient
from pandas import DataFrame, pivot_table, merge,concat, Series
import numpy as np
from re import match
from datetime import date, datetime, timedelta as td

def partidasDia(dia):
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/natl_wcup_results_"+dia+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    #se houver partida
    if str(page):
        #separa cada partida
        partidas = str(page).split("|")
    
        #retira simbolos do inicio e do final
        partidas[0] = partidas[0].replace("matches=","")
        partidas[len(partidas)-1] = partidas[len(partidas)-1].replace("&amp;updte;=no&amp;Endstr;=End","")
    
        #adiciona items ao banco de dados
        for p in partidas:
            jogo = adicionaPartidas(p)
            if jogo: #se houver info
                adicionaEventos(jogo)
                jogadores = adicionaJogadores(jogo)
                if jogadores: #se houver info
                    atualizaJogadoresInfo(jogadores,jogo)


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
    codigo = partida['codigo_partida']
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/natl_wcup_lineups_"+codigo+".txt&timezone=ET&pad=y&callback=cb"
    
    page = BeautifulSoup(urlopen(url).read())

    #se houver info
    try:
        #pega os valores brutos
        jogadores = str(page).split("=")
        titulares_bruto = jogadores[2].split("&")[0]+jogadores[3].split("&")[0]
        banco_bruto = jogadores[4].split("&")[0]+jogadores[5].split("&")[0]
        eventos_bruto = jogadores[8].split("&")[0]+jogadores[9].split("&")[0]
    
        #cria lista com dicionários e campos organizados
        resultado = []
        for t in titulares_bruto.split("|"):
            campos = t.split("~")
            jogador = {}
            jogador["codigo"] = campos[0]
            jogador["partida"] = codigo
            jogador["evento"] = "titular"
            resultado.append(jogador)
        
        for t in banco_bruto.split("|"):
            campos = t.split("~")
            jogador = {}
            jogador["codigo"] = campos[0]
            jogador["partida"] = codigo
            jogador["evento"] = "banco"
            resultado.append(jogador)
        
        #gambiarra pra pegar todas as substituições
        eventos = [a.split("^") for a in eventos_bruto.split("|")]
        eventos_limpos = []
        for e in eventos:
            for i in e:
                eventos_limpos.append(i)

        for t in eventos_limpos:
            campos = t.split("~")
            jogador = {}
            jogador["partida"] = codigo
            #se for sub, adiciona dois jogadores aos eventos
            if campos[1] == "sub":
                jogador["evento"] = "sub_entrou"
                jogador["codigo"] = campos[3].split("*")[0].split("#")[1]
                resultado.append(jogador)
                jogador2 = {}
                jogador2["partida"] = codigo
                jogador2["evento"] = "sub_saiu"
                jogador2["codigo"] = campos[3].split("*")[1].split("#")[1]
                resultado.append(jogador2)
            
            else:
                jogador["evento"] = campos[1]
                jogador["codigo"] = campos[3].split("#")[1]
                resultado.append(jogador)

        #adiciona as novas infos no banco
        client = MongoClient()
        my_db = client["copa"]
        my_collection = my_db["jogadores"]

        for r in resultado:
            my_collection.insert(r)
    
        retornar = [r["codigo"] for r in resultado]
        return set(retornar)
    except IndexError: #se não houver info
        return False


def atualizaJogadoresInfo(jogadores,partida):
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db["jogadores_info"]
    
    total_jogadores = []
    for j in jogadores:
        #primeira página de stats
        url = "http://hosted.stats.com/ifb2009/data.asp?file=en/natl_wcup_player_"+j+".txt"
        page = BeautifulSoup(urlopen(url).read())
        #se houver jogador
        try:
            page = str(page).replace('cb({"data":"&amp;player;',"")
            page = page.replace(';biography;=&amp;Endstr;=End"})',"")
            campos = page.split("=")
            jogador = {}
            jogador["nome"] = campos[1].split("&")[0]
            jogador["codigo"] = campos[2].split("&")[0]
            infos = campos[7].split("~")
            jogador["time"] = infos[0]
            jogador["adversario"] = partida["time1"] if jogador["time"] == partida["time2"] else partida["time2"]
            jogador["posicao"] = infos[1]
            try: #se tiver cidade e país de nascimento
                jogador["cidade_nascimento"] = infos[2].split(",")[0].strip()
                jogador["pais_nascimento"] = infos[2].split(",")[1].strip()
            except IndexError: #se não, deixa a cidade como indefinido
                jogador["cidade_nascimento"] = "indefinido"
                jogador["pais_nascimento"] = infos[2].split(",")[0].strip()
            jogador["altura"] = infos[3].split(" ")[0]
            jogador["peso"] = infos[4].split(" ")[0]
            try: #se tiver data de nascimento
                jogador["ano_nascimento"] = infos[5].strip().split("&")[0]
            except IndexError: #se não tiver
                jogador["ano_nascimento"] = "indefinido"
        except IndexError:
            pass
        total_jogadores.append(jogador)                        
    
    #segunda página de stats
    url = "http://matchcast.estadao.stats.com/ifb2009/data.asp?file=pt/natl_wcup_plyrstat_"+partida["codigo_partida"]+".txt"
    page = BeautifulSoup(urlopen(url).read())

    campos = str(page).split("=")
     #para não goleiro
    infos_bruto = campos[5].split("|")
    for j in infos_bruto:
        try:
            infos = j.split("~")
            codigo = infos[1]
            informacoes = [inf.split("^")[0] for inf in infos]
            jogador = {}
            jogador["gols"] = informacoes[5]
            jogador["assistencias"] = informacoes[6]
            jogador["chutes_total"] = informacoes[7]
            jogador["chutes_certos"] = informacoes[8]
            jogador["passes"] = informacoes[9]
            jogador["roubadas"] = informacoes[10]
            jogador["bloqueios"] = informacoes[11]
            jogador["carrinhos"] = informacoes[12]
            jogador["faltas_cometidas"] = informacoes[15]
            jogador["faltas_sofridas"] = informacoes[16]
            jogador["cruzamentos"] = informacoes[17]
            jogador["impedimentos"] = informacoes[18]
            
            for t in total_jogadores:
                if t["codigo"] == codigo:
                    saida = dict(list(t.items()) + list(jogador.items()))
                    my_collection.insert(saida)
        except IndexError: 
            pass    
    
    #agora os goleiros
    infos_bruto = campos[7].split("|")
    for j in infos_bruto:
        try:
            infos = j.split("~")
            codigo = infos[1]
            informacoes = [inf.split("^")[0] for inf in infos]
            jogador = {}
 #           jogador["defesa_menos_vazada"] = informacoes[0]
 #           jogador["defesas"] = informacoes[1]
 #           jogador["chutes_recebidos1"] = informacoes[2]
 #           jogador["chutes_recebidos2"] = informacoes[3]
 #           jogador["faltas_cometidas"] = informacoes[4]
 #           jogador["faltas_sofridas"] = informacoes[5]
            for t in total_jogadores:
                if t["codigo"] == codigo:
                    saida = dict(list(t.items()) + list(jogador.items()))
                    my_collection.insert(saida)
            
        except IndexError: 
            pass    
    
def adicionaEventos(partida):
    codigo = partida['codigo_partida']
    time1 = partida['time1']
    time2 = partida['time2']
    url = "http://hosted.stats.com/ifb2009/data.asp?file=en/natl_wcup_shotchrt_"+codigo+".txt"
    page = BeautifulSoup(urlopen(url).read())
    
    #se houver evento
    try:
        
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
    except IndexError:
        pass
        
def consultaBase(base):
    #faz a consulta
    client = MongoClient()
    my_db = client["copa"]
    my_collection = my_db[base]
    items = list(my_collection.find())
    #transforma tudo que possível em número
    saida = []
    for item in items:
        jogador = {}
        for k in item:
            try:
                jogador[k] = int(item[k])
            except:
                jogador[k] = item[k]
        saida.append(jogador)
    return DataFrame(saida)
    
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
    #calcula o numero de jogos
    partidas = set(list(eventos["codigo_partida"]))
    junta_partidas = []
    for p in partidas:
        times = list(set(list(eventos[eventos.codigo_partida == p]["time"])))
        junta_partidas.append({"codigo":p,"time":times[0]})
        junta_partidas.append({"codigo":p,"time":times[1]})

    jogos = DataFrame(junta_partidas)
    num_jogos = pivot_table(jogos, values='codigo', rows="time", aggfunc="count")
    
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
    resultado = concat([num_jogos,aproveitamento,aproveitamento_por_quadrante,gols_por_intervalo], axis=1)
    names = list(resultado.columns)
    names[0] = "jogos"
    resultado.columns = names
    resultado.to_csv("gols_stats.csv")

def calculaFaltas(eventos):
    #calcula o numero de jogos
    partidas = set(list(eventos["codigo_partida"]))
    junta_partidas = []
    for p in partidas:
        times = list(set(list(eventos[eventos.codigo_partida == p]["time"])))
        junta_partidas.append({"codigo":p,"time":times[0]})
        junta_partidas.append({"codigo":p,"time":times[1]})
    
    jogos = DataFrame(junta_partidas)
    num_jogos = pivot_table(jogos, values='codigo', rows="time", aggfunc="count")

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
    resultado = concat([num_jogos,faltas_por_time,faltas_por_quadrante,faltas_por_intervalo], axis=1)
    names = list(resultado.columns)
    names[0] = "jogos"
    names[1] = "faltas"
    resultado.columns = names
    resultado.to_csv("faltas_stats.csv")

def calculaJogador(eventos):

    #calcula partidas titulares dos jogadores
    titulares = eventos[eventos.evento == "titular"]
    titular = pivot_table(titulares, values='evento', rows="codigo", aggfunc="count")
    titular = titular.to_frame("titular")

    #calcula partidas banco dos jogadores
    bancos = eventos[eventos.evento == "banco"]
    banco = pivot_table(bancos, values='evento', rows="codigo", aggfunc="count")
    banco = banco.to_frame("banco")
    
    #calcula partidas que saiu dos jogadores
    sairam = eventos[eventos.evento == "sub_saiu"]
    saiu = pivot_table(sairam, values='evento', rows="codigo", aggfunc="count")
    saiu = saiu.to_frame("saiu")
    
    #calcula partidas que entraram dos jogadores
    entraram = eventos[eventos.evento == "sub_entrou"]
    entrou = pivot_table(entraram, values='evento', rows="codigo", aggfunc="count")
    entrou = entrou.to_frame("entrou")
    
    #calcula cartões amarelos jogadores
    amarelos = eventos[eventos.evento == "ycard"]
    amarelo = pivot_table(amarelos, values='evento', rows="codigo", aggfunc="count")
    amarelo = amarelo.to_frame("amarelo")
    
    #calcula cartões vermelhos jogadores
    vermelhos = eventos[eventos.evento == "rcard"]
    vermelho = pivot_table(vermelhos, values='evento', rows="codigo", aggfunc="count")
    vermelho = vermelho.to_frame("vermelho")
    
    resultado=concat([titular,banco,saiu,entrou,amarelo,vermelho], axis=1)
    resultado = resultado.fillna(0)
    
    #adiciona infos do jogador que está no banco de dados
    jogadores_antigos = consultaBase("jogadores_info")
    
    #enche vazios e NAs com 0
    jogadores_antigos = jogadores_antigos.fillna(0)
    for coluna in jogadores_antigos:
        jogadores_antigos[coluna] = jogadores_antigos[coluna].apply(encheEspaco)
    
    #exporta o jogadores_antigos para um csv
    del jogadores_antigos["_id"]
    
    #acrescenta cartões aos jogadores_antigos
    jogadores_antigos.index = jogadores_antigos["codigo"]
    
    temp = jogadores_antigos.join(resultado,how="left")
    
    jogadores_antigos.to_csv("jogador_stats_cadajogo.csv",index=False)
    
    #salva o dataframe para ser usado depois
    del temp["titular"]
    del temp["banco"]
    del temp["saiu"]
    del temp["entrou"]
    
    jogadores_cadajogo = temp
    
    #faz a tabela dinâmica das infos antigas
    antigos_dinamica = jogadores_antigos.groupby("codigo").sum()
    
    del antigos_dinamica["peso"]
    
    #adiciona infos que retiramos (nome, ano nascimento e peso)
    jogadores_antigos = jogadores_antigos.set_index("codigo")
    for coluna in jogadores_antigos:
        if coluna not in ["nome","ano_nascimento","peso","time","posicao","altura"]:
            del jogadores_antigos[coluna]
    
    #junta as infos
    final = jogadores_antigos.join(antigos_dinamica,how="right")

    resultado = final.join(resultado,how="right")
    resultado = resultado.drop_duplicates()
    
    #arruma o nome dos times para português
    resultado["time"] = resultado["time"].apply(arrumaTime)
    
    resultado.to_csv("jogador_stats_somado.csv")
    
    return resultado, jogadores_cadajogo

def graficoJogador(jogadores,jogadores_cadajogo):
    #coloca o nome como index
    jogadores.index = jogadores["nome"]

    #arruma posição
    traducao = {"Goalkeeper":"Goleiro","Defender":"Zagueiro","Midfielder":"Meio Campo","Forward":"Atacante"}
    jogadores["posicao"] = jogadores["posicao"].apply(lambda t: traducao[t])
    
    #descobre número jogos jogados
    jogadores["jogos"] = jogadores["titular"] + jogadores["entrou"]
    
    #calcula média
    colunas_com_media = ["assistencias","bloqueios","carrinhos","chutes_certos","chutes_total","cruzamentos","faltas_cometidas","faltas_sofridas","gols","impedimentos","passes","roubadas"]
    for c in colunas_com_media:
        jogadores[c+"_media"] = jogadores[c]/jogadores["jogos"]
    jogadores = jogadores.replace([np.inf, -np.inf], np.nan)
    jogadores = jogadores.fillna(0)
    
    #arredonda tudo
    for coluna in jogadores:
        try:
            jogadores[coluna] = jogadores[coluna].apply(lambda t:round(t,1))
        except:
            pass
    
    del jogadores["entrou"]
    del jogadores["saiu"]
    del jogadores["titular"]
    del jogadores["banco"]
    del jogadores["nome"]

    #agora vamos juntar a tabela de cada jogo
    jogadores["adversario"] = "Todos"    
    
    jogadores_cadajogo.index = jogadores_cadajogo["nome"]
    del jogadores_cadajogo["cidade_nascimento"]
    del jogadores_cadajogo["nome"]
    del jogadores_cadajogo["codigo"]
    del jogadores_cadajogo["pais_nascimento"]
    
    final = jogadores.append(jogadores_cadajogo)
    final = final.fillna(0)
    
    #calcula aproveitamento e chutes no alvo
    final["aproveitamento"] = final["gols"]/final["chutes_total"]    
    final["mira_certa"] = final["chutes_certos"]/final["chutes_total"]
    
    #descobre idade
    final["idade"] = final["ano_nascimento"].apply(achaIdade)
    del final["ano_nascimento"]
    
    #arruma os nomes
    final = final.rename_axis(nomeJogador,axis=1)
    final["adversario"] = final["adversario"].apply(arrumaTime)
    final["time"] = final["time"].apply(arrumaTime)
    
    
    final.to_csv("grafico_jogadores.csv")
        
def nomeJogador(nome):
    traducao = {
        'altura':"Altura",
        'amarelo':"Cartões Amarelos",
        'aproveitamento':"Chutes convertidos em gols (%)",
        'assistencias':"Assistências",
        'assistencias_media':"Assistências - Média",
        'bloqueios':"Bloqueios",
        'bloqueios_media':"Bloqueios - Média",
        'carrinhos':"Carrinhos",
        'carrinhos_media':"Carrinhos - Média",
        'chutes_certos':"Chutes Certos",
        'chutes_certos_media':"Chutes Certos - Média",
        'chutes_total':"Chutes ao gol",
        'chutes_total_media':"Chutes ao gol - Média",
        'cruzamentos':"Cruzamentos",
        'cruzamentos_media':"Cruzamentos - Média",
        'faltas_cometidas':"Faltas Cometidas",
        'faltas_cometidas_media':"Faltas Cometidas - Média",
        'faltas_sofridas':"Faltas Sofridas",
        'faltas_sofridas_media':"Faltas Sofridas - Média",
        'gols':"Gols",
        'gols_media':"Gols - Média",
        'idade':"Idade",
        'impedimentos':"Impedimentos",
        'impedimentos_media':"Impedimentos - Média",
        'jogos':"Jogos",
        'mira_certa':"Acerto de chutes (%)",
        'passes':"Passes",
        'passes_media':"Passes - Média",
        'peso':"Peso",
        'roubadas':"Roubadas",
        'roubadas_media':"Roubadas - Média",
        'vermelho':"Cartões Vermelhos"
        }
            
    if nome in traducao:
        return traducao[nome]
    else:
        return nome

def achaIdade(data_nascimento):
    #acha dia, mês e ano
    campos = data_nascimento.split(" ")
    dia = campos[0]
    mes = campos[1].replace(",","")
    ano = campos[2]
    
    #conserta o mês
    datas = {
        "January":"01",
        "February":"02",
        "March":"03",
        "April":"04",
        "May":"05",
        "June":"06",
        "July":"07",
        "August":"08",
        "September":"09",
        "October":"10",
        "November":"11",
        "December":"12",
    }
    mes = datas[mes]
    
    data_string = dia + "/" + mes + "/" + ano
    
    data = time.strptime(data_string, "%d/%m/%Y")
    
    idade = calculate_age(data)
    
    return idade

def calculate_age(born):
    today = date.today()
    return today.year - born.tm_year - ((today.month, today.day) < (born.tm_mon, born.tm_mday))
    
def arrumaTime(time):
    traducao = {
        "Germany":"Alemanha",
        "Algeria":"Argélia",
        "Argentina":"Argentina",
        "Australia":"Austrália",
        "Belgium":"Bélgica",
        "Bosnia-Herzegovina":"Bósnia",
        "Brazil":"Brasil",
        "Ivory Coast":"C. Marfim",
        "Cameroon":"Camarões",
        "Chile":"Chile",
        "Colombia":"Colômbia",
        "Korea Republic":"Coreia",
        "Costa Rica":"Costa Rica",
        "Croatia":"Croácia",
        "Ecuador":"Equador",
        "Spain":"Espanha",
        "United States":"Estados Unidos",
        "France":"França",
        "Ghana":"Gana",
        "Greece":"Grécia",
        "Netherlands":"Holanda",
        "Honduras":"Honduras",
        "England":"Inglaterra",
        "Iran":"Irã",
        "Italy":"Itália",
        "Japan":"Japão",
        "Mexico":"México",
        "Nigeria":"Nigéria",
        "Portugal":"Portugal",
        "Russia":"Rússia",
        "Switzerland":"Suíça",
        "Uruguay":"Uruguai",
    }
    if time in traducao:
        return traducao[time]
    else:
        return time
    
def encheEspaco(t):
    if t == "":
        return 0
    else:
        return t

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

def atualizaPartidas():
    data_inicio = datetime.strptime('09072014', "%d%m%Y").date()
    data_fim = datetime.strptime('09072014', "%d%m%Y").date()
    delta = data_fim - data_inicio
    datas = []
    for i in range(delta.days + 1):
        datas.append((data_inicio + td(days=i)).strftime("%Y%m%d"))
    
    for d in datas:
        print("Pegando informações de "+d+"...")
        partidasDia(d)

def limpaBases():
    limpaBase("partidas")
    limpaBase("eventos")
    limpaBase("jogadores")
    limpaBase("jogadores_info")

def fazConsultas():
    calculaGols(consultaBase("eventos"))
    calculaFaltas(consultaBase("eventos"))
    jogador,jogadores_cadajogo = calculaJogador(consultaBase("jogadores"))
    graficoJogador(jogador,jogadores_cadajogo)
    

#desenhaExcel()
#limpaBases()
atualizaPartidas()
fazConsultas()

#eventos = consultaBase("jogadores")
#jogadores = consultaBase("jogadores_info")
#jogadores = jogadores[jogadores.nome == "Fernandinho"]
#eventos = eventos[eventos.codigo == 348958]
#print(eventos)

#calculaJogador(consultaBase("jogadores"))
#teste.to_csv("teste_copa.csv")

