"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
import csv
import pathlib

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()




db.define_table('users',
                Field('content', 'text'),
                Field('user_email', default=get_user_email),
                Field('created_on', 'datetime', default=get_time),
)

db.define_table('checklists',
                Field('latitude', 'double'),    # 纬度；界限
                Field('longitude', 'double'),   #'double'),     #经度
                Field('observation_date', 'string'),  # date that person see bird, datetime.date instance
                Field('time_observations_started', 'string'),               # the 24 hour time that person see bird datetime.time 
                Field('observer_id', 'string'),

                Field('duration_minutes', 'double'),     ###  

                Field('sampling_event_identifier', 'text'),     # Alternative way - efficient
                #Field('sightings_id', 'reference sightings'),   # one way, 
)

db.define_table('species',
                Field('common_name', 'text'),                    # common name
)

db.define_table('sightings',
                Field('checklist_id', 'reference checklists'),   # 对应sampling_event_identifier     # connection between 2 tables

                Field('observation_count', 'integer'),     # the X in csv file will become 0

                Field('species_id', 'reference species'),        # 对应represent the common name of the table species
)

db.commit()



# proj
data_dir = pathlib.Path().resolve().absolute().as_posix() + "/apps/watcher/data"


if db(db.species).isempty():
    with open(f'{data_dir}/species.csv', 'r') as f:         # add path to the file
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            db.species.insert(common_name=row[0])


def safe_float(s):
    try:
        return float(s)
    except Exception as e:
        return None

def safe_int(s):
    try:
        return int(s)
    except Exception as e:
        return 0

if db(db.checklists).isempty():     
    with open(f'{data_dir}/checklists.csv', 'r') as f:
        total = 0
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            try:
                duration_minutes = row[6] if row[6] else "-1" 
                db.checklists.insert(latitude=safe_float(row[1]),
                                 longitude=safe_float(row[2]),
                                 observation_date=row[3],
                                 time_observations_started=row[4],
                                 observer_id=row[5],
                                 duration_minutes=safe_float(duration_minutes),
                                 sampling_event_identifier=row[0],
                                 )
                total += 1
            except Exception as e:
                print(f"Error processing row {row}: {e}")
        print("Inserted", total, "lines")




# Let's build a dictionary from species names to species IDs. 
rows = db(db.species.id > 0).select()       ### rows = db(db.species.ALL).select()
species_name_to_id = {}
for row in rows:
    species_name_to_id[row.common_name] = row.id

# Same, to map observation_event_identifier to checklist_id. 
rows = db(db.checklists.id > 0).select()    ### rows = db(db.checklistsALL).select()
obs_id_to_id = {}
for row in rows:
    obs_id_to_id[row.sampling_event_identifier] = row.id



if db(db.sightings).isempty():
    with open(f'{data_dir}/sightings.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            # # Fix, you have to use the column number for the sampling_event_identifier
            # checklist_id = db(db.checlists.sampling_event_identifier == row[0]).select(db.checklist.id).first()
            # db.sightings.insert(name=row[1], checklist_id=checklist_id)
            
            # Alternative way - efficient
            db.sightings.insert(
                species_id=species_name_to_id.get(row[1]),      # common name
                observation_count=safe_int(row[2]),
                checklist_id=obs_id_to_id.get(row[0]),          # sampling event
            )


db.commit()

