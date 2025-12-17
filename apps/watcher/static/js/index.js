"use strict";

let app = {};

app.data = {    
    data: function() {
        return {
            region: {
                lat_min: '',
                lat_max: '',
                lon_min: '',
                lon_max: ''
            },
            drawnRectangles: [],
            allSightingsStats: [],
            sightingsStatistics: [],
            markers: [],
            markerCoords: {
                lat: '',
                lon: '',
            },
            query: '',
            selectedSpecies: '',
            species: [],
            heat: null
        };
    },

    methods: {
        submitCoordinates() {
            localStorage.setItem('selectedRegion', JSON.stringify(this.region));
            window.location.href = location_url;
        },

        //  MODIFIED: Added goToStatisticsPage method 
        goToStatisticsPage() {
            localStorage.setItem('selectedRegion', JSON.stringify(this.region));
            window.location.href = statistics_url;
        },

        // Modified: Added goToChecklistPage method
        goToChecklistPage() {
            window.location.href = checklist_url;
        },

        getSpecies() {
            const search_url = '/watcher/search_species';
            axios.get(search_url, {params: {q: this.query}})
                .then((response) => {
                    this.species = response.data.species;
                });
        },

        getSightings(speciesId) {
            axios.get(get_sightings_url, {params: {species_id: speciesId}})
            .then((r) => {
                let all_sightings = r.data.coordinates;
                this.sightingsStatistics = all_sightings;
                if (this.heat) {
                    this.heat.setLatLngs(all_sightings);
                } else {
                    this.heat = L.heatLayer(all_sightings, {radius: 12}).addTo(app.map);
                }
            })
            .catch((error) => {
                console.error('Error fetching sightings:', error);
            });
        },

        search() {
            if (this.query.length >= 1) {
                this.getSpecies();
            } else {
                this.species = [];
                this.getSightings();
            }
        },

        selectSpecies(option) {
            if(option.id) {
                this.query = option.common_name;
                this.species = [];
                this.getSightings(option.id);
            }
        },
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

document.addEventListener('DOMContentLoaded', function () {
    app.load_data();
});

app.load_data = function () {

    if (!app.map) {
        app.initMap();
        app.loadSightings();
    }
}

// Initialize map
app.initMap = function () {
    app.map = L.map('map').setView([40.38, -95.8887], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(app.map);
    var drawnItems = new L.FeatureGroup();
    app.map.addLayer(drawnItems);
    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polyline: false,
            polygon: false,
            circle: false,
            marker: true,
            circlemarker: false,
            rectangle: true
        }
    });
    app.map.addControl(drawControl);
    app.map.on(L.Draw.Event.CREATED, function (event) {
        app.handleDrawEvent(event, drawnItems);
    });
};

// Load sightings data
app.loadSightings = function () {

    axios.get(get_sightings_url)
        .then((r) => {
            let all_sightings = r.data.coordinates;
            app.vue.sightingsStatistics = all_sightings;
           
            var heatPoints = all_sightings;
            var heat = L.heatLayer(heatPoints, {radius: 12}).addTo(app.map);
            app.vue.heat = heat;
        })
        .catch((error) => {
            console.error('Error fetching sightings:', error);
        });
};

// Handle draw event
app.handleDrawEvent = function (event, drawnItems) {
    var layer = event.layer;
    if (event.layerType === 'rectangle') {
        if (app.vue.drawnRectangles.length > 0) {
            drawnItems.removeLayer(app.vue.drawnRectangles[0]);
            app.vue.drawnRectangles = [];
        }
        drawnItems.addLayer(layer);
        var bounds = layer.getBounds();
        var rectangleCoords = [
            bounds.getSouthWest().lat,
            bounds.getNorthEast().lat,
            bounds.getNorthWest().lng,
            bounds.getSouthEast().lng,
        ];
        app.vue.region.lat_min = String(rectangleCoords[0]);
        app.vue.region.lat_max = String(rectangleCoords[1]);
        app.vue.region.lon_min = String(rectangleCoords[2]);
        app.vue.region.lon_max = String(rectangleCoords[3]);
        app.vue.drawnRectangles.push(layer);

    } else if (event.layerType === 'marker') {
        if(app.vue.markers.length > 0) {
            drawnItems.removeLayer(app.vue.markers[0]);
            app.vue.markers = [];
        }
            drawnItems.addLayer(layer);
    
            var markerCoords = [
                layer.getLatLng().lat, 
                layer.getLatLng().lng
            ];
    
            app.vue.markerCoords.lat = markerCoords[0];
            app.vue.markerCoords.lon = markerCoords[1];
    
            app.vue.markers.push(layer);       
    }
}

app.load_data();