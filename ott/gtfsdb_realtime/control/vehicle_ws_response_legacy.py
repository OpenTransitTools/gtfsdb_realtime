
vehicle_tmpl = {
    "properties": {
        "lon": -000.111,
        "lat": 00.111,
        "heading": "111",
        "direction": 1,

        "routeNumber": 1,
        "routeNumberPadded": "01",
        "tripNumber": 111,
        "block": 111,
        "vehicleNumber": "111",
        "destination": "111 Bogus Route Name to Bogus Place via City Center",

        "minutes": 1,
        "seconds": 11,
        "reportDate": "11.11.2111 11:11 pm"
    },
    "type": "Feature", "geometry": {
        "type": "Point",
        "coordinates": [-0.111, 0.111]
    }
}


def make_vehcile(v):
    return vehicle_tmpl


def make_response(vehicles):
    ret_val = {
        "success": true,
        "total": 0,
        "type": "FeatureCollection",
        "features": []
    }
    for v in vehicles:
        v = make_vehcile(v)
        ret_val['features'].push(v)
        ret_val['total'] += 1

    return ret_val
