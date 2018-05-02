

def get_alerts(route_id):
    from model.alert_entity import AlertEntity
    session = AlertEntity
    AlertEntity.query_via_route_id()

def main():
    get_alerts("6")


if __name__ == '__main__':
    main()