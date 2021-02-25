// Custom color rgb values for the charts
chartColors = {
    red: 'rgba(255, 99, 132, 1)',
    orange: 'rgba(255, 159, 64, 1)',
    yellow: 'rgba(255, 205, 86, 1)',
    green: 'rgba(75, 192, 192, 1)',
    blue: 'rgba(54, 162, 235, 1)',
    purple: 'rgba(153, 102, 255, 1)',
    grey: 'rgba(201, 203, 207, 1)'
};
// Custom color rgb values with some transperacy for the charts
chartColorsTrans = {
    red: 'rgba(255, 99, 132, 0.5)',
    orange: 'rgba(255, 159, 64, 0.5)',
    yellow: 'rgba(255, 205, 86, 0.5)',
    green: 'rgba(75, 192, 192, 0.5)',
    blue: 'rgba(54, 162, 235, 0.5)',
    purple: 'rgba(153, 102, 255, 0.5)',
    grey: 'rgba(201, 203, 207, 0.5)',
};


// Function to choose a random number of elements in an array. Used in pie charts for choosing the colors
function getRandom(arr, n)
{
    var result = new Array(n),
        len = arr.length,
        taken = new Array(len);
    if (n > len)
        throw new RangeError("getRandom: more elements taken than available");
    while (n--)
    {
        var x = Math.floor(Math.random() * len);
        result[n] = arr[x in taken ? taken[x] : x];
        taken[x] = --len in taken ? taken[len] : len;
    }
    return result;
}


//=========//
// Configs //
//=========//

// Function for getting the line chart config file in the required format for the chart.js library
function line_chart_config(xy_data, title_name, xa_name, ya_name, step)
{
    var config = {
        type: 'line',
        data:
        {
            labels: [], //X axis labels
            datasets: [
            {
                data: [], //Y axis data to be plotted
                steppedLine: step, //true, false - Stepped line or curvy
                backgroundColor: chartColors.red,
                borderColor: chartColors.red,
                fill: false // TO fill the area with the graph
            }]
        },
        options:
        {
            responsive: true,
            legend:
            {
                display: false
            },
            title:
            {
                display: true,
                text: title_name, // Graph Title name
                fontSize: 20
            },
            tooltips:
            {
                mode: 'index',
                intersect: false,
            },
            hover:
            {
                mode: 'nearest',
                intersect: true
            },
            scales:
            {
                xAxes: [
                {
                    display: true,
                    scaleLabel:
                    {
                        display: true,
                        labelString: xa_name // X-axis label name
                    }
                }],
                yAxes: [
                {
                    display: true,
                    scaleLabel:
                    {
                        display: true,
                        labelString: ya_name // Y-axis label name
                    }
                }]
            }
        }
    };
    // Fill in the data to the above config object
    for (x of xy_data.data)
    {
        config.data.labels.push(x[0]); // Add the X-axis labels
        config.data.datasets[0].data.push(x[1]); // Add the data to be plotted
    };
    //Return the config file
    return config;
};


// Function for getting the bar chart config file in the required format for the chart.js library
function bar_chart_config(xy_data, title_name, bar_type)
{
    var config = {
        type: bar_type, //'bar', 'horizontalBar'
        data:
        {
            labels: [],
            datasets: [
            {
                backgroundColor: chartColorsTrans.red,
                borderColor: chartColors.red,
                data: []
            }]
        },
        options:
        {
            elements:
            {
                rectangle:
                {
                    borderWidth: 2,
                }
            },
            responsive: true,
            legend:
            {
                display: false,
            },
            title:
            {
                display: true,
                text: title_name, // Title name
                fontSize: 20
            },
            scales:
            {
                xAxes: [
                {
                    display: true,
                    ticks:
                    {
                        min: 0,
                        suggestedMax: 10
                    }
                }]
            }
        }
    }
    // Fill in the data to the above config object
    for (x of xy_data.data)
    {
        config.data.labels.push(x[0]); // Push in the labels
        config.data.datasets[0].data.push(x[1]); // Push in the values
    };
    return config; // Return the config file

}


// Function for getting the pie/doughnut chart config file in the required format for the chart.js library
function pie_chart_config(xy_data, title_name, pie_type, size)
{
    var config = {
        type: pie_type, //'pie', 'doughnut'
        data:
        {
            datasets: [
            {
                data: [],
                backgroundColor: getRandom(Object.values(chartColors), xy_data.data.length), // Choose random colors with the same number of length of the data
            }],
            labels: []
        },
        options:
        {
            responsive: true,
            legend:
            {
                position: 'top',
            },
            title:
            {
                display: true,
                text: title_name,
                fontSize: 20
            },
            animation:
            {
                animateScale: true,
                animateRotate: true
            }
        }
    };

    // Push data to the above config object
    for (x of xy_data.data)
    {
        config.data.labels.push(x[0]);
        config.data.datasets[0].data.push(x[1]);
    };

    // Set the configuration in the above config object based on where we want a full or only half a pie/doughnut plot
    if (size == 'full')
    {
        config.options.circumference = 2 * Math.PI; //Set the circumference to be complete circle
        config.options.rotation = -Math.PI / 2;
    }
    else
    {
        config.options.circumference = Math.PI; //Set the circumference to be helf of a circle
        config.options.rotation = -Math.PI;
    }

    return config //Return the config
}


// Function for getting the radar chart config file in the required format for the chart.js library
function radar_chart_config(xy_data, label, title_name)
{
    var config = {
        type: 'radar',
        data:
        {
            labels: [],
            datasets: [
            {
                label: label[0],
                backgroundColor: chartColorsTrans.red,
                borderColor: chartColors.red,
                pointBackgroundColor: chartColors.red,
                data: []
            },
            {
                label: label[1],
                backgroundColor: chartColorsTrans.blue,
                borderColor: chartColors.blue,
                pointBackgroundColor: chartColors.blue,
                data: []
            }]
        },
        options:
        {
            legend:
            {
                position: 'top',
            },
            title:
            {
                display: true,
                text: title_name, // Title name
                fontSize: 20
            },
            scale:
            {
                ticks:
                {
                    beginAtZero: true
                }
            }
        }
    };

		// Push data of the first dataset
    for (x of xy_data[0].data)
    {
        config.data.labels.push(x[0]);
        config.data.datasets[0].data.push(x[1]);
    };

		// Push the data of the second dataset
    for (x of xy_data[1].data)
    {
        config.data.datasets[1].data.push(x[1]);
    };

    return config 		// Return the
}
