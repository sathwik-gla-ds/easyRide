chartColors = {
	red: 'rgba(255, 99, 132, 1)',
	orange: 'rgba(255, 159, 64, 1)',
	yellow: 'rgba(255, 205, 86, 1)',
	green: 'rgba(75, 192, 192, 1)',
	blue: 'rgba(54, 162, 235, 1)',
	purple: 'rgba(153, 102, 255, 1)',
	grey: 'rgba(201, 203, 207, 1)'
};

chartColorsTrans = {
  red: 'rgba(255, 99, 132, 0.5)',
	orange: 'rgba(255, 159, 64, 0.5)',
	yellow: 'rgba(255, 205, 86, 0.5)',
	green: 'rgba(75, 192, 192, 0.5)',
	blue: 'rgba(54, 162, 235, 0.5)',
	purple: 'rgba(153, 102, 255, 0.5)',
	grey: 'rgba(201, 203, 207, 0.5)',
};

function getRandom(arr, n) {
    var result = new Array(n),
        len = arr.length,
        taken = new Array(len);
    if (n > len)
        throw new RangeError("getRandom: more elements taken than available");
    while (n--) {
        var x = Math.floor(Math.random() * len);
        result[n] = arr[x in taken ? taken[x] : x];
        taken[x] = --len in taken ? taken[len] : len;
    }
    return result;
}

function line_chart_config(xy_data, title_name, xa_name, ya_name, step) {
var config = {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
        data: [],
        steppedLine: step,
        backgroundColor: chartColors.red,
				borderColor: chartColors.red,
        fill: false
      }]
  },
  options: {
    responsive: true,
    legend:{
      display:false
    },
    title: {
      display: true,
      text: title_name,
      fontSize: 20
    },
    tooltips: {
					mode: 'index',
					intersect: false,
				},
    hover: {
     mode: 'nearest',
     intersect: true
    },
    scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: xa_name
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: ya_name
						}
					}]
				}
  }
};
for (x of xy_data.data) {
  config.data.labels.push(x[0]);
  config.data.datasets[0].data.push(x[1]);
};
return config;

};

function bar_chart_config(xy_data, title_name, bar_type) {
  var config = {
				type: bar_type, //'bar', 'horizontalBar'
				data: {
    			labels: [],
    			datasets: [{
    				backgroundColor: chartColorsTrans.red,
				    borderColor: chartColors.red,
    				data: []
    			}]
    		},
				options: {
					elements: {
						rectangle: {
							borderWidth: 2,
						}
					},
					responsive: true,
					legend: {
						display:false,
					},
					title: {
						display: true,
						text: title_name,
            fontSize: 20
					},
			    scales: {
								xAxes: [{
									display: true,
									ticks: {
                    min: 0,
										suggestedMax: 10
                }
								}]
							}
				}
			}
      for (x of xy_data.data) {
        config.data.labels.push(x[0]);
        config.data.datasets[0].data.push(x[1]);
      };
return config;

}

function pie_chart_config(xy_data, title_name, pie_type, size) {
  var config = {
			type: pie_type, //'pie', 'doughnut'
			data: {
				datasets: [{
					data: [],
					backgroundColor: getRandom(Object.values(chartColors), xy_data.data.length),
				}],
				labels: []
			},
			options: {
				responsive: true,
				legend: {
					position: 'top',
				},
				title: {
					display: true,
					text: title_name,
          fontSize: 20
				},
				animation: {
					animateScale: true,
					animateRotate: true
				}
			}
		};

 for (x of xy_data.data) {
   config.data.labels.push(x[0]);
   config.data.datasets[0].data.push(x[1]);
 };

if (size == 'full'){
  config.options.circumference = 2 * Math.PI;
		config.options.rotation = -Math.PI / 2;
} else {
  config.options.circumference = Math.PI;
			config.options.rotation = -Math.PI;
}

return config
}

function radar_chart_config(xy_data, label, title_name){
  var config = {
			type: 'radar',
			data: {
				labels: [],
				datasets: [{
					label: label[0],
					backgroundColor: chartColorsTrans.red,
					borderColor: chartColors.red,
					pointBackgroundColor: chartColors.red,
					data: []
				}, {
					label: label[0],
					backgroundColor: chartColorsTrans.blue,
					borderColor: chartColors.blue,
					pointBackgroundColor: chartColors.blue,
					data: []
				}]
			},
			options: {
				legend: {
					position: 'top',
				},
				title: {
					display: true,
					text: title_name,
          fontSize: 20
				},
				scale: {
					ticks: {
						beginAtZero: true
					}
				}
			}
		};
    for (x of xy_data[0].data) {
      config.data.labels.push(x[0]);
      config.data.datasets[0].data.push(x[1]);
    };
    for (x of xy_data[1].data) {
      config.data.datasets[1].data.push(x[1]);
    };
return config
}
