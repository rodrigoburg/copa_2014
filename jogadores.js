var complete_data = null;
var svg = null;

function mudaRecorte() {
    //pega o valor
    recorte = jQuery("#recorte").val();
    
    //deleta o svg
	jQuery("#jogador").replaceWith('<div id="jogador"></div>');
	desenhaGrafico(recorte);
}

function desenhaGrafico(recorte)    {
      var svg = dimple.newSvg("#jogador", 950, 520);
      data = window.complete_data
      var myChart = new dimple.chart(svg, data);
      myChart.setBounds(80, 30, 780, 405)
      myChart.addMeasureAxis("x", recorte);
      var y = myChart.addCategoryAxis("y", "nome");
      //retira o título do eixo Y
      y.title = ""
      series = myChart.addSeries("nome", dimple.plot.bar);
      y.addOrderRule(recorte,false)
      myChart = colore(myChart)
      myChart.draw();
      
      arrumaNomes()
}

function colore(chart) {
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
function inicializa() {
    
    //checa se tem variavel na url
    //se tiver, coloca o recorte como ela e muda a option
    variaveis = getUrlVars()
    if ("recorte" in variaveis) {
        recorte = variaveis["recorte"]
        jQuery('#recorte').val(recorte)
    }
    //se não tiver, coloca Gols mesmo
    else {
        recorte = "gols"
    }

    //cria o svg
    var svg = dimple.newSvg("#jogador", 950, 520);
    //carrega os dados e cria o gráfico
    d3.csv("jogador_stats_somado.csv", function (data) {
        window.complete_data = data
      var myChart = new dimple.chart(svg, data);
      myChart.setBounds(80, 30, 780, 405)
      myChart.addMeasureAxis("x", recorte);
      var y = myChart.addCategoryAxis("y", "nome");
      //retira o título do eixo Y
      y.title = ""
      series = myChart.addSeries("nome", dimple.plot.bar);
      y.addOrderRule(recorte,false)
      
      //arruma as cores
      myChart = colore(myChart)
      myChart.draw();
            
      arrumaNomes()
    });
}

function arrumaNomes() {
    //coloca bold no texto do Brasil
    jQuery("#jogador").find('text:contains("Brasil")').css({'font-weight':'bold'})
    
    //arruma nome das seleções
    jQuery("#jogador").find('text:contains("Costa do Marfim")').text("C. Marfim");
    jQuery("#jogador").find('text:contains("Bósnia e Herzegovina")').text("Bósnia");
    jQuery("#jogador").find('text:contains("Coreia do Sul")').text("Coreia");
    
    //achar ordem das seleções
    jogador = []
    nomes = jQuery("#jogador").find(".dimple-axis").find("text[x=-9]").each(
        function() {
            if (jQuery(this).text()) {
                jogador.push(jQuery(this).text())
            }
        }
    );
    
    //coloca o número na frente de cada time
   for (var i = 0; i < jogador.length;i++) {
        jQuery("#jogador").find('text:contains("'+jogador[i]+'")').text((jogador.length - i) + " - " +jogador[i]);
    }
}


function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}


inicializa()
