var data_jogador = null,
time_jogador = null,
recorte_jogador = null,
posicao_jogador = null,
ordem_jogador = "Decrescente";
jogo_jogador = null

function mudaRecorte() {
    //pega o valor
    var recorte = jQuery("#recorte").val();
    window.recorte_jogador = recorte
    
    //reseta radio da média para total
    jQuery('input[name="media"][value!="media"]').prop('checked', false);
    jQuery('input[name="media"][value="total"]').prop('checked', true);
    
    redesenhaGrafico();
}

function mudaAgrupa() {
    //pega o valor
    var time = jQuery("#time").val();
    window.time_jogador = time;
    window.jogo_jogador = "Todos";
    mostraJogoJogador();
    redesenhaGrafico();
}

function mudaPosicao() {
    //pega o valor
    var posicao = jQuery("#posicao").val();
    window.posicao_jogador = posicao;

    redesenhaGrafico();
}

function mudaMedia(el) {
    //passa o valor
    media = el.value
    window.media = media;
    recorte = window.recorte_jogador
    //ativa ou reativa o radio
    jQuery(el).prop('checked',true);
    jQuery('input[name="media"][value!="' + media + '"]').prop('checked', false);
    
    //muda o nome da variável se for necessário
    if (media == "media") {
        recorte = recorte + " - Média"
    } else {
        recorte = recorte.replace(" - Média","")
    }
    window.recorte_jogador = recorte
	redesenhaGrafico();
    
}

function mudaOrdem(el){
    //pega o valor
    var ordem = el.value;
    window.ordem_jogador = ordem;
    jQuery(el).prop('checked',true);
    jQuery('input[name="ordem"][value!="' + ordem + '"]').prop('checked', false);

    redesenhaGrafico();
}

function mudaJogoJogador() {
    //pega o valor
    var jogo_jogador = jQuery("#jogo_jogador").val();
    window.jogo_jogador = jogo_jogador;
    
    redesenhaGrafico();
    
}

function redesenhaGrafico(){
    //deleta o svg
    jQuery("#jogador").replaceWith('<div id="jogador"></div>');
    desenhaGrafico();
}

function ordenaDados(a, b){
    if (window.ordem_jogador == "Crescente") {
        return a[window.recorte_jogador] - b[window.recorte_jogador];
    } else {
        return b[window.recorte_jogador] - a[window.recorte_jogador];
    }
}

function desenhaGrafico()    {
    //pega as variáveis
    var recorte = window.recorte_jogador,
        time = window.time_jogador,
        data = window.data_jogador,
        ordem = window.ordem_jogador;
        posicao = window.posicao_jogador;
        jogo_jogador = window.jogo_jogador;

    //vê se há agrupamento por time
    if (time != "total") {
        data = dimple.filterData(data,"time",time);
    }
    //vê se há agrupamento por posição
    if (posicao != "total") {
        data = dimple.filterData(data,"posicao",posicao);
    }
    
    // agora por jogo
    data = dimple.filterData(data,"adversario",jogo_jogador)

    //desenha o gráfico
    var svg = dimple.newSvg("#jogador", 950, 700);

    //elimina todos com zero
    data = data.filter(function(a){return a[recorte] > 0;});

    //descobre o valor máximo
    var maximo_x = d3.max(data, function(d) {
        return parseFloat(d[recorte]);
    }); 
    
    //pega os 32 top
    data.sort(ordenaDados);
    data = data.slice(0,32);

    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(140, 30, 600, 600);
    var x = myChart.addMeasureAxis("x", recorte);
    
    //bota o tamanho máximo de x (para igualar ordem crescente ou decrescente)
    x.overrideMax = maximo_x;
    
    //coloca % se a variável pedir
    if (["Chutes convertidos em gols (%)","Acerto de chutes (%)"].indexOf(recorte)>=0) {
        x.tickFormat = "%";
    }
    
    x.ticks = 5;
    
    var y = myChart.addCategoryAxis("y", "nome");
    //retira o título do eixo Y
    y.title = "";
    var series = myChart.addSeries("nome", dimple.plot.bar);
    
    series.barGap = 0.42;
    
    if (ordem == "Decrescente") {
        y.addOrderRule(recorte,false);
    } else {
        y.addOrderRule(recorte,true);
    }

    //arruma o gráfico
    myChart = colore(myChart);
    myChart = arrumaTolltip(myChart);

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
    return myChart;
}

function arrumaTolltip(chart) {
    chart.series[0].getTooltipText = function (e) {
        //pega o nome
        var nome = e.aggField[0]
        //filtra o dado do gráfico e pega o time do jogador
        var time = chart.data.filter(function (a) { return a["nome"] == nome})[0]["time"]

        return [
           window.recorte_jogador+": "+ e.xValue ,
           "Time: "+ time
        ];
    };
    return chart;

}
function inicializa() {
    //checa se tem variavel na url
    //se tiver, coloca o recorte como ela e muda a option
    variaveis = getUrlVars()

    if ("recorte" in variaveis) {
        var recorte = variaveis["recorte"];
        jQuery('#recorte').val(recorte);
    }
    //se não tiver, coloca Gols mesmo
    else {
        var recorte = "Gols";
    }
        
    //faz o mesmo com o time
    if ("time" in variaveis) {
            var time = variaveis["time"];
            jQuery('#time').val(time);
        }
        //se não tiver, coloca total mesmo
        else {
            var time = "total";
    }

    //faz o mesmo com a posicao
    if ("posicao" in variaveis) {
            var posicao = variaveis["posicao"];
            jQuery('#posicao').val(posicao);
        }
        //se não tiver, coloca total mesmo
        else {
            var posicao = "total";
    }

    //faz o mesmo com a ordem
    if ("ordem" in variaveis) {
            var ordem = variaveis["ordem"];
            jQuery('#ordem').val(ordem);
            jQuery('input[name="ordem"][value="' + ordem + '"]').prop('checked', true);
            jQuery('input[name="ordem"][value!="' + ordem + '"]').prop('checked', false);
        }
        //se não tiver, coloca total mesmo
        else {
            var ordem = "Decrescente";
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
    
    //faz o mesmo com a posicao
    if ("contra" in variaveis) {
            var jogo_jogador = variaveis["contra"];
            jQuery('#jogo_jogador').val(jogo_jogador);
        }
        //se não tiver, coloca total mesmo
        else {
            var jogo_jogador = "Todos";
    }
    
    
    window.media = media;
    window.recorte_jogador = recorte;
    window.time_jogador = time;
    window.posicao_jogador = posicao;
    window.ordem_jogador = ordem;
    window.jogo_jogador = jogo_jogador;
    
    //mostra ou não mostra os radios de total e média
    mostraRadios()
    
    //carrega os dados e cria o gráfico
    //d3.csv("grafico_jogadores.csv", function (data) {
 d3.csv("https://s3-sa-east-1.amazonaws.com/blogedados/javascripts/copa_2014/grafico_jogadores.csv", function (data) {
    window.data_jogador = data;
    mostraJogoJogador(); 
    desenhaGrafico();
    });
}

function colocaOrdem(chart) {
    //coloca bold no texto dos jogadores do Brasil
    jogadores_BR = chart.data.filter(function (a) { return a["time"] == "Brasil"});
    for (j in jogadores_BR) {
        jQuery("#jogador").find('text:contains("'+jogadores_BR[j]["nome"]+'")').css({'font-weight':'bold'});
    }

    //achar ordem dos jogadores
    jogadores = []
    nomes = jQuery("#jogador").find(".dimple-axis").find("text[x=-9]").each(
        function() {
            if (jQuery(this).text()) {
                jogadores.push(jQuery(this).text());
            }
        }
    );

    //coloca o número na frente de cada jogador
   for (var i = 0; i < jogadores.length;i++) {
        jQuery("#jogador").find('text:contains("'+jogadores[i]+'")').text((jogadores.length - i) + " - " +jogadores[i]);
    }
    
    //muda tamanho do texto
    jQuery("#jogador").find("text").css({"font-size":"12px"})
    
}

function mostraRadios() {
    //vê quais são nossos agrupamentos
    var media = window.media
    var recorte = window.recorte_jogador
    var jogo_jogador = window.jogo_jogador
    
    //se recorte estiver com média, tira
    recorte = recorte.replace(" - Média","")
    
    var variaveis_com_media = ['Assistências', 'Bloqueios', 'Carrinhos', 'Chutes Certos', 'Chutes ao gol', 'Cruzamentos', 'Faltas Cometidas', 'Faltas Sofridas', 'Gols', 'Impedimentos', 'Passes', 'Roubadas']
    
    if (variaveis_com_media.indexOf(recorte) >= 0) {
        if (jogo_jogador == "Todos") {
            jQuery("#total_media").show()
        } else {
            jQuery("#total_media").hide()
        }
    } else { 
        jQuery("#total_media").hide()
    }
}

function mostraJogoJogador() {
    var data = window.data_jogador
    var time  = window.time_jogador
    var jogo_jogador = window.jogo_jogador
    if (time == "total") {
        jQuery(".seletor-jogo").hide()
        
    } else {
        novo_dado =  data.filter(function (a) { return (a["time"] == time)})
        adversarios = dimple.getUniqueValues(novo_dado,"adversario")

        jQuery('#jogo_jogador')
            .find('option')
            .remove()
            .end()
        
        adversarios.forEach(function(e){
            jQuery('#jogo_jogador')
                .append('<option value="'+e+'">'+e+'</option>')
            
        })
                
        jQuery(".seletor-jogo").show()        
    }
    
    jQuery('#jogo_jogador').val(jogo_jogador)
    
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}
