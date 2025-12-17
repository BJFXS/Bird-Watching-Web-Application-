"use strict";

let app = {};

app.data = {    
    // Define Vue data properties
    data: function() {
        return {
            bird_name: [],
            first_seen: [],
            most_recently_seen: [],
            current_query: '',
            query: '',
            show_first_seen: true,
            show_recently_seen: false,
            selected_bird: null  // Added to track the selected bird
        };
    },

    // Define Vue methods
    methods: {

        // Method to set the search query
        select_query() {
            this.query = this.current_query; 
        },

        set_first_seen() {
            this.show_first_seen = true;
            this.show_recently_seen = false;
            this.selected_bird = null;  // Reset selected bird when switching lists
        },

        set_recently_seen() {
            this.show_recently_seen = true;
            this.show_first_seen = false;
            this.selected_bird = null;  // Reset selected bird when switching lists
        },

        select_bird(bird) {
            this.selected_bird = bird;  // Set the selected bird
        },
    },

    // Define Vue computed properties
    computed: {
        // Computed property to filter birds based on search query
        filtered_list() {

            if (this.show_first_seen) {
                if (this.query == "") {
                    return this.first_seen;
                }
                // Filter birds based on search query (case-insensitive)
                return this.first_seen.filter(bird => 
                    bird.common_name.toLowerCase().includes(this.query.toLowerCase())
                );
            }

            if (this.show_recently_seen) {
                if (this.query == "") {
                    return this.most_recently_seen;
                }
                // Filter birds based on search query (case-insensitive)
                return this.most_recently_seen.filter(bird => 
                    bird.common_name.toLowerCase().includes(this.query.toLowerCase())
                );
            }
        }
    }
};

// Mount Vue instance to #app element
app.vue = Vue.createApp(app.data).mount("#app");

// Load the data from the server
app.load_data = function () {

    // Make a GET request to the server endpoint with the latitude and longitude parameters
    axios.get(user_statistics_url).then((response) => {
        console.log(response)
        this.vue.first_seen = response.data.results1;
        this.vue.most_recently_seen = response.data.results2;
        console.log(this.vue.first_seen)
    }).catch((error) => {
        console.error("Error loading data from server:", error);
    });
};

// Load data on page load
app.load_data();
