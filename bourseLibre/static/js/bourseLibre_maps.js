function getIconFromType(L, type_marqueur) {

 ('5','Violet'), ('6','Or'), ('7','Noir'), ('8','Gris')

var greenIcon = L.icon({
  iconUrl: "/static/img/marker-icon-2x-green.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

var blueIcon = L.icon({
  iconUrl: "/static/img/marker-icon-blue.png",
  shadowUrl:"/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var blackIcon = L.icon({
  iconUrl: "/static/img/marker-icon-black.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var greyIcon = L.icon({
  iconUrl: "/static/img/marker-icon-grey.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var yellowIcon = L.icon({
  iconUrl: "/static/img/marker-icon-yellow.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var orangeIcon = L.icon({
  iconUrl: "/static/img/marker-icon-orange.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

var redIcon = L.icon({
  iconUrl: "/static/img/marker-icon-red.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var violetIcon = L.icon({
  iconUrl: "/static/img/marker-icon-violet.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var blackIcon = L.icon({
  iconUrl: "/static/img/marker-icon-black.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var greyIcon = L.icon({
  iconUrl: "/static/img/marker-icon-grey.png",
  shadowUrl: "/static/img/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


var leafIcon = L.icon({
iconUrl: "/static/img/leafgreen.png",
shadowUrl: "/static/img/leafshadow.png",
iconSize:     [38, 95], // size of the icon
shadowSize:   [50, 64], // size of the shadow
iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
shadowAnchor: [4, 62],  // the same for the shadow
popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

    if (type_marqueur == '0') {
        return greenIcon
  } else if (type_marqueur == '1') {
        return blueIcon
  } else if (type_marqueur == '2') {
        return redIcon
  } else if (type_marqueur == '3') {
        return yellowIcon
  } else if (type_marqueur == '4') {
        return orangeIcon
  } else if (type_marqueur == '5') {
        return violetIcon
  } else if (type_marqueur == '6') {
        return goldIcon
  } else if (type_marqueur == '7') {
        return blackIcon
  } else if (type_marqueur == '8') {
        return greyIcon
  } else {
        return leafIcon
  }
}

