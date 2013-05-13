var Dashboard = {
	highlightingErrors: function() {
		$('div.service-info').each(function() {
            var bar = $(this).find('span.service-hist-wrap');
            var problems_count = $(bar).attr('data-have-problems');
            if (parseInt(problems_count) !== 0) {
                $.get(
                    '/get-bar-chart/' + $(bar).attr('sid'),
                    function(response) {
                        $(bar).html(response);
                        if ($(bar).find('span.hist-part:last', response).hasClass('hist-err')) {
                            $(bar).parent('div.service-info').addClass('mark');
                        }
                        $(bar).find('span.hist-part').each(function() {
                            if ($(this).hasClass('hist-err')) {
                                var probe = $(this);
                                $(probe).click(function() {
                                    $('span.hist-err').each(function() {
                                        if ($(this).hasClass('has-info')) {
                                            if ($(probe).attr('id') != $(this).attr('id')) {
                                                $(this).popover('hide');
                                                $(this).removeClass('popover-open');
                                            }
                                        }
                                    });
                                    if (!$(probe).hasClass('has-info')) {
                                        $.get(
                                            '/get-probe-details/' + $(probe).attr('id'),
                                            function(details) {
                                                $(probe).addClass('has-info');
                                                $(probe).popover({
                                                    'html': true,
                                                    'trigger': 'manual',
                                                    'content': details,
                                                    'placement': 'bottom'
                                                });
                                                $(probe).popover('show');
                                                $(probe).addClass('popover-open');
                                            }
                                        );
                                    } else {
                                        if ($(probe).hasClass('popover-open')) {
                                            $(probe).popover('hide');
                                            $(probe).removeClass('popover-open');
                                        } else {
                                            $(probe).popover('show');
                                            $(probe).addClass('popover-open');
                                        }
                                    }
                                });
                            }
                        });
                    }
                );
             } else {
                var chart_element = '<span class="hist-part"></span>';
                var chart_elements = '';
                for(i = 0; i < 60; i++){
                    chart_elements += chart_element;
                }
                $(bar).html(chart_elements);
             }
        });
	}
};

$(document).ready(function() {
	Dashboard.highlightingErrors();
});
