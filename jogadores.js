var complete_data = null;
var time = null
var recorte = null
var svg = null;
var posicao = null
var media = null

function mudaRecorte() {
    //pega o valor
    var recorte = jQuery("#recorte").val();
    window.recorte = recorte
    
    //deleta o svg
	jQuery("#jogador").replaceWith('<div id="jogador"></div>');
	desenhaGrafico();
}

function mudaAgrupa() {
    //pega o valor
    var time = jQuery("#time").val();
    window.time = time;
    
    //deleta o svg
	jQuery("#jogador").replaceWith('<div id="jogador"></div>');
	desenhaGrafico();
}

function mudaPosicao() {
    //pega o valor
    var posicao = jQuery("#posicao").val();
    window.posicao = posicao;
    
    //volta a média para total
    mudaMedia("total")
    
    //deleta o svg
	jQuery("#jogador").replaceWith('<div id="jogador"></div>');
	desenhaGrafico();
}

function mudaMedia(media) {
    //passa o valor
    window.media = media;

    //ativa ou reativa o radio
    jQuery("input[name='"+media+"']").attr("checked","checked")

    //muda o nome da variável se for necessário
    if (media == "media") {
        recorte = recorte + " - Média"
    } else {
        recorte = recorte.replace(" - Média","")
    }

    //deleta o svg
	jQuery("#jogador").replaceWith('<div id="jogador"></div>');
	desenhaGrafico();
    
}

function desenhaGrafico()    {
    //pega as variáveis
    var recorte = window.recorte
    var time = window.time
    var data = window.complete_data;

    
    //vê se há agrupamento por time
    if (time != "total") {
        data = dimple.filterData(data,"time",time);
    }
    
    //vê se há agrupamento por posição
    if (posicao != "total") {
        data = dimple.filterData(data,"posicao",posicao);
    }
    
    //desenha o gráfico
    var svg = dimple.newSvg("#jogador", 950, 520);
    
    //elimina todos com zero
    data = data.filter(function(a){return a[recorte] > 0;});
    
    //pega os 32 top
    data.sort(function(a,b){return b[recorte] - a[recorte];});
    data = data.slice(0,32);
    
    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(140, 30, 500, 405)
    var x = myChart.addMeasureAxis("x", recorte);
    
    //coloca % se a variável pedir
    if (["Chutes convertidos em gols (%)","Acerto de chutes (%)"].indexOf(recorte)>=0) {
        x.tickFormat = "%";
    }
    var y = myChart.addCategoryAxis("y", "nome");
    //retira o título do eixo Y
    y.title = ""
    var series = myChart.addSeries("nome", dimple.plot.bar);
    y.addOrderRule(recorte,false)
    
    //arruma o gráfico
    myChart = colore(myChart)
    myChart = arrumaTolltip(myChart)
    
    //desenha
    myChart.draw();
    
    //continua arrumando
    colocaOrdem(myChart)
    mostraRadios();
    
}

function colore(myChart) {
    //uma cor para cada time. o Brasil tem duas por causa do stroke
    var cores = {
        "Argentina":"#22C5F2",
        "Bélgica":"#8F433D",
        "Chile":"#E82113",
        "Alemanha":"#E8BD13",
        "Suíça":"#E81344",
        "Espanha":"#DE1B1B",
        "C. Marfim":"#D68213",
        "Brasil":"#F4FC56",
        "Japão":"#CF0E00",
        "Itália":"#2665AD",
        "Nigéria":"#0EB02C",
        "Inglaterra":"#DECED0",
        "França":"#185EA8",
        "Coreia":"#AB5F54",
        "Gana":"#8C8C8C",
        "México":"#17521C",
        "Croácia":"#A65858",
        "Bósnia":"#6A89BD",
        "Portugal":"#B03C3C",
        "Rússia":"#A13618",
        "Equador":"#E8D71E",
        "Camarões":"#1F5714",
        "Uruguai":"#80CCFF",
        "Colômbia":"#94912F",
        "Costa Rica":"#99426D",
        "Estados Unidos":"#294663",
        "Grécia":"#47B4C9",
        "Austrália":"#E3E8B0",
        "Holanda":"#CC4B18",
        "Honduras":"#D6FBFF",
        "Argélia":"#DAFFD6",
        "Irã":"#616E5F"
    }
    
    //coloca as cores (fill para Brasil e Argélia)
    for (jogador in myChart.data) {
        if (myChart.data[jogador].time == "Brasil") {
            myChart.assignColor(myChart.data[jogador].nome,cores[myChart.data[jogador].time],"#091BAB",1)
        }
        else if (myChart.data[jogador].time == "Argélia") {
            myChart.assignColor(myChart.data[jogador].nome,cores[myChart.data[jogador].time],"#1E9E4F")
        } else {
        myChart.assignColor(myChart.data[jogador].nome,cores[myChart.data[jogador].time])
        }
    }
    return myChart
}

function arrumaTolltip(chart) {
    chart.series[0].getTooltipText = function (e) {
        //pega o nome
        var nome = e.aggField[0]
        //filtra o dado do gráfico e pega o time do jogador
        var time = chart.data.filter(function (a) { return a["nome"] == nome})[0]["time"] 

        return [
           window.recorte+": "+ e.xValue ,
           "Time: "+ time
        ];
    };
    return chart
    
}
function inicializa() {
    //checa se tem variavel na url
    //se tiver, coloca o recorte como ela e muda a option
    variaveis = getUrlVars()
   
    if ("recorte" in variaveis) {
        var recorte = variaveis["recorte"]
        jQuery('#recorte').val(recorte)
    }
    //se não tiver, coloca Gols mesmo
    else {
        var recorte = "Gols"
    }
    
    //faz o mesmo com o time
    if ("time" in variaveis) {
            var time = variaveis["time"]
            jQuery('#time').val(time)
        }
        //se não tiver, coloca total mesmo
        else {
            var time = "total"
    }
    
    //faz o mesmo com a posicao
    if ("posicao" in variaveis) {
            var posicao = variaveis["posicao"]
            jQuery('#posicao').val(posicao)
        }
        //se não tiver, coloca total mesmo
        else {
            var posicao = "total"
    }
    
    //faz o mesmo com a media
    if ("media" in variaveis) {
        var media = variaveis["media"]
        var radios = document.total_media.media
        for (var id = 0; id < radios.length; id++) {
            if (radios[id].value == media) jQuery(radios[id]).attr('disabled',false);
        }
    }
    else {
        var media = "total"
    }
        
    //arruma as variáveis globais
    window.recorte = recorte
    window.time = time
    window.posicao = posicao
    window.media = media
    
    //mostra ou não mostra os radios de total e média
    mostraRadios()
    
    //carrega os dados e cria o gráfico
//    d3.csv("https://s3-sa-east-1.amazonaws.com/blogedados/javascripts/copa_2014/grafico_jogadores.csv.csv", function (data) {
    d3.csv("grafico_jogadores.csv", function (data) {
    window.complete_data = data;
    desenhaGrafico()
    });
}

function mostraRadios() {
    //vê quais são nossos agrupamentos
    var media = window.media
    var recorte = window.recorte
    
    //se recorte estiver com média, tira
    recorte = recorte.replace(" - Média","")
    
    var variaveis_com_media = ['Assistências', 'Bloqueios', 'Carrinhos', 'Chutes Certos', 'Chutes ao gol', 'Cruzamentos', 'Faltas Cometidas', 'Faltas Sofridas', 'Gols', 'Impedimentos', 'Passes', 'Roubadas']
    
    if (variaveis_com_media.indexOf(recorte) >= 0) {
        jQuery("form[name='total_media']").show()
    } else { 
        jQuery("form[name='total_media']").hide()
    }
}
function colocaOrdem(chart) {
    //coloca bold no texto dos jogadores do Brasil
    jogadores_BR = chart.data.filter(function (a) { return a["time"] == "Brasil"})
    for (j in jogadores_BR) {
        jQuery("#jogador").find('text:contains("'+jogadores_BR[j]["nome"]+'")').css({'font-weight':'bold'})    
    }
    
    //achar ordem dos jogadores
    jogadores = []
    nomes = jQuery("#jogador").find(".dimple-axis").find("text[x=-9]").each(
        function() {
            if (jQuery(this).text()) {
                jogadores.push(jQuery(this).text())
            }
        }
    );

    //coloca o número na frente de cada jogador
   for (var i = 0; i < jogadores.length;i++) {
        jQuery("#jogador").find('text:contains("'+jogadores[i]+'")').text((jogadores.length - i) + " - " +jogadores[i]);
    }
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}


