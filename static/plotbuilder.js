// begin running the zipcode on entry of a code by the user
d3.select("#zip_button")
        .on("click", function(d,i) {
            // convert the code to an interger
            code = parseInt(document.getElementById("zip_code").value)
            console.log(code)
            //for the purpose of my portfolio, disable the input of a new zip; not able to use the API keys to get data
            alert("Sorry, this function is not available due to expired API keys");
            //checkzip(code)
        });

// check the zip code to make sure it is valid, place popup for invalid zips
// return lat/lon/city/county to the other functions when zip code is valid
function checkzip(code) {
    Plotly.d3.json("/zip_latlng/" + code, function(errr, data){
      // fixes zip codes that lead with 0
      if (code < 10){
          code = "0000" + code;
      }
      else if (code < 100){
        code = "000" + code;
      }
      else if (code < 1000){
        code = "00" + code;
      }
      else if (code < 10000){
        code = "0" + code;
      }

      console.log(code)

        if (Object.keys(data).length < 3){
            console.log("empty")
            var zipCode = prompt("Sorry, there is no data for that zipcode, please enter another");
            checkzip(zipCode)
        }
        else{

            Plotly.d3.json("/alldata/" + code, function(err, allData){
                poi_pie(allData[1], code);
                age_pie(allData[0], code, data.LAT, data.LON, allData[4][0]);
                build_gauge_chart(allData);
                build_real_estate_graph(allData[3]);
                census_county_pop(allData[2]);
                build_meta_data(allData);
                build_pop_homes_correl(allData);

                //display the zip code and score in the header bar
                var app = document.querySelector("#zip_score");
                var h3data = document.querySelector("#zip_score > h3");
                if (h3data !== null) {
                      app.removeChild(h3data);
                }
                var app = document.querySelector("#zip_score");
                var h3data = document.createElement("h3");
                //city, state, zip on first line
                h3data.innerHTML = allData[4][0]['city'] + ", " + allData[4][0]['state'] + " " +allData[4][0]['zip'] +
                              ",  SCORE: " + (allData[0]['score'] * 100).toPrecision(2);
                //h3data.style.textAlign = "center";
                app.appendChild(h3data);
            })

        }

})};

function zipMap(lat, lng, z_info, score){

  // change the map view to the new zip code
  myMap.panTo(new L.LatLng(lat, lng));
  var final_score = Math.round(score * 100)
  // add marker for new zipcode
  var marker = L.marker([lat, lng], {
      draggable: true
  }).bindPopup("Zip Code: " + z_info.zip + "<hr> City: " + z_info.city + "<br> County: " + z_info.county + "<br>State: " + z_info.state + "<br> Score: " + final_score).addTo(myMap);

};


// POI pie plot taking lat/lng from checkzip function
function poi_pie(data, zip){

        // create the total number of places of interest and the percentages, place in pie values list
        console.log(data)
        var poi_total = data.Liquorstore + data.Gym + data.Park + data.Shoppingmall + data.Groceryorsupermarket + data.Movietheater;
        var ls_pct = (data.Liquorstore/poi_total) * 100;
        var gym_pct = (data.Gym/poi_total) * 100;
        var park_pct = (data.Park/poi_total) * 100;
        var sm_pct = (data.Shoppingmall/poi_total) * 100;
        var gos_pct = (data.Groceryorsupermarket/poi_total) * 100;
        var mt_pct = (data.Movietheater/poi_total) * 100;
        var pie_values = [ls_pct, gym_pct, park_pct, sm_pct, gos_pct, mt_pct];

        console.log(pie_values);

        // place the individual totals for hover text
        var ind_totals = [data.Liquorstore, data.Gym, data.Park, data.Shoppingmall, data.Groceryorsupermarket, data.Movietheater];
        console.log(ind_totals);

        // create the pie labels
        var pie_labels = ["Liquor Stores", "Gyms", "Parks", "Shopping Malls", "Grocery Stores", "Movie Theaters"];

        // create the hovertext using ind totals and pie labels
        var poi_desc = [];
        for (p=0; p < ind_totals.length; p++){
            poi_desc.push(pie_labels[p] + ": " + ind_totals[p]);
        }
        console.log(poi_desc);

        var new_title = 'Points of Interest';

        // plot the chart
        Plotly.restyle('POI-pie', "values", [pie_values]);
        Plotly.restyle('POI-pie', "labels", [pie_labels]);
        Plotly.restyle('POI-pie', "hovertext", [poi_desc]);
        Plotly.relayout('POI-pie', "title", new_title);

};

function age_pie(data, zip, lat, lng, zip_info){
    // call the route with the POI data

        // create the total number of places of interest and the percentages, place in pie values list
        console.log(data)
        var age_total = data._0_09 + data._10_19 + data._20_29 + data._30_39 + data._40_49 + data._50_59 + data._60_69 + data._70_plus;
        var _0_09_pct = (data._0_09/age_total) * 100;
        var _10_19_pct = (data._10_19/age_total) * 100;
        var _20_29_pct = (data._20_29/age_total) * 100;
        var _30_39_pct = (data._30_39/age_total) * 100;
        var _40_49_pct = (data._40_49/age_total) * 100;
        var _50_59_pct = (data._50_59/age_total) * 100;
        var _60_69_pct = (data._60_69/age_total) * 100;
        var _70_plus_pct = (data._70_plus/age_total) * 100;

        var pie_values = [_0_09_pct,_10_19_pct, _20_29_pct, _30_39_pct, _40_49_pct, _50_59_pct, _60_69_pct, _70_plus_pct];

        console.log(pie_values);

        // place the individual totals for hover text
        var ind_totals = [data._0_09, data._10_19, data._20_29, data._30_39, data._40_49, data._50_59, data._60_69, data._70_plus];
        console.log(ind_totals);

        // create the pie labels
        var pie_labels = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"];

        // create the hovertext using ind totals and pie labels
        var age_desc = [];
        for (a=0; a < ind_totals.length; a++){
            age_desc.push(pie_labels[a] + ": " + ind_totals[a]);
        }
        console.log(age_desc);

        var new_title_age = 'Age Demographics';

        // plot the chart
        Plotly.restyle('age-pie', "values", [pie_values]);
        Plotly.restyle('age-pie', "labels", [pie_labels]);
        Plotly.restyle('age-pie', "hovertext", [age_desc]);
        Plotly.relayout('age-pie', "title", new_title_age);
        zipMap(lat,lng, zip_info, data.score)
};

var originalWidth = document.getElementById('cont1').clientWidth;
  var gaugeMarkerSize = 10;
  var mycolorsgauge = ['rgba(0, 255, 0, .5)',
  'rgba(191, 255, 0, .5)',
   'rgba(255, 255, 0, .5)',
  'rgba(255, 128, 0, .5)',
    'rgba(255, 0, 0, .5)',
     'rgba(0,0,0,0)'];

function build_gauge_chart(zip_data) {

  //var level = zip_data[0]['score'] * 100;
  var level = (zip_data[0]['score'] * 100).toPrecision(2);

  console.log("level score: " + level);

  // Trig to calc meter point
      var deg = degrees = ((level*180)/100);
      var degrees = 180-deg,
          radius = .5;
      var radians = degrees * Math.PI / 180;
      var x = radius * Math.cos(radians);
      var y = radius * Math.sin(radians);


      // Path:
      var mainPath = 'M -.0 -0.025 L .0 0.025 L ',
          pathX = String(x),
          space = ' ',
          pathY = String(y),
          pathEnd = ' Z';
      var path = mainPath.concat(pathX,space,pathY,pathEnd);

      var data = [{ type: 'scatter',
          x: [0], y:[0],
          marker: {size: gaugeMarkerSize, color:'black'},
          showlegend: false,
          name: 'score',
          text: level,
          hoverinfo: 'text'},
          { values: [40/5, 40/5, 40/5, 40/5, 40/5, 40],
          rotation: 90,
          text: ['Great','Good', 'Adequate', 'Poor', 'Awful', ''],
          textinfo: 'text',
          textposition:'inside',
          marker: {colors: mycolorsgauge},
          labels: ['80-100','60-80', '40-60', '20-40', '0-20', ''],
          hoverinfo: 'label',
          hole: .5,
          type: 'pie',
          showlegend: false
      }];

      var layout = {
      shapes:[{
          type: 'path',
          path: path,
          fillcolor: 'black',
          line: {
              color: 'black'
          }
          }],
      title: 'Zip Slip Score for '+ zip_data[4][0].zip,
      height: 350,
      width: 350,
      paper_bgcolor:'rgba(0,0,0,0)',
      plot_bgcolor:'rgba(0,0,0,0)',
      xaxis: {zeroline:false, showticklabels:false,
                  showgrid: false, range: [-1, 1]},
      yaxis: {zeroline:false, showticklabels:false,
                  showgrid: false, range: [-1, 1]}
      };
      Plotly.newPlot('gauge', data, layout);
}

function build_real_estate_graph(REdata) {


  //first remove a previously-rendered svg
  d3.select("#homechart").remove();
  d3.select("#homestooltip").remove();

  var svgWidth = 700;
  var svgHeight = 400;

  var margin = { top: 20, right: 40, bottom: 80, left: 100 };

  var width = svgWidth - margin.left - margin.right;
  var height = svgHeight - margin.top - margin.bottom;
  var yMax;
  var yMin;


  // Create a function to parse date (YYYY-MM) because this will be a time-sequenced graph
  var parseTime = d3.timeParse("%Y_%m");
  // Format the data
  REdata.forEach(function(data) {
    data.period = parseTime(data.period);
    data.home_value = +data.home_value;
    data.rental = +data.rental;
  });

  // Create an SVG wrapper, append an SVG group that will hold the chart, and shift the latter by left and top margins.
  var svg = d3.select(".chart")
    .append("svg")
    .attr("id","homechart")
    .attr("width", svgWidth)
    .attr("height", svgHeight)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var chart = svg.append("g");

  // Append a div to the body to create tooltips, assign it a class
  d3.select(".chart")
    .append("div")
    .attr("class", "tooltip")
    .attr("id", "homestooltip")
    .style("opacity", 0);

    // This function identifies the minimum and maximum values in a column
    // and assign them to yMin and yMax variables, which will define the axis domain
    function findMinAndMax(dataColumnY) {
      yMin = d3.min(REdata, function(data) {
      return +data[dataColumnY] * 0.8;
      });
      yMax = d3.max(REdata, function(data) {
        return +data[dataColumnY] * 1.1;
      });
    }

  // The default y-axis is 'home_value'
  // Another axis can be assigned to the variable during an onclick event.
  // This variable is key to the ability to change axis/data column
  var currentAxisLabelX = "period";
  var currentAxisLabelY = "home_value";
  var otherAxisLabelY = "rental";

  // Call findMinAndMax() with default Y label
  findMinAndMax(currentAxisLabelY);

  var xTimeScale = d3.scaleTime()
    .range([0, width]);

  var x = d3.scaleTime()
      .range([0, width]);

  // Create scale functions for each Y axis
  var yLinearScale = d3.scaleLinear()
    .range([height, 0]);
  var yLinearScale2 = d3.scaleLinear()
      .range([height, 0]);


  var line1 = d3
        .line()
        .x(function(data) {
          return xTimeScale(data.period);
        })
        .y(function(data) {
          return yLinearScale(data.home_value);
        });
  var line2 = d3
        .line()
        .x(function(data) {
          return xTimeScale(data.period);
        })
        .y(function(data) {
          return yLinearScale2(data.rental);
        });

  // Create axis functions
  var bottomAxis = d3.axisBottom(xTimeScale)
    .ticks(18)
    .tickFormat(d3.timeFormat("%m-%Y"));

  var leftAxis = d3.axisLeft(yLinearScale)
    .tickFormat(d3.format('$,'));

  // Scale the domain
  xTimeScale.domain(d3.extent(REdata, function(data) {
    return data.period;
  }));
  yLinearScale.domain([yMin, yMax]);

  findMinAndMax(otherAxisLabelY);
  yLinearScale2.domain([yMin, yMax]);

  // Add the line paths.
  chart.append("path")
      .data([REdata])
      .attr("class", "line blue")
      .attr("id","homeline")
      .style("stroke-opacity", 0.8)
      .attr("d", line1);

  chart.append("path")
      .data([REdata])
      .attr("class", "line green")
      .attr("id","rentline")
      .style("stroke-opacity", 0)
      .attr("d", line2);

  //add the tool tip
  var toolTip = d3.tip()
    .attr("class", "tooltip")
    .offset([0,0])
    .html(function(data) {

      if (currentAxisLabelY === "home_value") {
        var yVal = data.home_value;
      }
      else {
        var yVal = data.rental;
      };
      var formatAmount = d3.format('$,');
      yString = formatAmount(yVal);

      var formatPeriod = d3.timeFormat("%m-%Y");
      xString = formatPeriod(data.period);
      return (xString + ": " + yString);
    });

  chart.call(toolTip);

  // create the circles
  chart.selectAll("circle")
    .data(REdata)
    .enter()
      .append("circle")
      .attr("cx", function(data, index) {
        return xTimeScale(data[currentAxisLabelX]);
      })
      .attr("cy", function(data, index) {
        return yLinearScale(+data[currentAxisLabelY]);
      })
      .attr("r", "5")
      .attr("stroke","black")
      .attr("fill", "blue")


      //on hover, show the tooltip
      .on("mouseover", function(data) {
        toolTip.show(data);
      })
      // onmouseout event hide the tooltip
      .on("mouseout", function(data, index) {
        toolTip.hide(data);
      });


  //append x axis
  chart.append("g")
    .attr("transform", `translate(0, ${height})`)
    .attr("class","x-axis") //used for transition
    .attr("class","axis")
    .call(bottomAxis)
    .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".35em")
        .attr("transform", "rotate(-65)")


  //append y axis
  chart.append("g")
    .attr("class","y-axis")
    .call(leftAxis);

  //y-axis label; all y-axis labels will always be inactive. the only way to select an axis is through the x-axis
  // first y-axis is considered selected and bolded

  //x-axis label always selected; y label is selectable (active or inactive)
  chart.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left + 20)
      .attr("x", 0 - (height / 1.7))  // make 1.5 smaller to get the axis title to move down a bit
      .attr("dy", "1em")
      .attr("class", "axis-text active blue")
      //default
      .attr("data-axis-name", currentAxisLabelY)
      .text("Home Prices ($)")

  //append the unselected Y labels
  chart.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 1.7))  // make 1.5 smaller to get the axis title to move down a bit
      .attr("dy", "1em")
      .attr("class", "axis-text inactive green")
      .attr("data-axis-name", otherAxisLabelY)
      .text("Monthly Rent ($)")



  // Append x-axis labels
  chart.append("text")
    .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.top + 50) + ")") //make 2.5 larger to get title to move left
    .attr("class", "axis-text x-selected")
    //default
    .attr("data-axis-name", "period")
    .text("Month")

  //add a title to the chart
  chart.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2) +10)
    .attr("text-anchor", "middle")
    .style("font-size", "18px")
    .text("Home Sales and Rents - 2014-2017");


  //handle the axis change
  function labelChange(clickedAxis) {
    d3.selectAll(".axis-text")
      .filter(".active")
      // An alternative to .attr("class", <className>) method. Used to toggle classes.
      .classed("active", false)
      .classed("inactive", true);
    clickedAxis.classed("inactive", false).classed("active", true);
  }

    //CLICKED Y AXIS!!!
    d3.selectAll(".axis-text").on("click", function() {
    // Assign a variable to current axis
      var clickedSelection = d3.select(this);

      // "true" or "false" based on whether the axis is currently selected
      var isClickedSelectionInactive = clickedSelection.classed("inactive");

      // Grab the data-attribute of the axis and assign it to a variable
      var clickedAxis = clickedSelection.attr("data-axis-name");

      // The onclick events below take place only if the axis is inactive
      // Clicking on an already active axis will therefore do nothing
      if (isClickedSelectionInactive) {
        // Assign the clicked axis to the variable currentAxisLabelY
        currentAxisLabelY = clickedAxis;

        //find min and max domain values
        findMinAndMax(currentAxisLabelY);
        // Set the domain for the y-axis
        yLinearScale.domain([yMin, yMax]);


        // Create a transition effect for the y-axis
        svg
          .select(".y-axis")
          .transition()
          .duration(500)
          .call(leftAxis);

        // Select all circles to create a transition effect, then relocate the horizontal and vertical location
        // based on the new axis that was selected/clicked
        d3.selectAll("circle").each(function() {
          d3
            .select(this)
            .transition()
            .attr("cy", function(data, index) {
              return yLinearScale(+data[currentAxisLabelY]);
            })
            .duration(500)

            .attr("fill", function(data,index) {
              if (currentAxisLabelY === "home_value") {
                return "blue";
              }
              else {
                return "green";
              }
            })


        });

        // change the line
        if (clickedAxis === "home_value") {
          d3.select("#homeline").style("stroke-opacity",1);
          d3.select("#rentline").style("stroke-opacity",0);
          console.log("homevalue selected");
        }
        else {
          d3.select("#homeline").style("stroke-opacity",0);
          d3.select("#rentline").style("stroke-opacity",1);
          console.log("rent selected");
        }

        // Change the status of the axes.
        labelChange(clickedSelection);

      }
    });

}

//build the census population chart
function census_county_pop (data) {
  var pops = [data.POPULATION_2010, data.POPULATION_2011, data.POPULATION_2012, data.POPULATION_2013, data.POPULATION_2014,
      data.POPULATION_2015, data.POPULATION_2016];
  var labels = ['2010', '2011', '2012', '2013', '2014', '2015', '2016'];
  var pop_desc = [];
  for (p=0; p < pops.length; p++){
      pop_desc.push(labels[p] + ": " + pops[p]);
  };
  var trace = {
      x: labels,
      y: pops,
      type: 'scatter',
      hoverinfo: "text",
      hovertext: pop_desc
    };
  var layout = {
      height: 500,
      width: 600,
      paper_bgcolor:'rgba(0,0,0,0)',
      plot_bgcolor:'rgba(0,0,0,0)',
      title: 'Census Population for ' + data.COUNTY ,
      xaxis: {
          title: '2010 - 2016 Difference: ' + data.diff_2010_2016 + "%",
          titlefont: {
            family: 'Arial, sans-serif',
            size: 16
          }}
  };
  var d = [trace];
  Plotly.newPlot('population', d, layout);};


  //build the score data info section
  function build_meta_data(zip_data) {

    var app = document.querySelector("#meta_list");

      //first need to remove any data that might be there, and then populate it
      //get the H6 data associated with the #meta_list
      var h6data = document.querySelector("#meta_list > h6");
      if (h6data !== null) {
        for (i=0; i<11; i++) {
          var h6data = document.querySelector("#meta_list > h6");
          app.removeChild(h6data);
        }
      }


      //put the metadata into h6 tags
      var h6data = document.createElement("h6");
      //city, state, zip on first line
      h6data.innerHTML = zip_data[4][0]['city'] + ", " + zip_data[4][0]['state'] + " " +zip_data[4][0]['zip'];
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Avg Home Value: $' +  zip_data[4][0]['home_value'].toLocaleString();
      h6data.innerHTML = "<i class = 'fa fa-home'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Avg Rent: $' +  zip_data[4][0]['rental'].toLocaleString();
      h6data.innerHTML = "<i class='material-icons' style='font-size:16px'>location_city</i>"+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Avg Winter Temp: ' +  Math.round(zip_data[0]['avg_jan']) + '\xB0F';
      h6data.innerHTML = "<i class = 'fa fa-snowflake-o'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Avg Summer Temp: ' +  Math.round(zip_data[0]['avg_jul']) + '\xB0F';
      h6data.innerHTML = "<i class = 'fa fa-thermometer-full'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Schools: Public: ' +  zip_data[0]['public_school'] + ", Private: " + zip_data[0]['private_school'] + zip_data[0]['catholic_school'];
      h6data.innerHTML = "<i class = 'fa fa-graduation-cap'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Crime Risk: ' +  zip_data[0]['crime'] + " (median=100)";
      h6data.innerHTML = "<i class='material-icons' style='font-size:16px'>fingerprint</i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Sales Tax: ' +  zip_data[0]['sales_tax'] + "%";
      h6data.innerHTML = "<i class = 'fa fa-usd'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Market Health Index: ' +  zip_data[0]['market_health_index'].toPrecision(2) + " (0-10)";
      h6data.innerHTML = "<i class = 'fa fa-line-chart'></i> "+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Walkability: ' +  zip_data[0]['walk_description'];
      h6data.innerHTML = "<i class='material-icons' style='font-size:16px'>directions_walk</i>"+home_text;
      app.appendChild(h6data);

      var h6data = document.createElement("h6");
      var home_text = 'Population Growth: ' +  zip_data[2]['diff_2010_2016']+ "%";
      h6data.innerHTML = "<i class = 'fa fa-group'></i> "+home_text;
      app.appendChild(h6data);
    }


    //create population/home value correlation graph
    function build_pop_homes_correl(zip_data) {
      console.log("remove prev corr chart");
      //first remove previous chart
      d3.select("#correlationchart").remove();
      d3.select("#correlationtip").remove();

      var pop = zip_data[2];
      offset1 = (pop.POPULATION_2015 - pop.POPULATION_2014)/4;
      offset2 = (pop.POPULATION_2016 - pop.POPULATION_2015)/4;

      var RE = zip_data[3];

      function format_period(period){
        //sometimes the YYYY_MM changes to internal format so first need to get the period into the right format

        var currentDate = new Date(period);
        if ( isNaN( currentDate.getMonth() ) ) {
          //not a date format; use original format
          new_period = period.slice(5,7)+"-"+period.slice(0,4);
          console.log("OKnew_period: "+ new_period);
        }
        else {
          //date format; reformat into string format for display
          var month = currentDate.getMonth(); //Be careful! January is 0 not 1
          var year = currentDate.getFullYear();

          var dateString = (month + 1) + "-" + year;
          console.log("dateString: " + dateString);
          new_period = dateString;
        }
        return new_period;
      }

    console.log(RE);
      var pop_home = [
        {period: format_period(RE[0].period), pop: pop.POPULATION_2014, home_value: RE[0].home_value},
        {period: format_period(RE[1].period), pop: pop.POPULATION_2014 + offset1, home_value: RE[1].home_value},
        {period: format_period(RE[2].period), pop: pop.POPULATION_2014 + (offset1*2), home_value: RE[2].home_value},
        {period: format_period(RE[3].period), pop: pop.POPULATION_2014 + (offset1*3), home_value: RE[3].home_value},
        {period: format_period(RE[4].period), pop: pop.POPULATION_2015, home_value: RE[4].home_value},
        {period: format_period(RE[5].period), pop: pop.POPULATION_2015 + offset2, home_value: RE[5].home_value},
        {period: format_period(RE[6].period), pop: pop.POPULATION_2015 + (offset2*2), home_value: RE[6].home_value},
        {period: format_period(RE[7].period), pop: pop.POPULATION_2015+ (offset2*3), home_value: RE[7].home_value},
        {period: format_period(RE[8].period), pop: pop.POPULATION_2016, home_value: RE[8].home_value}
      ];
      console.log("pop_home");
      console.log(pop_home);

      var yMin;
      var xMin;

      function findyMin() {
        yMin = d3.min(pop_home, function(data) {
        return +data['home_value'] * 0.99;
        });
      }
      function findxMin() {
        xMin = d3.min(pop_home, function(data) {
        return +data['pop'] * 0.999;
        });
      }
      // Call findMin()
      findyMin();
      findxMin();


    var svgWidth = 500;
    var svgHeight = 500;
    var margin = { top: 30, right: 40, bottom: 85, left: 80 };
    var width = svgWidth - margin.left - margin.right;
    var height = svgHeight - margin.top - margin.bottom;
    // Create an SVG wrapper, append an SVG group that will hold our chart, and shift the latter by left and top margins.
    var svg = d3.select(".correl")
      .append("svg")
      .attr("id","correlationchart")
      .attr("width", svgWidth)
      .attr("height", svgHeight)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var chart = svg.append("g");
    //Append a div to the body to create tooltips, assign it a class
    d3.select(".correl")
      .append("div")
      .attr("class", "tooltip2")
      .attr("id","correlationtip")
      .style("opacity", 0);


      // Create scale functions
      var yLinearScale = d3.scaleLinear()
        .range([height, 0]);
      var xLinearScale = d3.scaleLinear()
        .range([0, width]);
      // Create axis functions
      var bottomAxis = d3.axisBottom(xLinearScale);
      var leftAxis = d3.axisLeft(yLinearScale)
        .tickFormat(d3.format('$,'));
      // Scale the domain
      xLinearScale.domain([xMin, d3.max(pop_home, function(data) {
        return +data.pop;
      })]);
      yLinearScale.domain([yMin, d3.max(pop_home, function(data) {
        return +data.home_value;
      })]);

      var toolTip = d3.tip()
        .attr("class", "tooltip2")
        .offset([80, -60])
        .html(function(data) {

          var period = data.period;
          var pop = +data.pop;
          var home_value = +data.home_value;

          var formatAmount = d3.format('$,');
          var formatPop = d3.format(',');
          var popString = formatPop(pop);
          yString = formatAmount(home_value);

          return (period + "<br> Population: " + popString + "<br> Home Value: " + yString);
        });
      chart.call(toolTip);

      chart.selectAll("rect")
        .data(pop_home)
        .enter().append("rect")
          .attr("x", function(data, index) {
            return xLinearScale(data.pop);
          })
          .attr("y", function(data, index) {
              return yLinearScale(data.home_value);
          })
          .attr("width", "10")
          .attr("height", "10")
          .attr("fill", "mediumvioletred")
          .on("mouseover", function(data) {
            toolTip.show(data);
          })
          // onmouseout event
          .on("mouseout", function(data, index) {
            toolTip.hide(data);
          });
      chart.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(bottomAxis)
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".35em")
            .attr("transform", "rotate(-65)");
      chart.append("g")
        .call(leftAxis);
      chart.append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 0 - margin.left + 5)
          .attr("x", 0 - (height / 2))
          .attr("dy", "1em")
          .attr("class", "axisText")
          .text("Home Value");
    // Append x-axis labels
      chart.append("text")
        .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.top + 50) + ")")
        .attr("class", "axisText")

        .text("Population");


        //add a title to the chart
           chart.append("text")
                .attr("x", (width / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle")
                .style("font-size", "18px")
                .text("Correlation of Population and Home Sales - 2014-2016");
    }
