def process_county(county: str):
    if 'Аобл.' in county:
        county = county.replace('Аобл. ', '')
        county = county + ' автономная область'
    elif 'обл.' in county:
        county = county.replace('обл. ', '')
        county = county + ' область'
    elif 'Респ.' in county:
        county = county.replace('Респ.', 'Республика')
        county = county.replace('  ', ' ')
    elif 'край.' in county:
        county = county.replace('край. ', '')
        county = county + ' край'
    elif 'АО.' in county:
        county = county.replace('АО. ', '')
        county = county + ' автономный округ'
    return county


def process_street(street: str):
    if "ул." in street:
        street = street.replace(' ул.', 'улица')
        street = street.replace("  ", " ")
    elif "пр-кт." in street:
        street = street.replace(' пр-кт. ', '')
        street = street + ' проспект'
    elif "б-р." in street:
        street = street.replace(' б-р.', 'бульвар')
        street = street.replace("  ", " ")
    elif "аллея." in street:
        street = street.replace(' аллея.', 'аллея')
        street = street.replace("  ", " ")
    elif "проезд." in street:
        street = street.replace(' проезд.', 'проезд')
        street = street.replace("  ", " ")
    elif "пер." in street:
        street = street.replace(' пер. ', '')
        street = street + ' переулок'
    elif "ш." in street:
        street = street.replace(' ш. ', '')
        street = street + ' шоссе'
    elif "туп." in street:
        street = street.replace(' туп. ', '')
        street = street + ' тупик'
    elif "пл." in street:
        street = street.replace(' пл. ', '')
        street = street + ' площадь'
    return street


def process_house (house:str):
    if "д." in house:
        house = house.replace(' д. ', '')
        house = house.replace("  ", " ")
    if "литера" in house:
        house = house.replace(' литера ', '')
        house = house.replace("  ", " ")
    if "корпус" in house:
        house = house.replace(' корпус ', 'к')
        house = house.replace("  ", " ")
    if "строение" in house:
        house = house.replace(' строение ', 'с')
        house = house.replace("  ", " ")
    return house


def process_address(address, countyEx):
    if countyEx:
        index, county, city, street, house = address.split(',')
        county = process_county(county)
    else:
        index, city, street, house = address.split(',')
    if "г." in city:
        city = city.replace("г.", "")
        city = city.replace("  ", "")
    street = process_street(street)
    house = process_house(house)
    if countyEx:
        res_address = county + ', ' + city + ', ' + street + ', ' + house
    else:
        res_address = city + ', ' + street + ', ' + house
    return res_address