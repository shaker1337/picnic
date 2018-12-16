var map, infoWindow,marker1,  position;
//markers
var markers=[];
// Info window
let info = new google.maps.InfoWindow();
$(document).ready(function() {
    // Options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    let options = {
        center: {lat: 51.476852, lng: 0.0}, // Greenwich
        zoom: 13
    };



    // Get DOM node in which map will be instantiated
    let canvas = $("#map-canvas").get(0);

    // Instantiate map
    map = new google.maps.Map(canvas, options);


    infoWindow = new google.maps.InfoWindow;



if (navigator.geolocation) {
              navigator.geolocation.getCurrentPosition(function(position) {
                var pos = {
                  lat: position.coords.latitude,
                  lng: position.coords.longitude
                };

                infoWindow.setPosition(pos);
                infoWindow.setContent('You are here!.');
                infoWindow.open(map);
                map.setCenter(pos);
              }, function() {
                handleLocationError(true, infoWindow, map.getCenter());
              });
            } else {
              // Browser doesn't support Geolocation
              handleLocationError(false, infoWindow, map.getCenter());
            }


          function handleLocationError(browserHasGeolocation, infoWindow, pos) {
            infoWindow.setPosition(pos);
          }

google.maps.event.addListener(map, "click", function(event) {
      if (marker1 == null){
      marker1 = new google.maps.Marker({
      position: event.latLng,
      map: map

      })} else{
          marker1.setPosition(event.latLng);
      }
      position=marker1.getPosition();
      console.log(marker1);
      console.log(JSON.stringify(marker1.position));
});
//GENERATE MARKERS WITH ALL POSSIBLE PLACES FROM DATABASE
//generate_markers();

});
//SEND PLACE position name and description INFO TO ADD DATA
window.onload = function(){
$("#submit").click(function() {
var place_name=$("#place_name").val();
var description=$("#description").val();
var data=[];
data.push(place_name);
data.push(description);
console.log("HELLLLLLLLLLO WORLDDD/11");
$.ajax({
                            type: 'POST',
                            url: "/add_data",
                            data:"&place_name="+place_name+"&description="+description+"&position="+position,
                        });

})};

    console.log("HELLO WORLD!");
    $.ajax({
        type: 'POST',
        url: '/generate_markers',
        async: true
        }).success(function(response){
        console.log(response);
     //Add new markers to map
       for (let i = 0; i < response.length; i++)
       {
           addMarker(response[i]);
       }
});




function addMarker(data)
{
    //instatiate marker
        var marker = new google.maps.Marker({
        position: new google.maps.LatLng(data.marker_lat, data.marker_lng),
        map: map,
        title: data.place_name

    });
    //create a clickable titled link with descripton
    var articles = '<p><b>' +data['place_name'] + "</b></p>"
    + "<p>" + data['description'] + '</p><a href=/goto?lat='+data.marker_lat+'&lng='+data.marker_lng+' class="alert-link">Navigate</a>';



    //show info windows on click
    marker.addListener('click', function() {
        showInfo(marker, articles);
    });
    //add marker to markers list
    markers.push(marker);
    console.log(markers);
}

function showInfo(marker, content)
{
    // Start div
    let div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // End div
    div += "</div>";
    // Set info window's content
    info.setContent(div);

    // Open info window (if not already open)
    info.open(map, marker);
}

