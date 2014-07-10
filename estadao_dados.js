var complete_dataSelecoes = null;

function mudaRecorteSelecoes() {
    //pega o valor
    recorte = jQuery("#recorte_selecoes").val();
    
    //deleta o svg
	jQuery("#selecoes").replaceWith('<div id="selecoes"></div>');
	desenhaGraficoSelecoes(recorte);
}

function desenhaGraficoSelecoes(recorte)    {
      var svg = dimple.newSvg("#selecoes", 950, 700);
      data = window.complete_dataSelecoes
      var myChart = new dimple.chart(svg, data);
      myChart.setBounds(110, 30, 600, 600);
      var x = myChart.addMeasureAxis("x", recorte);
      
      var y = myChart.addCategoryAxis("y", "time");
      //retira o título do eixo Y
      y.title = ""
      series = myChart.addSeries("time", dimple.plot.bar);
      //ordena diferente se o recorte for Ranking
      if (["Ranking","Minutos para cada gol"].indexOf(recorte) >= 0) { 
          y.addOrderRule(recorte,true) 
      }  else { y.addOrderRule(recorte,false) }
      
      //tira ticks se for saldo
      if (recorte == "Saldo de Gols") {
          y.showGridlines = false
      }
      series.barGap = 0.42;
      
      myChart = coloreSelecoes(myChart)
      myChart.draw();
      
      arrumaNomesSelecoes(recorte)
      arrumaMediaSelecoes(recorte)
      
}

function coloreSelecoes(chart) {
    //uma cor para cada time. o Brasil tem duas por causa do stroke
     chart.assignColor("Argentina","#22C5F2");
     chart.assignColor("Bélgica","#8F433D");
     chart.assignColor("Chile","#E82113");
     chart.assignColor("Alemanha","#E8BD13");
     chart.assignColor("Suíça","#E81344");
     chart.assignColor("Espanha","#DE1B1B");
     chart.assignColor("Costa do Marfim","#D68213");
     chart.assignColor("Brasil","#F4FC56","#091BAB",1);
     chart.assignColor("Japão","#CF0E00");
     chart.assignColor("Itália","#2665AD");
     chart.assignColor("Nigéria","#0EB02C");
     chart.assignColor("Inglaterra","#DECED0");
     chart.assignColor("França","#185EA8");
     chart.assignColor("Coreia do Sul","#AB5F54");
     chart.assignColor("Gana","#8C8C8C");
     chart.assignColor("México","#17521C");
     chart.assignColor("Croácia","#A65858");
     chart.assignColor("Bósnia e Herzegovina","#6A89BD");
     chart.assignColor("Portugal","#B03C3C");
     chart.assignColor("Rússia","#A13618");
     chart.assignColor("Equador","#E8D71E");
     chart.assignColor("Camarões","#1F5714");
     chart.assignColor("Uruguai","#80CCFF");
     chart.assignColor("Colômbia","#94912F");
     chart.assignColor("Costa Rica","#99426D");
     chart.assignColor("EUA","#294663");    
     chart.assignColor("Grécia","#47B4C9");
     chart.assignColor("Austrália","#E3E8B0");
     chart.assignColor("Holanda","#CC4B18");
     chart.assignColor("Honduras","#D6FBFF");
     chart.assignColor("Argélia","#DAFFD6","#1E9E4F");
     chart.assignColor("Irã","#616E5F");
      
     return chart
}
function inicializa_selecoes() {
    //checa se tem variavel na url
    //se tiver, coloca o recorte como ela e muda a option
    variaveis = getUrlVars()
    if ("recorte" in variaveis) {
        recorte = variaveis["recorte"]
        jQuery('#recorte_selecoes').val(recorte)
    }
    //se não tiver, coloca Ranking mesmo
    else {
        recorte = "Ranking"
    }

    //cria o svg
    var svg = dimple.newSvg("#selecoes", 950, 700);
    //carrega os dados e cria o gráfico
    d3.csv("https://s3-sa-east-1.amazonaws.com/blogedados/javascripts/copa_2014/grafico_times.csv", function (data) {
//    d3.csv("grafico_times.csv", function (data) {
        window.complete_dataSelecoes = data
      var myChart = new dimple.chart(svg, data);
      myChart.setBounds(110, 30, 600, 600);
      myChart.addMeasureAxis("x", recorte);
      var y = myChart.addCategoryAxis("y", "time");
      //retira o título do eixo Y
      y.title = ""
      series = myChart.addSeries("time", dimple.plot.bar);
      //ordena diferente se o recorte for Ranking
      if (["Ranking","Minutos para cada gol"].indexOf(recorte) >= 0) { 
          y.addOrderRule(recorte,true) 
      }  else { y.addOrderRule(recorte,false) }
      series.barGap = 0.42;
      
      //arruma as cores
      myChart = coloreSelecoes(myChart)
      myChart.draw();
            
      arrumaNomesSelecoes(recorte)
      arrumaMediaSelecoes(recorte)
    });
}

function arrumaNomesSelecoes(recorte) {
    data = window.complete_dataSelecoes
    
    if (recorte == "Minutos para cada gol") {
        data.sort(function (a,b) {return a[recorte]-b[recorte]})
        console.log(data)
    }
    
    //coloca bold no texto do Brasil
    jQuery("#selecoes").find('text:contains("Brasil")').css({'font-weight':'bold'})
    
    //arruma nome das seleções
    jQuery("#selecoes").find('text:contains("Costa do Marfim")').text("C. Marfim");
    jQuery("#selecoes").find('text:contains("Bósnia e Herzegovina")').text("Bósnia");
    jQuery("#selecoes").find('text:contains("Coreia do Sul")').text("Coreia");
    
    //muda tamanho do texto
    jQuery("#selecoes").find("text").css({"font-size":"12px"})
    
    //achar ordem das seleções
    //começa pegando o nome de todas as seleções e a ordem delas
    var selecoes = []
    var ordem = []
    var ranking = []
    for (i in data) {
        selecoes.push(data[i].time)
        ordem.push(data[i][recorte])
    }
    
    //cria um array ranking com a ordem para ser colocada
    for (var i = 0; i< ordem.length;i++) {
        var p = i + 1
        ranking[i] = p
        var j = 1
        while (ordem[i]==ordem[i+j]) {
            ranking[i+j] = p
            j++
        }
        i = i+ (j-1)
        
    }
        
    //coloca o número na frente de cada time
    if (recorte != "Ranking") {
        //arruma as selecoes que tiveram os nomes mudados
        selecoes[selecoes.indexOf("Bósnia e Herzegovina")] = "Bósnia"
        selecoes[selecoes.indexOf("Costa do Marfim")] = "C. Marfim"
        selecoes[selecoes.indexOf("Coreia do Sul")] = "Coreia"
        
        var numero = 0
        for (var i = 0; i < selecoes.length;i++) {
            numero = ordem[i]
            jQuery("#selecoes").find('text:contains("'+selecoes[i]+'")').text(ranking[i] + " - " +selecoes[i]);
        }
    } else if (recorte == "Ranking"){
        //regra diferente pro ranking
        data.sort(function(a, b){return b[recorte]-a[recorte]});
        
        for (var i = 0; i < selecoes.length;i++) {
            posicao = data.filter(function (a) { return a["time"] == selecoes[i]})[0]["Ranking"] 
            jQuery("#selecoes").find('text:contains("'+selecoes[i]+'")').text(parseInt(posicao) + " - " +selecoes[i])
         }        
    }
}

function arrumaMediaSelecoes(recorte) {
    //se o recorte for algum desses:
    if (["Mordidas","Pontos","Saldo de Gols","Ranking","Gols","Gols Sofridos"].indexOf(recorte) >= 0) {
        jQuery("#media_selecoes").hide()
        jQuery("#total_selecoes").show()
    }
    else {
        jQuery("#total_selecoes").hide()
        jQuery("#media_selecoes").show()    
    }
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}


inicializa_selecoes()
