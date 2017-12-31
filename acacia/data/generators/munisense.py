'''
Created on Dec 21, 2017

@author: theo
'''
from django.conf import settings
from acacia.data.generators.generator import Generator
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import pytz
from acacia.data.models import MeetLocatie, aware
from acacia.data.util import slugify
import pandas as pd
import json

fields = {
  "object_id": 0,
  "creation_timestamp": 0,
  "creation_uid": "string",
  "description": "string",
  "dino_id": "string",
  "bro_id": "string",
  "installation_notes": "string",
  "opendata_text": "string",
  "opendata_image": "string",
  "owner_id": "string",
  "delivery_accountable_party_id": "string",
  "maintenance_responsible_party_id": "string",
  "tube_status": "string",
  "node": {},
  "node_eui64": 0,
  "node_name": "string",
  "node_description": "string",
  "node_zcl_version": "string",
  "node_model": "string",
  "node_datecode": "string",
  "node_power_source": "string",
  "node_alarm_mask": 0,
  "node_alarm_status": 0,
  "node_alarm_count": 0,
  "node_temperature": 0,
  "node_identify_time": 0,
  "node_data_age": 0,
  "node_duplicate_frames": 0,
  "node_rssi": 0,
  "node_tx_errors": 0,
  "node_mains_voltage": 0,
  "node_battery_voltage": 0,
  "node_node_voltage": 0,
  "node_time": 0,
  "node_time_status": 0,
  "node_time_timezone": 0,
  "node_time_dst_start": 0,
  "node_time_dst_end": 0,
  "node_time_dst_shift": 0,
  "well_covering_project_code": "string",
  "well_covering_area_code": "string",
  "well_covering_cover_code": "string",
  "well_covering_altitude_reference": "string",
  "well_covering_surface_level": {},
  "well_covering_barometric_pressure": 0,
  "well_covering_barometric_pressure_in_Pa": 0,
  "well_covering_barometric_pressure_last_result_age": 0,
  "well_covering_barometric_pressure_mh2O": 0,
  "well_covering_reference_id": 0,
  "alarm_level": 0,
  "alarm_high": 0,
  "alarm_low": 0,
  "warning_high": 0,
  "warning_low": 0,
  "well_properties_aquifer": "string",
  "well_properties_depth": {},
  "well_properties_diameter": 0,
  "well_head_reference": 0,
  "well_properties_well_head": {},
  "well_properties_filter_upper": 0,
  "well_properties_filter_lower": 0,
  "well_properties_filter_upper_reference": 0,
  "well_properties_filter_lower_reference": 0,
  "well_properties_filter_reference": "string",
  "well_properties_drill_survey_date": 0,
  "well_properties_drill_survey_operator_name": "string",
  "sensor_distance_to_water_level": "string",
  "sensor_offset": "string",
  "distance_calibration": "string",
  "water_level_available": 0,
  "water_level_validation_measurement": "string",
  "water_level_validation_timestamp": "string",
  "water_level_validation_measurement_object": "string",
  "water_level_calibration_date": 0,
  "water_level_calibration_operator_name": "string",
  "water_level_calibration_level": 0,
  "water_level_at_validation_moment": 0,
  "water_level": 0,
  "water_absolute_pressure": 0,
  "water_level_calculated": 0,
  "water_level_alarm": 0,
  "water_level_warning": 0,
  "water_temperature_available": 0,
  "water_temperature": 0,
  "water_conductivity_available": 0,
  "water_conductivity": 0,
  "keller_sensor_available": 0,
  "keller_sensor_type": "string",
  "keller_sensor_model": "string",
  "keller_sensor_serial": "string",
  "keller_sensor_version": 0,
  "keller_sensor_control": 0,
  "keller_sensor_status": 0,
  "analog_pressure_sensor_available": 0,
  "analog_pressure_sensor_type": "string",
  "analog_pressure_sensor_model": "string",
  "analog_pressure_sensor_serial": "string",
  "analog_pressure_sensor_configuration": 0,
  "analog_pressure_sensor_maximum": 0,
  "analog_pressure_sensor_pressure_calibration": 0,
  "analog_pressure_sensor_control": 0,
  "analog_pressure_sensor_status": 0,
  "analog_sample_time": 0,
  "baro_sample_time": 0,
  "connect_cycle": 0,
  "schlumberger_diver_available": 0,
  "schlumberger_diver_id": "string",
  "schlumberger_diver_location_well_head": 0,
  "schlumberger_diver_type": "string",
  "schlumberger_diver_model": "string",
  "schlumberger_diver_serial": {},
  "schlumberger_diver_sensor_offset": {},
  "schlumberger_diver_sensor_offset_reference": 0,
  "schlumberger_diver_calibration_offset": {},
  "schlumberger_diver_calibration_offset_reference": 0,
  "meteo_id": 0,
  "meteo": {},
  "precipitation_gross": 0,
  "precipitation_gross_nine_day_sum": 0,
  "potential_evaporation": 0,
  "precipitation_net": 0,
  "precipitation_net_positive": 0,
  "precipitation_net_negative": 0,
  "vegetation_factor": 0,
  "logging_log": 0,
  "logging_start_date_time": 0,
  "logging_end_date_time": 0,
  "logging_collection_date": 0,
  "logging_collection_person": "string",
  "logging_validation_absolute_max": 0,
  "logging_validation_absolute_min": 0,
  "stats_starttime": 0,
  "stats_endtime": 0,
  "stats_min": 0,
  "stats_max": 0,
  "stats_rlg": 0,
  "stats_rhg": 0,
  "stats_gg": 0,
  "stats_count": 0,
  "stats_starttime_hidden": 0,
  "stats_endtime_hidden": 0,
  "stats_min_hidden": 0,
  "stats_max_hidden": 0,
  "stats_rlg_hidden": 0,
  "stats_rhg_hidden": 0,
  "stats_gg_hidden": 0,
  "stats_count_hidden": 0,
  "stats_relative_rlg": 0,
  "stats_relative_rhg": 0,
  "water_level_90th_percentile": 0,
  "water_level_75th_percentile": 0,
  "water_level_25th_percentile": 0,
  "water_level_10th_percentile": 0,
  "surfacewater_level_min": 0,
  "surfacewater_level_max": 0,
  "surfacewater_level_summer": 0,
  "surfacewater_level_winter": 0,
  "import_logger_water_level": 0,
  "water_level_validated": {},
  "water_level_filtered": {},
  "water_level_filtered_annotation_state": {},
  "validation_criteria_id": 0,
  "validation_displayrule_id": 0,
  "well_depth_reference": 0,
  "sensor_offset_reference": 0,
  "water_level_filtered_water_level_validated": "string",
  "water_level_filtered_raw_value": "string",
  "water_level_filtered_value": "string",
  "water_level_filtered_automatic_validation_state": "string",
  "water_level_filtered_automatic_validation_rule_name": "string",
  "water_level_filtered_automatic_validation_rule": "string",
  "water_level_filtered_manual_validation_state": "string",
  "water_level_filtered_manual_validation_override": "string",
  "water_level_filtered_manual_validation_comment": "string",
  "water_level_filtered_manual_validation_uid": "string",
  "water_level_filtered_manual_validation_timestamp": "string",
  "location": {},
  "location_description": "string",
  "location_gis_description": "string",
  "location_timezone": "string",
  "location_id": 0,
  "location_latitude": "string",
  "location_longitude": "string",
  "location_lat_long_comma_sep": "string",
  "location_rd_x": "string",
  "location_rd_y": "string",
  "location_rd_xy_comma_sep": "string",
  "object_type": "string",
  "composite_description": "string",
  "simple_description": "string",
  "groups": {}
}

class Munisense(Generator):

    def download(self, **kwargs):
        api = kwargs.get('url',settings.MUNISENSE_API)
        endpoint = '/groundwaterwells/{id}/{property}/query/{start_timestamp}'
        prop = kwargs.get('property','water_level_validated')
        loc = kwargs.get('meetlocatie',None)
        if not loc:
            raise ValueError('Meetlocatie not defined')
        if isinstance(loc, MeetLocatie):
            loc = loc.name
        object_id = kwargs.get('object_id',loc) 
        callback = kwargs.get('callback',None)
        start = kwargs.get('start') or datetime(2017,1,1)
        start = aware(start,pytz.utc)
        username = kwargs.get('username',settings.MUNISENSE_USERNAME)
        password = kwargs.get('password',settings.MUNISENSE_PASSWORD)
        headers = {'Accept': 'application/json' }
        url = '{api}{endpoint}'.format(api=api,endpoint=endpoint)
        url = url.format(id=object_id,property=prop,start_timestamp=start.isoformat())
        payload = {'rowcount': 1000}
        
        result = {}
        index = 0
        while True:
            response = requests.get(url,headers=headers,params=payload,auth=HTTPBasicAuth(username,password))
            response.raise_for_status()
            index += 1
            filename = kwargs.get('filename','{id}_{timestamp}_{index}.json'.format(id=slugify(loc),timestamp=start.strftime('%y%m%d%H%M'),index=index))
            result[filename]=response.text
            try:
                data = response.json()
                link_next = data['meta']['link_next']
                if link_next:
                    url = '{api}{endpoint}'.format(api=api,endpoint=link_next)
                else:
                    break
            except:
                break
        if callback:
            callback(result)
        return result

    def download_wells(self,**kwargs):
        api = kwargs.get('url',settings.MUNISENSE_API)
        endpoint = '/users/{id}/groundwaterwells'
        fields = ['object_id',
                  'description',
                  'dino_id',
                  'bro_id', 
                  'owner_id', 
                  'location_latitude',
                  'location_longitude',
                  'location_description',
                  'location_gis_description',
                  'location_timezone',
                  'location_id',
                  'well_covering_altitude_reference',
                  'well_covering_surface_level',
                  'well_properties_aquifer',
                  'well_properties_depth',
                  'well_properties_diameter',
                  'well_head_reference',
                  'well_properties_well_head',
                  'well_properties_filter_upper',
                  'well_properties_filter_lower',
                  'well_properties_filter_upper_reference',
                  'well_properties_filter_lower_reference',
                  'well_properties_filter_reference',
                  'schlumberger_diver_available',
                  'schlumberger_diver_id',
                  'schlumberger_diver_location_well_head',
                  'schlumberger_diver_type',
                  'schlumberger_diver_model',
                  'schlumberger_diver_serial',
                  'schlumberger_diver_sensor_offset',
                  'schlumberger_diver_sensor_offset_reference',
                  'schlumberger_diver_calibration_offset',
                  'schlumberger_diver_calibration_offset_reference',
                  ]
        username = kwargs.get('username',settings.MUNISENSE_USERNAME)
        password = kwargs.get('password',settings.MUNISENSE_PASSWORD)
        headers = {'Accept': 'application/json' }
        url = '{api}{endpoint}'.format(api=api,endpoint=endpoint)
        url = url.format(id=username)
        offset = 0
        payload = {'offset':0, 'rowcount': 100, 'fields':','.join(fields)}
        done = False
        while not done:
            response = requests.get(url,headers=headers,params=payload,auth=HTTPBasicAuth(username,password))
            response.raise_for_status()
            offset += 100
            payload['offset']=offset
            done = len(response.json()) < 100
            yield response
            
    def get_data(self, fil, **kwargs):
        contents = json.load(fil)
        data = contents['results']
        records = [(r['timestamp'],r['water_level_validated'],r['raw_value'],r['value']) for r in data]
        df = pd.DataFrame.from_records(records,columns=['timestamp','water_level_validated', 'raw_value', 'value'])
        index = pd.DatetimeIndex(df['timestamp'])
        df.set_index(index,drop=True,inplace=True)
        return df
    
    def get_parameters(self, fil):
        return {
            'water_level_validated': {'description': 'validated water level', 'unit': 'm NAP'},
            'raw_value': {'description': 'water level', 'unit': 'm NAP'},
            'value': {'description': 'water level', 'unit': 'm NAP'},
        }
