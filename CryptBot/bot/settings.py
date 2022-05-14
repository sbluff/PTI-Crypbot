def getSQLParameters(mode="local"):
    if mode == "local":
        parameters = {
            "server": "localhost",
            "port": 3306,
            "db_name": "trades",
            "username": "root",
            "password": "root"
        }
    elif mode == "production":
        parameters = {

        }   
    return parameters     