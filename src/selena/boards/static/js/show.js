var Show = {
    PlotLastHourResponseTime: function(group_id, probes){
        return $.jqplot(group_id,  [probes], {
            fontSize: '9px',
            legend: {
                show: true
            },
            series: [
                {
                    showMarker: false,
					label: 'RESPONSE TIME'
                }
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    label: 'When',
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {
                        angle: 60
                    }
                },
                yaxis: {
                    autoscale:true,
                    label: 'Response time',
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {}
                },
            }
        });
	},

	PlotOtherLastHourTimes: function(group_id, namelookup_probes, connect_time_probes, starttransfer_time_probes) {
        return $.jqplot(group_id,  [namelookup_probes, connect_time_probes, starttransfer_time_probes], {
            legend: {show: true},
            series:[
                {
                    showMarker: false,
					label: 'NAMELOOKUP TIME'
				},
                {
                    showMarker: false,
                    label: 'CONNECT TIME'
                },
                {
                    showMarker: false,
                    label: 'STARTTRANSFER TIME'
                }
            ],
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    label: 'When',
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {
                        angle: 60
                    }
                },
                yaxis: {
                    autoscale:true,
                    label: 'Time',
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                    tickOptions: {}
                },
            }
        });
	},

    BaseTimesPlotsTabs: function(charts) {
        $('#base_times_tabs li a').click(function() {
            $(this).tab('show');
            charts[$(this).attr('plot')].destroy();
            charts[$(this).attr('plot')].draw();

            return false;
        });
    },

    OtherTimesPlotsTabs: function(plots) {
        $('#last_hour_times_tabs li a').click(function() {
            $(this).tab('show');
            plots[$(this).attr('plot')].destroy();
            plots[$(this).attr('plot')].draw();

            return false;
        });
    }
}
