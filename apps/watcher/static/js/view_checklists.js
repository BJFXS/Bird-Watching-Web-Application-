"use strict";

let app = {};

app.data = {
    data: function() {
        return {
            my_checklists: [],
            my_sightings:[],
            is_Fetching:true,
            species_list: [],
        };
    },
    methods: {
        filter_species: function(checklist_id) {
            let toReturn = this.my_sightings.filter((el) => (el.sightings.checklist_id == checklist_id ))
            console.log(this.my_sightings)
            console.log(toReturn)
            return toReturn
        },

        submit_changes: function(checklist_id, checklist_observation_date, checklist_time_observations_started, checklist_latitude, checklist_longitude, checklist_duration_minutes) {
            let sightings_to_edit = this.filter_species(checklist_id) //nice little trick to ensure only entries belonging to this checklist are sent to DB
            let ready_for_db = true
            for (let sighting of sightings_to_edit) {
                //if (sighting.sightings.temporary) {
                    let found = this.species_list.find((el) => el.common_name.toLowerCase() == sighting.species.common_name.toLowerCase())
                    if (found != undefined) {
                        console.log(found)
                        sighting.species.common_name=found.common_name
                        sighting.sightings.species_id=found.id
                        console.log("VALID SIGHTING ", sighting)
                    }

                    else {
                        ready_for_db = false
                        console.log("ERROR, INVALID NAME")
                        window.alert("Error: " + sighting.species.common_name + " is not a valid bird species.");
                    }
                    console.log(sighting.species.observation_count)
                    if (sighting.sightings.observation_count == 0 || sighting.sightings.observation_count == undefined) {
                        ready_for_db = false
                        console.log("ERROR, INVALID COUNT")
                        window.alert("Error: " + sighting.species.common_name + " has 0 sightings. Please insert a non-zero number.");
                    }



                //}
                
            }

            if (ready_for_db) {
                axios.post(update_checklist_url, {
                    checklist_id: checklist_id,
                    checklist_observation_date:checklist_observation_date,
                    checklist_time_observations_started:checklist_time_observations_started,
                    checklist_latitude:checklist_latitude,
                    checklist_longitude:checklist_longitude,
                    checklist_duration_minutes:checklist_duration_minutes,
                    sightings_to_edit:sightings_to_edit
                }).then(function(ret) {
                    app.vue.my_checklists = ret.data.my_checklists
                    app.vue.my_sightings = ret.data.my_sightings
                    app.vue.is_Fetching = false
                    window.alert("Checklist successfully edited.");
                })
            }

            
        },

        add_row: function(checklist_id) {
            console.log(checklist_id)
            this.my_sightings.push({"sightings" : {checklist_id: checklist_id, observation_count: 0, species_id: -1, id: -1, temporary:true}, "species" : {common_name: "", valid_name: false}})
            console.log(this.my_sightings)
        },

        
        delete_sighting: function(sighting) {
            console.log(sighting)
            sighting.sightings.checklist_id = -1 //this is incredibly hacky - but keeps it from being displayed on the front end

            axios.post(delete_sighting_url, { //should be safe - if sighting_id does not exist, it won't be deleted from the DB
                sighting_id: sighting.sightings.id
            })

        },

        delete_checklist: function(checklist) {

            axios.post(delete_checklist_url, { //should be safe - if sighting_id does not exist, it won't be deleted from the DB
                checklist_id: checklist.id
            })
            checklist.render = false

        },

        go_to_checklists: function() {
            window.location.href = checklist_url
        }
    },

    
    computed: {
    },
            
};


app.load_data = function () {
    console.log("loading...")
    app.vue = Vue.createApp(app.data).mount("#app");
    axios.get(get_my_checklists_url).then(function(ret) {
        app.vue.my_checklists = ret.data.my_checklists
        console.log(ret.data.my_checklists)
        app.vue.my_sightings = ret.data.my_sightings
        console.log(app.vue.my_sightings)
        app.vue.is_Fetching = false
    })

    axios.get(get_species_url).then(function(ret) {
        console.log(ret.data.species)
        
        app.vue.species_list = ret.data.species
    })
}
app.load_data();


// This is the initial data load.

