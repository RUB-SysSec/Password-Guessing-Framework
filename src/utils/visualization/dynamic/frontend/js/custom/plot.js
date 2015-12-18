var ADRESS = "localhost";
var PORT = "31338";
var NO_OF_JOBS = 0;

function create_table() {
    'use strict';
    $.get('/results/jobs.json', function(data) {
        create_table_rows(data)
    });
}


function create_table_rows(data) {
    NO_OF_JOBS = data.jobs.length;
    var table_body = document.getElementById("table_body");
    var job_counter = -1;
    var job;
    data.jobs.forEach(function(job) {
        job_counter++
        var tr = document.createElement('TR');
        td = document.createElement('TD');
        td.id = "job_counter_".concat(job_counter);
        td.appendChild(document.createTextNode(job_counter+1));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "label_".concat(job_counter);
        td.appendChild(document.createTextNode(job.label));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "training_file_".concat(job_counter);
        td.appendChild(document.createTextNode(job.training_file));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "pw_file_".concat(job_counter);
        td.appendChild(document.createTextNode(job.pw_file));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "pw_format_".concat(job_counter);
        td.appendChild(document.createTextNode(job.pw_format));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "success_rate_".concat(job_counter);
        td.appendChild(document.createTextNode("Pending"));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "status_".concat(job_counter);
        td.appendChild(document.createTextNode("Pending"));
        tr.appendChild(td);
        td = document.createElement('TD');
        td.id = "runtime_".concat(job_counter);
        td.appendChild(document.createTextNode(job.runtime));
        tr.appendChild(td);
        table_body.appendChild(tr);
    });
}



function request_jobs_json() {
    'use strict';
    $.get('/results/jobs.json', function(data) {
        for (var i=0; i<data.jobs.length; i++) {
            document.getElementById('runtime_'.concat(i)).innerHTML = data.jobs[i].runtime;
        }
        request_job_data(data.plot_file)
        });
}


function request_job_data(plot_file) {
    'use strict';
    var options = {
        chart: {
            renderTo: 'container',
            type: 'line',
            events: {
                load: function () {
                    var theSeries = this.series;
                    $.each(theSeries, function () {
                        if (this.index < theSeries.length-4) {
                            this.setVisible(false);
                        }
                    });
                }
            }
        },
        title: {
            text: 'Guessing Comparison'
        },
        xAxis: {
            min: 0,
            categories: []
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Percentage Found'
            }
        },
        tooltip: {
            crosshairs: true,
            shared: false,
            valueSuffix: '',
            headerFormat: '{series.name}: <b>{point.y} %</b><br>{point.x} Guesses<br>',
            pointFormat: ''
        },
        legend: {
            enabled: true
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: false
                },
                enableMouseTracking: true
            }
        },
        series: []
    };
    $.get('/results/'+plot_file, function(data) {
        // Split the lines
        var lines = data.replace(/^\s+|\s+$/g,"").split('\n'); //Fix to ingore last line data.split('\n');
        var header_length = 0;
        $.each(lines, function(lineNo, line) {
            var items = line.split(',');
            // header line containes categories
            if (lineNo == 0) {
                header_length = items.length;
                $.each(items, function(itemNo, item) {
                    if (itemNo > 0) options.xAxis.categories.push(item);
                });
            } else {
                if(items.length != header_length) {
                    document.getElementById('status_'.concat(lineNo-1)).innerHTML = "Running";      // current job is running
                } else {
                    document.getElementById('status_'.concat(lineNo-1)).innerHTML = "Done";
                }
                // the rest of the lines contain data with their name in the first position
                var series = { 
                    data: []
                };
                $.each(items, function(itemNo, item) {
                    if (itemNo == 0) {
                        series.name = item;
                    } else {
                        series.data.push(parseFloat(item));
                        document.getElementById('success_rate_'.concat(lineNo-1)).innerHTML = item;
                    }
                });
                options.series.push(series);
            }
        });
        var chart = new Highcharts.Chart(options);
    });
}

function notify(title, text, type) {
    var myStack = {
        'dir1': 'down',
        'dir2': 'left',
        'firstpos1': 25,
        'firstpos2': 25
    };
    new PNotify({
        title: title,
        title_escape: true,
        text: text,
        text_escape: true,
        icon: true,
        hide: true,
        delay: 3000,
        styling: 'bootstrap3',
        type: type, //error, warning, info
        addclass: 'stack-custom',
        stack: myStack,
        width: '400px'
    });
}

$(document).ready(function () {
    'use strict';
    var all_done = false
    //notify('Highcharts', 'Requested plot.csv', 'info')
    create_table()
    request_jobs_json()
    var loop = setInterval(function(){
        if (!all_done) {
            request_jobs_json()
            for (var i=0; i<NO_OF_JOBS; i++){
                if (document.getElementById('status_'.concat(i)).innerHTML != "Done") {
                    all_done = false
                } else {
                    all_done = true
                }
            }
        } else {
            request_jobs_json()         // last request to get runtime of last job
            clearInterval(loop)         // stop requesting the jobs.json when all jobs are done
        }
        //notify('Highcharts', 'Requested update of plot.csv', 'info')
    },15000);
    if (all_done) {
        
    }
});
