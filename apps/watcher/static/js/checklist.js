"use strict";
var time = 0
var interval = setInterval( increment, 1000);
function increment(){
    console.log(app.vue.timer_running)
    if (app.vue.timer_running) {
        time++
        let string = "" + Math.floor((time/60)) + "m " + (time % 60) + "s"
        app.vue.current_time = string
        console.log(string)
    }

}
function geo_location_success(pos) {
    let sightings_list = []
    for (let species of app.vue.species_list) {
        if (app.vue.checklist_seen[species.id] != null && app.vue.checklist_seen[species.id] != "") {
            console.log(app.vue.checklist_seen[species.id])
            let sighting = new Array(2)
            sighting[0] = species.id
            sighting[1] = app.vue.checklist_seen[species.id]
            sightings_list.push(sighting)
        }  
    }
    if (sightings_list.length != 0) {
        console.log(sightings_list)
        axios.post(post_checklist_url, {
            sightings_list: sightings_list,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            duration: Math.floor(time / 60)
        }).then(function(ret) {
            window.alert("Checklist successfully submitted.")
        })
    }

    else {
        window.alert("Error: Checklist Empty.")
    }

}   

function geo_location_failure(pos){
    window.alert("Please enable location sharing.")
}
let app = {};

app.data = {
    data: function() {
        return {
            species_list: [],
            filtered_species_list: [],
            checklist_seen: [],
            bird_search_text: "",
            current_time: 0,
            timer_running: false
        };
    },
    methods: {
        geolocation_error: function() {
            switch(error.code) {
                case error.PERMISSION_DENIED:
                  x.innerHTML = "User denied the request for Geolocation."
                  break;
                case error.POSITION_UNAVAILABLE:
                  x.innerHTML = "Location information is unavailable."
                  break;
                case error.TIMEOUT:
                  x.innerHTML = "The request to get user location timed out."
                  break;
                case error.UNKNOWN_ERROR:
                  x.innerHTML = "An unknown error occurred."
                  break;
              }
        },
        incriment_seen: function(id) {
            if (this.checklist_seen[id] == null) {
                this.checklist_seen[id] = 1
            }
            else {
                this.checklist_seen[id]++
            }
        },

        submit_checklist: function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(geo_location_success, geo_location_failure)
            }

        },

        go_to_my_checklists() {
            window.location.href = my_checklist_url;
        },

        toggle_timer: function() {
            time = 0
            this.current_time = time
            let string = "" + Math.floor((time/60)) + "m " + (time % 60) + "s"
            app.vue.current_time = string
            this.timer_running = !this.timer_running
        },

        updateSearch: function(bird_search_text) {
            this.filtered_species_list=this.species_list.filter((species) => species.common_name.toLowerCase().includes(bird_search_text.toLowerCase()))
        },

        go_to_index: function() {
            window.location.href = index_url;
        },
    }
};

app.vue = Vue.createApp(app.data).mount("#app");
app.load_data = function () {
    console.log("loading...")
    axios.get(get_species_url).then(function(ret) {
        console.log(ret.data.species)
        
        app.vue.species_list = ret.data.species
    })
}

// This is the initial data load.
app.load_data();

