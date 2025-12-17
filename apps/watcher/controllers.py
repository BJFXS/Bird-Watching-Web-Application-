"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
import datetime
import logging
import random
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma
url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # my_callback_url = URL('my_callback', signer=url_signer),
        location_url = URL('location', signer=url_signer),
        get_species_url = URL('get_species', signer=url_signer),
        get_sightings_url = URL('get_sightings', signer=url_signer),
        search_species_url = URL('search_species', signer=url_signer),
    )

@action('location')
@action.uses('location.html', db, url_signer, auth.user)   #auth, 
def location():
    return dict(
        location_callback_url = URL('location_callback', signer=url_signer),
        species_data_url = URL('species_data', signer=url_signer),  # Modified: Added species_data_url
    )



@action('checklist')
@action.uses('checklist.html', db, url_signer, auth.user)   #auth, 
def checklist(): 
    print("User ", get_user_email(), " logged in")
    if (get_user_email() == None):
        redirect(URL('auth/login'))

    else:
        return dict(
            get_species_url = URL('get_species', signer=url_signer),
            post_checklist_url = URL('post_checklist', signer=url_signer),
            view_checklists_url = URL('view_checklists', signer=url_signer),
            index_url = URL('index', signer=url_signer)
        )


@action('statistics')
@action.uses('statistics.html', db, url_signer, auth.user)   #auth,
def statistics():
    return dict(
        user_statistics_url=URL('get_statistics', signer=url_signer),
    )






@action('location_callback', method=['POST']) # auth, 
@action.uses(db, session)
def location_callback():
    data = request.json
    region = data.get('region', {})

    ### 从checklist表格里提取region内的checklists，得到它们的ID

    lat_min = float(region.get('lat_min', 0))
    lat_max = float(region.get('lat_max', 0))
    lon_min = float(region.get('lon_min', 0))
    lon_max = float(region.get('lon_max', 0))

    logging.info(type(lat_min))
    logging.info(f"lat_min={lat_min}, lat_max={lat_max}, lon_min={lon_min}, lon_max={lon_max}")
    logging.info(f"Database latitude type: {type(db.checklists.latitude)}")

    # Cast the database fields to float for comparison
    lat_field = db.checklists.latitude.cast('float')
    lon_field = db.checklists.longitude.cast('float')
    logging.info(type(lat_field))

    # get the checklists in the region
    checklist_query = (lat_field >= lat_min) & (lat_field <= lat_max) & \
                  (lon_field >= lon_min) & (lon_field <= lon_max)
    checklist = db(checklist_query).select(db.checklists.id) 


    if not checklist:
        logging.info("No checklists found in the region.")
        return dict(species_data=[], contributors=[]) 
    # get the checklists in the region
    """# get the checklists in the region
    checklist = db((db.checklists.latitude >= lat_min) &
                    (db.checklists.latitude <= lat_max) &
                    (db.checklists.longitude >= lon_min) &
                    (db.checklists.longitude <= lon_max)).select(db.checklists.id)

    if not checklist:
        logging.info("No checklists found in the region.")
        return dict(species_data=[], contributors=[])  # Modified
    """


    
    # get the checklists in the region
    checklist_ids = [c.id for c in checklist]
    n = len(checklist_ids)
    #logging.info(f"There are {n} ids")  # 512       ### 正确


    ### 然后去 sightings和species表格 里提取这些IDs的 observation_count和common_name.
    query = (db.sightings.checklist_id.belongs(checklist_ids)) & (db.sightings.species_id == db.species.id)  #对
    """rows = db(query).select(db.species.common_name, 
                            db.sightings.id.count(),                  
                            db.sightings.observation_count.sum(),     # Sum the observation_count for the species
                            db.sightings.checklist_id.count(),        # Count the number of checklists(rows) for the species
                            groupby=db.sightings.species_id)"""
    #从database检索 species的common_name、 sightings的observation_count 和 checklist_id
    rows = db(query).select(db.species.common_name, 
                            db.sightings.observation_count,     # Removed sum() operation
                            db.sightings.checklist_id)          # Removed count() operation
    m = len(rows)
    #logging.info(f"There are {m} rows")  # 7760       ### 正确
    # row = [common_name, observation_count, checklist_id]


    # 将相同common_name的row提取出来，得到此species的checklists总数，然后sum此species的observation_count
    species_data_dict = {}
    for row in rows:
        common_name = row.species.common_name
        observation_count = row.sightings.observation_count or 0  # Modified

        if common_name not in species_data_dict:
            species_data_dict[common_name] = {
                'sighting_count': 0,
                'checklist_count': 0
            }
        species_data_dict[common_name]['sighting_count'] += observation_count
        species_data_dict[common_name]['checklist_count'] += 1


    species_data = []
    for common_name, data in species_data_dict.items():
        species_data.append({
            'common_name': common_name,
            'sighting_count': data['sighting_count'],
            'checklist_count':data['checklist_count']
        })

    #logging.info(f"species_data: {species_data}")


    contributors_query = db(db.checklists.id.belongs(checklist_ids)
                            ).select(db.checklists.observer_id, 
                                    db.checklists.id) 
    
    contributors_dict = {}
    for row in contributors_query:
        observer_id = row[db.checklists.observer_id]
        if observer_id not in contributors_dict:
            contributors_dict[observer_id] = 0
        contributors_dict[observer_id] += 1

    contributors = sorted(contributors_dict.items(), key=lambda item: item[1], reverse=True)[:5]
    contributors = [{'observer_id': observer_id, 'checklist_count': count} for observer_id, count in contributors]

    return dict(species_data=species_data, contributors=contributors)

@action('species_data', method=['POST'])
@action.uses(db, session)
def species_data():
    data = request.json
    species_name = data.get('common_name')
    region = data.get('region', {})


    lat_min = float(region.get('lat_min', 0))
    lat_max = float(region.get('lat_max', 0))
    lon_min = float(region.get('lon_min', 0))
    lon_max = float(region.get('lon_max', 0))

    logging.info(type(lat_min))
    logging.info(f"lat_min={lat_min}, lat_max={lat_max}, lon_min={lon_min}, lon_max={lon_max}")
    logging.info(f"Database latitude type: {type(db.checklists.latitude)}")

    # Cast the database fields to float for comparison
    lat_field = db.checklists.latitude.cast('float')
    lon_field = db.checklists.longitude.cast('float')
    logging.info(type(lat_field))

    # get the checklists in the region
    checklist_query = (lat_field >= lat_min) & (lat_field <= lat_max) & \
                  (lon_field >= lon_min) & (lon_field <= lon_max)
    checklist = db(checklist_query).select(db.checklists.id) 


    if not checklist:
        logging.info("No checklists found in the region.")
        return dict(species_data=[], contributors=[]) 
    
    

    """    
    lat_min = region.get('lat_min', 0)
    lat_max = region.get('lat_max', 0)
    lon_min = region.get('lon_min', 0)
    lon_max = region.get('lon_max', 0)
    logging.info(f"lat_min={lat_min}, lat_min={lat_min}, lon_min={lon_min}, lon_max={lon_max}")

    # get the checklists in the region
    checklist = db((db.checklists.latitude >= lat_min) &
                    (db.checklists.latitude <= lat_max) &
                    (db.checklists.longitude >= lon_min) &
                    (db.checklists.longitude <= lon_max)).select(db.checklists.id)
    if not checklist:
        logging.info("No checklists found in the region.")
        return dict(dates=[], counts=[])
    """
    # extract checklist 'id's
    checklist_ids = [c.id for c in checklist]
    n = len(checklist_ids)
    logging.info(f"There are {n} ids")  # 512   ### 正确


    # 条件：需要属于这个region,即包括在checklist_id内， ～?～，  寻找这个species_name 
    query = ((db.sightings.checklist_id.belongs(checklist_ids)) & 
             (db.checklists.id == db.sightings.checklist_id) &  ### select 里有checklists，这里就必须加上一个条件，不然下面会变成selct所有checklists的
             (db.sightings.species_id == db.species.id) & 
             (db.species.common_name == species_name) &
             (db.sightings.observation_count > 0))
    # logging.info("there are {} rows in species".format(db(db.species.id > 0).count()))
    # logging.info("there are {} rows in sightings".format(db(db.sightings.id > 0).count()))
    # logging.info(f"query={query}")
    # 提取：每个符合条件的checklists的 observation_date 和 observation_count
    rows = db(query).select(db.sightings.observation_count, 
                            db.checklists.observation_date)
    
    m = len(rows)
    logging.info(f"There are {m} rows")    # 51036 rows，when species_name='Cackling Goose'
    # rows = (observation_count, observation_date)
    
    ##### 检验：gpt验算rows数量
    ##### 结果：rows数量错误，应为6
    # 为能到原因
    # 条件只多了：  db.species.common_name == species_name


    sightings_by_date = {}
    for row in rows:
        date = row.checklists.observation_date 
        count = row.sightings.observation_count
        if count is None:
            count = 0  # Modified: Handle None values for observation_count
        else:
            count = int(count)
        sightings_by_date[date] = sightings_by_date.get(date, 0) + count


    dates = sorted(sightings_by_date.keys())
    counts = [sightings_by_date[date] for date in dates]

    logging.info(f"Dates: {dates}")
    logging.info(f"Counts: {counts}")

    return dict(dates=dates, counts=counts)








@action('get_species', method="GET")
@action.uses(db, session)
def get_species():
    print("getting species...")
    species = db(db.species).select(orderby=db.species.common_name).as_list()
    #print(species)
    return dict(species=species)

@action('post_checklist', method="POST")
@action.uses(db, session, auth.user)
def post_checklist():
    sightings_list = request.json.get('sightings_list')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    print(date)
    time = datetime.datetime.now().strftime("%H:%M:%S")
    print(time)
    user_id = get_user_email()
    duration = request.json.get('duration')
    sampling_event_identifier="S" + str(random.randint(0, 1000000))
    print("inserting ", sampling_event_identifier, " ", duration, " ", user_id, " ", time, " ", date, " ", latitude, " ", longitude, " into checklist_entry db")
    checklist_entry = db.checklists.insert(
        latitude=latitude, 
        longitude=longitude, 
        observation_date=date, 
        time_observations_started=time, 
        observer_id=user_id,
        duration_minutes=duration,
        sampling_event_identifier = sampling_event_identifier
    )
    for sightings in sightings_list:
        sighting_species_id = sightings[0]
        sighting_observation_count = sightings[1]
        print("inserting ", sighting_species_id, " ", sighting_observation_count, " into sightings db")
        db.sightings.insert(
            species_id = sighting_species_id,
            observation_count = sighting_observation_count,
            checklist_id = checklist_entry
        )
        
    return

@action('view_checklists', method=["GET", "POST"])
@action('view_checklists/<path:path>', method=["GET", "POST"])
@action.uses('view_checklists.html', db, auth.user)
def view_checklists():
    print("viewing user ", get_user_email(), " checklists")
    return dict(
        get_my_checklists_url=URL('get_my_checklists'),
        update_checklist_url=URL('update_checklist'),
        get_species_url=URL('get_species'),
        delete_sighting_url=URL('delete_sighting'),
        delete_checklist_url=URL('delete_checklist'),
        checklist_url=URL('checklist')
    )

@action('update_checklist', method=['POST', 'GET'])
@action.uses(db, session, auth.user)
def update_checklist():
    checklist_id = request.json.get('checklist_id')
    checklist_observation_date = request.json.get('checklist_observation_date')
    checklist_time_observation_started = request.json.get('checklist_time_observations_started')
    checklist_latitude = request.json.get('checklist_latitude')
    checklist_longitude = request.json.get('checklist_longitude')
    checklist_duration_minutes = request.json.get('checklist_duration_minutes')
    sightings_to_edit = request.json.get('sightings_to_edit')
    db(db.checklists.id == checklist_id).update(
        latitude=checklist_latitude,
        longitude=checklist_longitude,
        observation_date=checklist_observation_date,
        time_observations_started=checklist_time_observation_started,
        duration_minutes=checklist_duration_minutes,
    )

    delete_checklist = 1

    for sighting in sightings_to_edit:
        sighting_internal = sighting["sightings"]
        sighting_id = sighting_internal["id"]
        sighting_count = int(sighting_internal["observation_count"])
        sighting_species_id = sighting_internal["species_id"]
        print(sighting_count)
        if sighting_count == 0:
            print("DELETING")
            db(db.sightings.id == sighting_id).delete()

        else:
            db(db.sightings.id == sighting_id).update(
                observation_count=sighting_count,
                species_id=sighting_species_id
            )
            delete_checklist = 0

        if sighting_id == -1: #sigithing does not exist - added on edit
            print("adding new sighting to db")
            db.sightings.insert(
                species_id = sighting_species_id,
                observation_count = sighting_count,
                checklist_id = checklist_id
            )

    
    if delete_checklist:
        print("DELETING CHECKLIST")
        db(db.checklists.id == checklist_id).delete()


    redirect(URL("get_my_checklists"))
       
@action('get_my_checklists', method='GET')
@action.uses(db, auth.user)  
def get_my_checklists():
    print("getting checklists...")
    checklist_sightings = db((db.sightings.checklist_id == db.checklists.id) & (db.checklists.observer_id == get_user_email()) & (db.sightings.species_id == db.species.id))
    my_checklists=checklist_sightings.select(
        db.checklists.id, 
        db.checklists.latitude, 
        db.checklists.longitude, 
        db.checklists.observation_date, 
        db.checklists.time_observations_started,
        db.checklists.observer_id, 
        db.checklists.duration_minutes, 
        db.checklists.sampling_event_identifier).as_dict().items() #WE WANT TO REMOVE IDENTICAL ENTRIES

    my_sightings = checklist_sightings.select(
        db.sightings.id,
        db.sightings.checklist_id, 
        db.sightings.observation_count, 
        db.sightings.species_id,
        db.species.common_name).as_list() #WE DO NOT WANT TO REMOVE IDENTICAL ENTRIES
    
    print("checklists: ", my_checklists)
    print("sightings: ", my_sightings)
    return dict(my_checklists=my_checklists, my_sightings=my_sightings)


@action('get_sightings', method='GET')
@action.uses(db)
def get_sightings_stats():
    print("RETRIEVING SIGHTINGS DATA")
    species_id = request.params.get("species_id")
    if species_id and species_id != -1:
        query = (db.sightings.species_id == species_id)
    else:
        query = (db.sightings)

    sightings_data = db(query).select(
        db.sightings.observation_count,
        db.checklists.latitude,
        db.checklists.longitude,
        join=db.checklists.on(db.sightings.checklist_id == db.checklists.id)
    ).as_list()

    coordinates = [] 
    for row in sightings_data:
        latitude = row["checklists"]["latitude"]
        longitude = row["checklists"]["longitude"]
        observation_count = row["sightings"]["observation_count"]
        coordinates.append([latitude, longitude, observation_count])

    print("FINISHED RETRIEVING SIGHTINGS DATA")
    return dict(coordinates=coordinates)

@action('delete_sighting', method='POST')
@action.uses(db)
def delete_sighting():
    print("deleting sighting...")
    sighting_id = request.params.get("sighting_id")
    db(db.sightings.id == sighting_id).delete()
    return

@action('delete_checklist', method='POST')
@action.uses(db, auth.user)
def delete_checklist():
    print("called delete_checklist")
    checklist_id = request.params.get("checklist_id")
    print("deleting checklist ", checklist_id)
    db((db.checklists.id == checklist_id) & (db.checklists.observer_id == get_user_email())).delete()
    db(db.sightings.checklist_id == checklist_id).delete() #also delete any sightings associated with this checklist!
    return

@action('search_species', method='GET')
@action.uses(db)
def search_species():
    q = request.params.get("q")
    if q:
        query = db.species.common_name.contains(q)
    else:
        query = (db.species.id > 0)

    species = db(query).select(orderby=db.species.common_name).as_list()
    return dict(species=species)

@action('get_statistics', method="GET")
@action.uses(db, auth.user, session)
def get_species():

    user_email = get_user_email()
    if not user_email:
        return None

    # Join the tables to get the necessary data
    query = (db.checklists.observer_id == user_email) & \
            (db.checklists.id == db.sightings.checklist_id) & \
            (db.sightings.species_id == db.species.id)

    # Fetch data sorted by observation date
    rows = db(query).select(
        db.species.id,
        db.species.common_name,
        db.sightings.observation_count,
        db.checklists.observation_date,
        db.checklists.latitude,
        db.checklists.longitude,
        db.checklists.time_observations_started,
        db.checklists.duration_minutes,
        orderby=db.checklists.observation_date
    )

    # Convert rows to a list of dictionaries
    results1 = []
    results2 = []
    for row in rows:
        # Check if the common name already exists in the results
        common_name_exists = False
        for result1 in results1:
            if result1['common_name'] == row.species.common_name:
                # If it exists, add the observation count from the current row
                result1['observation_count'] += row.sightings.observation_count
                common_name_exists = True
                break
    
        # If the common name does not exist in the results, append a new dictionary
        if not common_name_exists:
            results1.append({
                'species_id': row.species.id,
                'common_name': row.species.common_name,
                'observation_count': row.sightings.observation_count,
                'latitude': row.checklists.latitude,
                'longitude': row.checklists.longitude,
                'time_observations_started': row.checklists.time_observations_started,
                'duration_minutes': row.checklists.duration_minutes,
                'observation_date': row.checklists.observation_date,
            })
    
    for row in rows:
        # Check if the common name already exists in the results
        common_name_exists = False
        for result2 in results2:
            if result2['common_name'] == row.species.common_name:
                # If it exists, add the observation count from the current row
                result2['observation_count'] += row.sightings.observation_count
                result2['observation_date'] = row.checklists.observation_date
                common_name_exists = True
                break
    
        # If the common name does not exist in the results, append a new dictionary
        if not common_name_exists:
            results2.append({
                'species_id': row.species.id,
                'common_name': row.species.common_name,
                'observation_count': row.sightings.observation_count,
                'latitude': row.checklists.latitude,
                'longitude': row.checklists.longitude,
                'time_observations_started': row.checklists.time_observations_started,
                'duration_minutes': row.checklists.duration_minutes,
                'observation_date': row.checklists.observation_date,
            })

    return dict(results1=results1, results2=results2)
