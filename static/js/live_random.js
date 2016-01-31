
function update_on (event_name, chart, callback) {
    event_name = event_name || 'msg';

    socket.on(event_name, function(msg) {
        console.log('on "' + event_name + '": ' + JSON.stringify(msg));
        callback(chart, msg);
    });
};


function update_timepoint (chart, msg) {
    var series = chart.series[0];
    var x = (new Date()).getTime(),
        y = (new Date()).getTime() % msg.timestamp;
    series.addPoint([x, y], true, true);
};



function create_time_series_chart() {
    $(document).ready(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        console.log('creating time-series chart');

        $('#time-series-chart').highcharts({
            chart: {
                type: 'spline',
                animation: Highcharts.svg, // don't animate in old IE
                marginRight: 10,
                events: {
                    load: function() { update_on('tweet', this, update_timepoint); }
                }
            },
            title: {
                text: 'Tweet.timestamp % Now.timestamp'
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {
                    text: 'Value'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            series: [{
                name: 'Random data',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -19; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 1000,
                            y: Math.random()
                        });
                    }
                    return data;
                }())
            }]
        });
    });
}

$(function() { create_time_series_chart() ; });