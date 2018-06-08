


def set_coord(vehicle, lat, lon):
    vehicle["properties"]['lat'] = lat
    vehicle["properties"]['lon'] = lon
    vehicle["geometry"]["coordinates"] = [lon, lat]


def set_time(vehicle, position):
    vehicle["properties"]['minutes'] = 111
    vehicle["properties"]['seconds'] = 111
    vehicle["properties"]['reportDate'] = "XXX"


def make_vehcile(v, i):
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
            "blockId": position.vehicle_fk,

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
        break

    return ret_val