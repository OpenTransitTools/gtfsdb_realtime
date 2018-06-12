"""
TODO: in the future, we might want to show vehicles positions both from scheduled (GTFS) and real-time (GTFS-RT) datasets ...
      in that tobe (todo) world, we should define a single 'vehicle' service with Swagger, autogen the DAOs in OTT's api
      section, and then use both gtfsdb and gtfsdb_realtime to populate 2 varities of object / service
"""
import datetime

def set_coord(vehicle, lat, lon):
    vehicle["properties"]['lat'] = lat
    vehicle["properties"]['lon'] = lon
    vehicle["geometry"]["coordinates"] = [lon, lat]


def set_time(vehicle, position):
    ts = float(position.timestamp)
    t = datetime.datetime.fromtimestamp(ts)
    pretty_date_time = t.strftime('%x %I:%M %p').replace(" 0", " ")

    diff = datetime.datetime.now() - t
    min_sec_diff = divmod(diff.days * 86400 + diff.seconds, 60)

    vehicle["properties"]['minutes'] = min_sec_diff[0]
    vehicle["properties"]['seconds'] = min_sec_diff[1]
    vehicle["properties"]['reportDate'] = str(pretty_date_time)


def make_vehcile(v, i):
    """
    :return:
    """
    position = v.positions[0]

    ret_val = {
        "properties": {
            "~unique-id~": str(i),
            "lon": -000.111,
            "lat": 00.111,
            "heading": float(position.bearing),

            # old schedule vars for map
            "direction": 111, # no equal in gtfsdb-rt (is there a need to /q gtfs route_dir for this??)
            "tripNumber": position.trip_id, #todo int utils safe
            "routeNumber": 1,
            "routeNumberPadded": "001", #todo int utils safe padding

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

    set_coord(ret_val, float(position.lat), float(position.lon))
    set_time(ret_val, position)

    return ret_val



def make_response(vehicles):
    ret_val = {
        "success": True,
        "total": 0,
        "type": "FeatureCollection",
        "features": []
    }
    for i, v in enumerate(vehicles):
        v = make_vehcile(v, i)
        ret_val['features'].append(v)
        ret_val['total'] += 1
        #break

    return ret_val
