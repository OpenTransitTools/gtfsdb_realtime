

def make_vehcile(v, i):
    ret_val = {
        "properties": {
            "id": 111,
            "lon": -000.111,
            "lat": 00.111,
            "heading": "111",
            "direction": 1,
            "routeNumber": 1,
            "routeNumberPadded": "001",
            "tripNumber": 111,
            "block": 111,
            "vehicleNumber": "111",
            "destination": "111 Bogus Route Name to Bogus Place via City Center",
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

    ret_val['id'] = i
    #ret_val['tripNumber'] = v.get('trip')

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

    return ret_val
