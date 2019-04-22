"""
TODO: in the future, we might want to show vehicles positions both from scheduled (GTFS) and real-time (GTFS-RT) datasets ...
      in that tobe (todo) world, we should define a single 'vehicle' service with Swagger, autogen the DAOs in OTT's api
      section, and then use both gtfsdb and gtfsdb_realtime to populate 2 varities of object / service
"""
import datetime
from ott.utils import geo_utils

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def make_vehcile(v, i):
    """
    :return a geojson property map for a vehicle...:
    """
    # import pdb; pdb.set_trace()

    ret_val = {
        "properties": {
            "~unique-id~": str(i),
            "lon": -000.111,
            "lat": 00.111,
            "heading": float(v.bearing),

            # old schedule vars for map
            "tripNumber": v.trip_id,
            "routeNumber": 1,
            "routeNumberPadded": "001",

            "agencyId": v.agency,
            "stopId": v.stop_id,
            "stopSequence": v.stop_seq,
            "routeId": v.route_id,
            "tripId": v.trip_id,
            "shapeId": v.shape_id,
            "directionId": v.direction_id,
            "blockId": v.block_id,

            "status": v.status,
            "vehicleNumber": v.vehicle_id,
            "destination": v.headsign,
            "minutes": 1,
            "seconds": 11,
            "reportDate": "11.11.2111 11:11 pm"
        },
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [-0.111, 0.111]
        }
    }

    _set_coord(ret_val, float(v.lat), float(v.lon))
    _set_time(ret_val, v.timestamp)
    _set_route_number(ret_val)

    return ret_val


def _set_coord(vehicle, lat, lon, convert="GOOGLE"):
    vehicle["properties"]['lon'] = lon
    vehicle["properties"]['lat'] = lat

    # convert if requested...then set geojson coordinates field
    x = lon; y = lat
    if convert == "OSPN":
        x, y = geo_utils.to_OSPN(lon, lat)
    if convert == "GOOGLE" or convert == "900913":
        x, y = geo_utils.to_meters(lon, lat)
        #x, y = geo_utils.to_900913(lon, lat)
    vehicle["geometry"]["coordinates"] = [x, y]


def _set_time(vehicle, timestamp):
    ts = float(timestamp)
    t = datetime.datetime.fromtimestamp(ts)
    pretty_date_time = t.strftime('%x %I:%M %p').replace(" 0", " ")

    diff = datetime.datetime.now() - t
    min_sec_diff = divmod(diff.days * 86400 + diff.seconds, 60)

    vehicle["properties"]['minutes'] = min_sec_diff[0]
    vehicle["properties"]['seconds'] = min_sec_diff[1]
    vehicle["properties"]['reportDate'] = str(pretty_date_time)


def _set_route_number(vehicle):
    try:
        route_id = vehicle["properties"]['routeId'].strip()
        vehicle["properties"]['routeNumber'] = route_id
        vehicle["properties"]['routeNumberPadded'] = route_id.zfill(3)
        vehicle["properties"]['routeNumber'] = int(route_id) # this could be dicy
    except:
        pass


def make_response_as_dict(vehicles):
    ret_val = {
        "success": True,
        "total": 0,
        "type": "FeatureCollection",
        "features": []
    }
    for i, v in enumerate(vehicles):
        try:
            v = make_vehcile(v, i)
            ret_val['features'].append(v)
            ret_val['total'] += 1
        except Exception as e:
            log.warn(e)
            continue

    return ret_val


def make_response_as_json_str(vehicles, pretty):
    import json
    json_dict = make_response_as_dict(vehicles)
    if pretty:
        ret_val = json.dumps(json_dict, indent=4, sort_keys=True)
    else:
        ret_val = json.dumps(json_dict)
    return ret_val


def make_response(vehicles, pretty=False):
    return make_response_as_json_str(vehicles, pretty)
