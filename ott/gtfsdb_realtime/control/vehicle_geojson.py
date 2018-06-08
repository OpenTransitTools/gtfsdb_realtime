
def set_coord(vehicle, lat, lon):
    vehicle["properties"]['lat'] = lat
    vehicle["properties"]['lon'] = lon
    vehicle["geometry"]["coordinates"] = [lon, lat]


def make_vehcile(v, i):
    position = v.positions[0]

    ret_val = {
        "properties": {
            "~unique-id~": str(i),
            "lon": -000.111,
            "lat": 00.111,
            "heading": float(position.bearing),
            "direction": 1,

            # old schedule vars for map
            "tripNumber": position.trip_id, #todo int utils safe
            "routeNumber": 1,
            "routeNumberPadded": "001", #todo int utils safe padding

            "agencyId": position.agency,
            "stopId": position.stop_id,
            "routeId": position.route_id,
            "tripId": position.trip_id,
            "blockId": position.vehicle_fk,

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
