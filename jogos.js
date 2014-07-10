var jogos_data = null,
recorteJogo = null,
ordem_jogo = null

function mudaRecorteJogo() {
    //pega o valor
    var recorteJogo = jQuery("#recorteJogo").val();
    window.recorteJogo = recorteJogo
    
    redesenhaGraficoJogos();
}


function mudaOrdemJogo(el){
    //pega o valor
    var ordem_jogo = el.value;
    window.ordem_jogo = ordem_jogo;
    jQuery(el).prop('checked',true);
    jQuery('input[name="ordem_jogo"][value!="' + ordem_jogo + '"]').prop('checked', false);

    redesenhaGraficoJogos();
}

function redesenhaGraficoJogos(){
    //deleta o svg
    jQuery("#jogos").replaceWith('<div id="jogos"></div>');
    desenhaGraficoJogos();
}

function ordenaDadosJogos(a, b){
    if (window.ordem_jogo == "Crescente") {
        return a[window.recorteJogo] - b[window.recorteJogo];
    } else {
        return b[window.recorteJogo] - a[window.recorteJogo];
    }
}

function desenhaGraficoJogos()    {
    //pega as variáveis
    var recorteJogo = window.recorteJogo,
        data = window.jogos_data,
        ordem_jogo = window.ordem_jogo;
    
    //desenha o gráfico
    var svg = dimple.newSvg("#jogos", 950, 700);

    //descobre o valor máximo
    var maximo_x = d3.max(data, function(d) {
        return parseFloat(d[recorteJogo]);
    }); 
    
    //pega os 32 top
    data.sort(ordenaDadosJogos);
    data = data.slice(0,32);

    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(190, 30, 600, 600);
    var x = myChart.addMeasureAxis("x", recorteJogo);

    //bota o tamanho máximo de x (para igualar ordem_jogo crescente ou decrescente)
    x.overrideMax = maximo_x;
    x.ticks = 5;
    
    var y = myChart.addCategoryAxis("y", "Times");
    //retira o título do eixo Y
    y.title = "";
    var series = myChart.addSeries("Times", dimple.plot.bar);
    
    series.barGap = 0.42;
    
    if (ordem_jogo == "Decrescente") {
        y.addOrderRule(recorteJogo,false);
    } else {
        y.addOrderRule(recorteJogo,true);
    }

    //arruma o gráfico
    myChart = coloreJogos(myChart);
    myChart = arrumaTolltipJogos(myChart);

    //desenha
    myChart.draw();

    //continua arrumando
    arrumaNomesJogos()
    colocaOrdemJogos(myChart)
    
}

function coloreJogos(myChart) {
    //ranking da ordem_jogo dos times
    var ranking = [
        "Colômbia",
        "Holanda",
        "Argentina",
        "Bélgica",
        "França",
        "Alemanha",
        "Brasil",
        "Costa Rica",
        "Chile",
        "México",
        "Suíça",
        "Uruguai",
        "Grécia",
        "Argélia",
        "Equador",
        "EUA",
        "Nigéria",
        "Portugal",
        "Croácia",
        "Bósnia e Herzegovina",
        "Costa do Marfim",
        "Itália",
        "Espanha",
        "Rússia",
        "Gana",
        "Inglaterra",
        "Coreia do Sul",
        "Irã",
        "Japão",
        "Austrália",
        "Honduras",
        "Camarões"   
        ]
    
    //uma cor para cada time 
    var cores = {
        "Argentina":"#22C5F2",
        "Bélgica":"#8F433D",
        "Chile":"#E82113",
        "Alemanha":"#E8BD13",
        "Suíça":"#E81344",
        "Espanha":"#DE1B1B",
        "Costa do Marfim":"#D68213",
        "Brasil":"#F4FC56",
        "Japão":"#CF0E00",
        "Itália":"#2665AD",
        "Nigéria":"#0EB02C",
        "Inglaterra":"#DECED0",
        "França":"#185EA8",
        "Coreia do Sul":"#AB5F54",
        "Gana":"#8C8C8C",
        "México":"#17521C",
        "Croácia":"#A65858",
        "Bósnia e Herzegovina":"#6A89BD",
        "Portugal":"#B03C3C",
        "Rússia":"#A13618",
        "Equador":"#E8D71E",
        "Camarões":"#1F5714",
        "Uruguai":"#80CCFF",
        "Colômbia":"#94912F",
        "Costa Rica":"#99426D",
        "EUA":"#294663",
        "Grécia":"#47B4C9",
        "Austrália":"#E3E8B0",
        "Holanda":"#CC4B18",
        "Honduras":"#D6FBFF",
        "Argélia":"#DAFFD6",
        "Irã":"#616E5F"
    }
    
    //coloreJogos de acordo com o time que vem primeiro no ranking
    for (jogo in myChart.data) {
        times = myChart.data[jogo].Times.replace(" *","")
        times = times.split(" x ")
        cor_atual = []
        if (times.indexOf("Brasil") > -1) {
            cor_atual = [cores["Brasil"],"#091BAB"]
        } else {
            if (ranking.indexOf(times[0]) > ranking.indexOf(times[1])) {
                cor_atual = [cores[times[1]],cores[times[1]]]
            } else {
                cor_atual = [cores[times[0]],cores[times[0]]]
            }
            if (cor_atual[0] == "#DAFFD6") { //no caso da argélia
                cor_atual[1] = "#1E9E4F"
            }
        }
        
        myChart.assignColor(myChart.data[jogo].Times,cor_atual[0],cor_atual[1])

    }
    
    
    return myChart;
}

function arrumaTolltipJogos(chart) {
    chart.series[0].getTooltipText = function (e) {
        //pega o nome
        var nome = e.aggField[0]
        //filtra o dado do gráfico e pega o time do jogador
        var time = chart.data.filter(function (a) { return a["Times"] == nome})[0]["Times"]
        
        item = null
        for (i in chart.data) {
            if (chart.data[i].Times == time) {
                item = chart.data[i]
                break
            }
        }
        if (window.recorteJogo.indexOf("Distância") > -1) {
            return [
            item["time1"]+": "+(Math.round(item[window.recorteJogo+"1"]/100)/10)+" km",
            item["time2"]+": "+(Math.round(item[window.recorteJogo+"2"]/100)/10)+" km",
            "Total de "+window.recorteJogo+": "+(Math.round(e.xValue/100)/10)+" km"
            ];            
        } else {
            return [
            item["time1"]+": "+item[window.recorteJogo+"1"],
            item["time2"]+": "+item[window.recorteJogo+"2"],
            "Total de "+window.recorteJogo+": "+ e.xValue
            ];
        }
        
    };
    return chart;

}
function inicializaJogos() {
    //checa se tem variavel na url
    //se tiver, coloca o recorteJogo como ela e muda a option
    variaveis = getUrlVars()

    if ("recorte" in variaveis) {
        var recorteJogo = variaveis["recorte"];
        jQuery('#recorteJogo').val(recorteJogo);
    }
    //se não tiver, coloca Gols mesmo
    else {
        var recorteJogo = "Gols";
    }
        
    //faz o mesmo com a ordem_jogo
    if ("ordem_jogo" in variaveis) {
            var ordem_jogo = variaveis["ordem_jogo"];
            jQuery('#ordem_jogo').val(ordem_jogo);
            jQuery('input[name="ordem_jogo"][value="' + ordem_jogo + '"]').prop('checked', true);
            jQuery('input[name="ordem_jogo"][value!="' + ordem_jogo + '"]').prop('checked', false);
        }
        //se não tiver, coloca total mesmo
        else {
            var ordem_jogo = "Decrescente";
    }
    
    
    window.recorteJogo = recorteJogo;
    window.ordem_jogo = ordem_jogo;

    //carrega os dados e cria o gráfico
    d3.csv("https://s3-sa-east-1.amazonaws.com/blogedados/javascripts/copa_2014/grafico_jogos.csv", function (data) {
    window.jogos_data = data;
    desenhaGraficoJogos();
    });
}

function colocaOrdemJogos(chart) {
    //coloca bold no texto dos jogos com Brasil
    jogadores_BR = chart.data.filter(function (a) { return a["Times"].indexOf("Brasil") > -1 });

    for (j in jogadores_BR) {
        jQuery("#jogos").find("text:contains('Brasil')").css({'font-weight':'bold'});
    }

    //achar ordem_jogo dos jogadores
    jogadores = []
    nomes = jQuery("#jogos").find(".dimple-axis").find("text[x=-9]").each(
        function() {
            if (jQuery(this).text()) {
                jogadores.push(jQuery(this).text());
            }
        }
    );
    
    //coloca o número na frente de cada jogador
   for (var i = 0; i < jogadores.length;i++) {
        jQuery("#jogos").find('text:contains("'+jogadores[i]+'")').text((jogadores.length - i) + " - " +jogadores[i]);
        
    //muda tamanho do texto
    jQuery("#jogos").find("text").css({"font-size":"12px"})
        
        
    }
}

function arrumaNomesJogos() {
    jQuery("#jogos").find("text:contains('Costa do Marfim')").each(function () {
        jQuery(this).text(jQuery(this).text().replace("Costa do Marfim","C. Marfim"))
    })
    jQuery("#jogos").find("text:contains('Bósnia e Herzegovina')").each(function () {
        jQuery(this).text(jQuery(this).text().replace("Bósnia e Herzegovina","Bósnia"))
    })
    jQuery("#jogos").find("text:contains('Coreia do Sul')").each(function () {
        jQuery(this).text(jQuery(this).text().replace("Coreia do Sul","Coreia"))
    })    
    
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}


