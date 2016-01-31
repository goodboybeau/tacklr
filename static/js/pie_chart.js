var slices = [{  name: "Microsoft Internet Explorer",
                y: 56.33
            }, {
                name: "Chrome",
                y: 24.03,
                sliced: true,
                selected: true
            }, {
                name: "Firefox",
                y: 10.38
            }, {
                name: "Safari",
                y: 4.77
            }, {
                name: "Opera",
                y: 0.91
            }, {
                name: "Proprietary or Undetectable",
                y: 0.2
            }];

var update_pie = function(chart) {

    setInterval(function() {
        console.log('updating pie chart');
        var diff = Math.random() * 10;
        _slices = chart.series[0];
        for( var i=0; i<_slices.data.length; i++)
        {
            if (_slices.data[i].y > diff)
            {
                var old = _slices.data[i].y;
                _slices.data[i].update(old - diff);
                if(i<_slices.data.length-1)
                {
                    old = _slices.data[i+1].y;
                    _slices.data[i+1].update(old+diff);
                }
                else
                {
                    old = _slices.data[0].y;
                    _slices.data[0].update(old+diff);
                }
                break;
            }
        }

    }, 2000); };

var _slices = [];



var create_pie_chart = function(div_id, data, chart_text) {

    data = data || slices;
    console.log('creating pie chart in div #' + div_id + ' with data: ' + data);

    $("#container").append('<div id="' + div_id + '" class="chart-in-grid"></div>');


        var chartingOptions = {
            chart: {
                renderTo: div_id,
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie',
//                events: {
//                   load: function() {
//
//                        socket.on('tweet', function(msg) {
//                            var _exists = false;
//                            for(var i=0; i<_slices.length; i++)
//                            {
//                                if(_slices[i].name == msg.user)
//                                {
//                                    _slices[i] = {name:_slices[i].name, y:_slices[i].y + 1};
//                                    _exists = true;
//                                    break;
//                                }
//                            }
//
//                            if(!_exists)
//                            {
//                                var data = {name:msg.user, y:1};
//                                console.log(data);
//                                _slices.push(data);
//                            }
//
//                            if(!chart.series)
//                            {
//                                return;
//                            }
//
//                            this.series[0].setData({});
//                            this.series[0].setData(_slices);
//                            });
//                            console.log();
//
//                        }
//
            },
            title: {
                text: chart_text
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: "Brands",
                colorByPoint: true,
                data: data
            }]
        };

        console.log("JSON: " + JSON.stringify(chartingOptions));
        console.log("Render to element with ID : " + chartingOptions.chart.renderTo);
        console.log("Number of matching dom elements : " + $("#" + chartingOptions.chart.renderTo).length);


    Highcharts.Chart.prototype.callbacks.push(push_update_pie);
    var chart = new Highcharts.Chart(chartingOptions);
    console.log('chart ' + (chart))
    chart.chart.events.load = function() { push_update_pie(chart) };

    return chart;
}
var charts = [];
$(function () {
    console.log('create');
    create_pie_chart('ppi');

    socket.on('tweet uniqueness', function(tweet_data) {
        console.log('tweet uniqueness');
        console.log(JSON.stringify(tweet_data));
        create_pie_chart(tweet_data['id_str'] || ''+(new Date()).getTime(), tweet_data['highcharts_data'], tweet_data['text']);
    })
});

