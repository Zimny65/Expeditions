// html_dynamic_trail_layer.js
let allGpxLayer = null;

window.addEventListener("DOMContentLoaded", function () {
    const mapId = document.querySelector(".folium-map")?.getAttribute("id");
    const map = window[mapId];
    if (!map) {
        console.warn("Nie znaleziono obiektu mapy Leaflet.");
        return;
    }

    function toggleAllGpxLayer() {
        const zoom = map.getZoom();

        if (zoom >= 10 && !allGpxLayer) {
            fetch('expeditions.geojson')
                .then(res => res.json())
                .then(data => {
                    const groupLayers = [];

                    L.geoJSON(data, {
                        style: function(feature) {
                            return {
                                color: feature.properties.color || 'gray',
                                weight: 3,
                                opacity: 1
                            };
                        },
                        onEachFeature: function (feature, layer) {
                            if (feature.geometry.type === "LineString") {
                                const coords = feature.geometry.coordinates;

                                if (feature.properties?.name && feature.properties?.trail_counter) {
                                    layer.bindTooltip(
                                        `<div style="font-family: 'Oswald', sans-serif; font-size: 12px;">
                                            ${feature.properties.trail_counter} ${feature.properties.name}
                                        </div>`,
                                        { sticky: true }
                                    );
                                }

                                layer.on({
                                    mouseover: function () {
                                        layer.setStyle({ weight: 6, color: '#000000' });
                                        layer.bringToFront();
                                    },
                                    mouseout: function () {
                                        layer.setStyle({
                                            weight: 3,
                                            color: feature.properties.color || 'gray'
                                        });
                                    }
                                });

                                const startMarker = L.circleMarker([coords[0][1], coords[0][0]], {
                                    radius: 3,
                                    color: feature.properties.color || 'gray',
                                    fillColor: feature.properties.color || 'gray',
                                    fillOpacity: 1
                                });
                                const endMarker = L.circleMarker([coords[coords.length - 1][1], coords[coords.length - 1][0]], {
                                    radius: 3,
                                    color: feature.properties.color || 'gray',
                                    fillColor: feature.properties.color || 'gray',
                                    fillOpacity: 1
                                });

                                const group = L.layerGroup([layer, startMarker, endMarker]);
                                groupLayers.push(group);
                            }
                        }
                    });

                    allGpxLayer = L.layerGroup(groupLayers);
                    allGpxLayer.addTo(map);
                });
        }

        if (zoom < 10 && allGpxLayer) {
            map.removeLayer(allGpxLayer);
            allGpxLayer = null;
        }
    }

    map.on('zoomend', toggleAllGpxLayer);
    toggleAllGpxLayer();
});
