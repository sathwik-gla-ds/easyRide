L_PREFER_CANVAS=false; L_NO_TOUCH=false; L_DISABLE_3D=false;
var bounds = null;

// Map configs
var mapglasgow = L.map(
    'mapglasgow',
    {
        center: [55.86788356581354, -4.2845474556716425],
        zoom: 13,
        maxBounds: bounds,
        layers: [],
        worldCopyJump: false,
        crs: L.CRS.EPSG3857,
        zoomControl: true,
        attributionControl: false
    });

// OpenStreetMap Map tile
var tile_layer = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        "attribution": "",
        "detectRetina": false,
        "maxNativeZoom": 15,
        "maxZoom": 15,
        "minZoom": 11,
        "noWrap": false,
        "opacity": 1,
        "subdomains": "abc",
        "tms": false
    }).addTo(mapglasgow);



// Marker for Hillhead
var marker_hillhead = L.marker(
    [55.875114778583914, -4.283510723936834],
    {
        icon: new L.Icon.Default(),
    }
).addTo(mapglasgow);
// Popup for Hillhead
var popup_hillhead = L.popup(
{
    maxWidth: '100%',
    autoClose: false,
    closeOnClick: false,
    closeButton: false
});
var html_hillhead = $(`<div id="html_hillhead" style="width: 100.0%; height: 100.0%;">Hillhead</div>`)[0];
popup_hillhead.setContent(html_hillhead);
// Marker Binding for Hillhead
marker_hillhead.bindPopup(popup_hillhead)
    .openPopup();



// Marker for Partick
var marker_partick = L.marker(
    [55.87063648685825, -4.307028333075087],
    {
        icon: new L.Icon.Default(),
    }
).addTo(mapglasgow);
// Popup for Partick
var popup_partick = L.popup(
{
    maxWidth: '100%',
    autoClose: false,
    closeOnClick: false,
    closeButton: false
});
var html_partick = $(`<div id="html_partick" style="width: 100.0%; height: 100.0%;">Partick</div>`)[0];
popup_partick.setContent(html_partick);
// Marker Binding for Partick
marker_partick.bindPopup(popup_partick)
    .openPopup();



// Marker for Finnieston
var marker_finnieston = L.marker(
    [55.86479189351046, -4.272910539698294],
    {
        icon: new L.Icon.Default(),
    }
).addTo(mapglasgow);
// Popup for Finnieston
var popup_finnieston = L.popup(
{
    maxWidth: '100%',
    autoClose: false,
    closeOnClick: false,
    closeButton: false
});
var html_finnieston = $(`<div id="html_finnieston" style="width: 100.0%; height: 100.0%;">Finnieston</div>`)[0];
popup_finnieston.setContent(html_finnieston);
// Marker Binding for Finnieston
marker_finnieston.bindPopup(popup_finnieston)
    .openPopup();



// Marker for govan
var marker_govan = L.marker(
    [55.85784298533108, -4.3014868355477],
    {
        icon: new L.Icon.Default(),
    }
).addTo(mapglasgow);
// Popup for govan
var popup_govan = L.popup(
{
    maxWidth: '100%',
    autoClose: false,
    closeOnClick: false,
    closeButton: false
});
var html_govan = $(`<div id="html_govan" style="width: 100.0%; height: 100.0%;">Govan</div>`)[0];
popup_govan.setContent(html_govan);
// Marker Binding for govan
marker_govan.bindPopup(popup_govan)
    .openPopup();



// Marker for Laurieston
var marker_laurieston = L.marker(
    [55.853627679483225, -4.264236317019805],
    {
        icon: new L.Icon.Default(),
    }
).addTo(mapglasgow);
// Popup for Laurieston
var popup_laurieston = L.popup(
{
    maxWidth: '100%',
    autoClose: false,
    closeOnClick: false,
    closeButton: false
});
var html_laurieston = $(`<div id="html_laurieston" style="width: 100.0%; height: 100.0%;">Laurieston</div>`)[0];
popup_laurieston.setContent(html_laurieston);
// Markup Binding for Laurieston
marker_laurieston.bindPopup(popup_laurieston,
    {
        noHide: true
    })
    .openPopup();
