"use strict";

let app = {};

app.data = {
    data: function() {
        return {
            sightings: [],
            speciesData: [],
            region: {},
            contributors: [], 
            showGraph: false, // Modified: Added showGraph
            graphTitle: '', // Modified: Added graphTitle
            chart: null, // Modified: Added chart
        };
    },
    methods: {
        fetchLocationData() {
            console.log("Fetching data for region:", this.region);

            axios.post(location_callback_url, { region: this.region }).then((response) => {
                console.log("Fetched data:", response.data);
                this.speciesData = response.data.species_data;
                this.contributors = response.data.contributors;  // Modified
            }).catch((error) => {
                console.error(error);
            });
        },
        


        fetchSpeciesData(common_name) { // new code
            console.log("Fetching species data for:", common_name);
            axios.post(species_data_url, { common_name: common_name, region: this.region }).then((response) => {
                console.log("Fetched species data:", response.data);
                this.showGraph = true; // new code
                this.graphTitle = `Sightings for ${common_name} over time`; // new code
                this.$nextTick(() => { // new code
                    this.renderChart(response.data); // new code
                });
            }).catch((error) => {
                console.error(error);
            });
        },

        renderChart(data) { // new code
            if (this.chart) {
                this.chart.destroy();
            }
            const ctx = document.getElementById('speciesChart').getContext('2d'); // new code
            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Number of Sightings',
                        data: data.counts,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Number of Sightings'
                            }
                        }
                    }
                }
            });
        }


    },
    mounted() {
        this.region = JSON.parse(localStorage.getItem('selectedRegion')) || {};
        console.log("Mounted with region:", this.region);
        this.fetchLocationData();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");
