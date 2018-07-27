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

    # note: we might get either Vehicle or Position objects here based on how the query happened
    #       so we first have to get both the position and the vehicle objects
    from vehicle_position import VehiclePosition
    if isinstance(v, VehiclePosition):
        position = v
        v = position.vehicle[0]
    else:
        position = v.positions[0]

    ret_val = {
        "properties": {
            "~unique-id~": str(i),
            "lon": -000.111,
            "lat": 00.111,
            "heading": float(position.bearing),

            # old schedule vars for map
            "direction": 111,  # no equal in gtfsdb-rt (is there a need to /q gtfs route_dir for this??)
            "tripNumber": position.trip_id, #todo int utils safe
            "routeNumber": 1,
            "routeNumberPadded": "001",

            "agencyId": position.agency,
            "stopId": position.stop_id,
            "stopSequence": position.stop_seq,
            "routeId": position.route_id,
            "tripId": position.trip_id,
            "blockId": "TODO ... need to look at gtfsdb",

            "status": position.vehicle_fk,
            "vehicleNumber": v.vehicle_id,
            "destination": position.headsign,
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

    _set_coord(ret_val, float(position.lat), float(position.lon))
    _set_time(ret_val, position)
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


def _set_time(vehicle, position):
    ts = float(position.timestamp)
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
