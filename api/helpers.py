def units_mapper(meas_type):
    """
    Maps units to each kind of meter
    """
    # Add more units here as more unique 'type's in the database are added
    units = {"Active Energy Delivered": "kWh",
             "Active Power": "kW"}
    try:
        return (units[meas_type])
    except KeyError:
        return ""

def sensortype_mapper(source):
    """
    Maps the unique 3-letter code to different types of meters. Should be migrated to a database in a future version.
    """
    stype = re.search('B\d\d\d(.*)',source).group(1)[:-1] # removing the Bxxx part, and the trailing \r that seems to be in the database
    stype = ''.join(filter(str.isalpha, stype)) # keep only the characters, drop all numbers - this gives a unique 3 letter code (for now) for all different meters
    sensortypes = {
        "EMS": "Electrical mains transformer (4160V - 480V)",
        "EMH": "Electrical mains meter, high voltage (480V)",
        "EML": "Electrical mains meter, low voltage (208V)",
        "EUH": "Electrical sub-meter, high voltage (480V)",
        "EUL": "Electrical sub-meter, low voltage (208V)"
    }
    try:
        return (sensortypes[stype])
    except KeyError:
        return "unknown"


def res_to_json(row):
    """
    Encode the result of a power-related SQL query to JSON
    """
    output = {
        "source_name": row[3][:-1],    # remove the trailing \r that seems to be in the database
        "source_type": sensortype_mapper(row[3]),
        "timestamp": row[0],           # get data in UNIX format, with GMT times, client can use JavaScript to convert timezones.
        "value_read": str(row[2]),
        "units": units_mapper(row[1])
    }
    return(output)