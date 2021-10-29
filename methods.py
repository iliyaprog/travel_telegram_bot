import collections

def lowprice_hotels(dict_hotels):
    sorted_dict_hotels = collections.OrderedDict()
    list_price = []
    for i_key in dict_hotels.keys():
        try:
            price = dict_hotels[i_key]['price']
            list_price.append(price)
        except:
            pass
    list_price = sorted(list_price)
    for i_value in list_price:
        for j_key in dict_hotels.keys():
            if str(dict_hotels[j_key]['price']) == str(i_value):
                sorted_dict_hotels[j_key] = dict_hotels[j_key]
    return sorted_dict_hotels


def highprice_hotels(dict_hotels):
    sorted_dict_hotels = collections.OrderedDict()
    list_price = []
    for i_key in dict_hotels.keys():
        try:
            price = dict_hotels[i_key]['price']
            list_price.append(price)
        except:
            pass
    list_price = sorted(list_price, reverse=True)
    for i_value in list_price:
        for j_key in dict_hotels.keys():
            if str(dict_hotels[j_key]['price']) == str(i_value):
                sorted_dict_hotels[j_key] = dict_hotels[j_key]
    return sorted_dict_hotels


def bestdeal_hotels(dict_hotels, distance):
    sorted_dict_hotels = collections.OrderedDict()
    list_price = []
    favorit_keys = []
    for i_key in dict_hotels.keys():
        new_distance = ''
        for i_elem in dict_hotels[i_key]['distance']:
            if i_elem.isdigit():
                new_distance += i_elem
            elif i_elem == ',' or i_elem == '.':
                new_distance += '.'
        new_distance = float(new_distance)
        if new_distance <= distance:
            favorit_keys.append(i_key)
            try:
                price = dict_hotels[i_key]['price']
                list_price.append(price)
            except:
                pass
    list_price = sorted(list_price)
    for i_value in list_price:
        for j_key in favorit_keys:
            if str(dict_hotels[j_key]['price']) == str(i_value):
                sorted_dict_hotels[j_key] = dict_hotels[j_key]
    return sorted_dict_hotels

