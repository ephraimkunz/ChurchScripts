
from lcr import API as LCR
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import gmplot

import urllib
import json
import datetime
import os
from enum import Enum


class OptimizationCriteria(Enum):
    DURATION = "duration"
    DISTANCE = "distance"


def set_env_variables():
    with open('cred') as f:
        for line in f:
            line = line.strip('\n')
            pieces = line.split('=')
            if len(pieces) == 2:
                os.environ[pieces[0]] = pieces[1]


def fetch_member_addresses():
    user = os.environ['LDS_USER']
    password = os.environ['LDS_PASSWORD']
    unit_number = os.environ['LDS_UNIT_NUMBER']

    lcr = LCR(user, password, unit_number)

    member_list = lcr.members_alt()

    me_address = ""
    addresses = set()  # For deduplication
    for member in member_list:
        if member['nameGivenPreferredLocal'] == 'Ephraim':
            # It's me
            me_address = ', '.join(member['address']['addressLines'])

        joined_address = ', '.join(member['address']['addressLines'])

        if 'California' not in joined_address:
            # Some address in Chicago?
            continue

        # Combine all of Stanford into 1 address. This greatly simplifies unstructured apartment locations (by removing them).
        if 'Stanford, California' in joined_address:
            addresses.add("Stanford, California 94305")
        else:
            addresses.add(joined_address)

    return (me_address, list(addresses))


def build_cost_matrix(response, optimization_criteria):
    cost_matrix = []
    for row in response['rows']:
        key = optimization_criteria.value
        row_list = [row['elements'][j][key]['value']
                    for j in range(len(row['elements']))]
        cost_matrix.append(row_list)
    return cost_matrix


def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        url_encoded_addresses = [urllib.parse.quote(
            address) for address in addresses]
        address_str = '|'.join(url_encoded_addresses)
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
        dest_address_str + '&key=' + API_key
    jsonResult = urllib.request.urlopen(request).read()
    response = json.loads(jsonResult)
    return response


def create_cost_matrix(addresses, optimization_criteria):
    API_key = os.environ['GOOGLE_API_KEY']
    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses)
    # Maximum number of rows that can be computed per request.
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r.
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    cost_matrix = []
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        cost_matrix += build_cost_matrix(response, optimization_criteria)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        cost_matrix += build_cost_matrix(response, optimization_criteria)
    return cost_matrix


def create_data_model(cost_matrix, me_address):
    """Stores the data for the problem."""
    data = {}
    data['cost_matrix'] = cost_matrix
    data['num_vehicles'] = 1
    data['depot'] = address_list.index(me_address)
    return data


def miles_from_meters(meters):
    return meters / 1609.344


def time_from_seconds(seconds):
    return str(datetime.timedelta(seconds=seconds))


def geocode_address(address):
    # Returns lat, long tuple
    request = 'https://maps.googleapis.com/maps/api/geocode/json?'
    encoded_address = urllib.parse.quote(address)
    request = request + 'address=' + encoded_address + \
        '&key=' + os.environ['GOOGLE_API_KEY']
    jsonResult = urllib.request.urlopen(request).read()
    response = json.loads(jsonResult)
    location = response['results'][0]["geometry"]["location"]
    return (location["lat"], location["lng"])


def output_solution(manager, routing, assignment, optimization_criteria):
    """Prints assignment on console."""
    if optimization_criteria == OptimizationCriteria.DURATION:
        print('Objective: {}'.format(
            time_from_seconds(assignment.ObjectiveValue())))
    else:
        print('Objective: {} miles'.format(
            miles_from_meters(assignment.ObjectiveValue())))

    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    currentLat = 0
    currentLon = 0
    lats = []
    lons = []

    while not routing.IsEnd(index):
        routed_address = address_list[manager.IndexToNode(index)]
        currentLat, currentLon = geocode_address(routed_address)
        lats.append(currentLat)
        lons.append(currentLon)
        plan_output += ' {} ->'.format(routed_address)
        index = assignment.Value(routing.NextVar(index))

    routed_address = address_list[manager.IndexToNode(index)]
    currentLat, currentLon = geocode_address(routed_address)
    lats.append(currentLat)
    lons.append(currentLon)
    plan_output += ' {}\n'.format(routed_address)
    print(plan_output)

    gmap = gmplot.GoogleMapPlotter(lats[0],
                                   lons[0], 13, apikey=os.environ['GOOGLE_API_KEY'])

    # scatter method of map object
    # scatter points on the google map
    gmap.scatter(lats, lons, '# FF0000',
                 size=40, marker=False)

    # Plot method Draw a line in
    # between given coordinates
    gmap.plot(lats, lons,
              'cornflowerblue', edge_width=2.5)

    gmap.draw("map.html")


if __name__ == '__main__':
    set_env_variables()

    optimization_criteria = OptimizationCriteria.DURATION

    # 1. Fetch and format origin address and destination addresses.
    print("Fetching and formatting member addresses")
    me_address, address_list = fetch_member_addresses()

    # 2. Fetch cost matrix using Google Distance Matrix api.
    print("Creating cost matrix")
    cost_matrix = create_cost_matrix(address_list, optimization_criteria)

    # 3. Solve TSP using Google OR tools.
    print("Running solver")
    data_model = create_data_model(cost_matrix, me_address)

    def transit_callback(from_index, to_index):
        """Returns the cost between the two nodes."""
        # Convert from routing variable Index to cost matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data_model['cost_matrix'][from_node][to_node]

    manager = pywrapcp.RoutingIndexManager(
        len(data_model['cost_matrix']), data_model['num_vehicles'], data_model['depot'])
    routing = pywrapcp.RoutingModel(manager)
    transit_callback_index = routing.RegisterTransitCallback(transit_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)  # pylint: disable=no-member
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH) # pylint: disable=no-member
    search_parameters.time_limit.seconds = 300
    search_parameters.log_search = True

    assignment = routing.SolveWithParameters(search_parameters)

    # 4. Output results and annotated map.
    print("Generating output map")
    if assignment:
        output_solution(manager, routing, assignment, optimization_criteria)
