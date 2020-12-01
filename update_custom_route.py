from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from flask import Flask, redirect, url_for, request, render_template, make_response, session, abort, flash



app = Flask(__name__)

apikey = 'xyz'
authenticator = IAMAuthenticator(apikey)
service = VpcV1(authenticator=authenticator)
service.set_service_url("https://us-south.iaas.cloud.ibm.com")
version = "2020-04-10"
zone = "us-south-1"
subnet_name_1 = "failover-subnet1"
ha_pair = ["10.xxx.xx.xxx", "10.xxx.xx.xxx"]
next_hop_vsi = "10.xxx.xx.xxx"
update_next_hop_vsi = "10.xxx.xx.xxx"
# vpc-f5-subnet5
source_subnet_id = "0717-xx-xxx-xxxxf1f7"
source_ipv4_cidr_block = "10.xxx.xx.xxx"
# vpc-f5-subnet4

vpc_name = "vpc-f5-test"


service = VpcV1(version, authenticator=authenticator)

#  Listing VPCs

def get_vpc_id():
    print("List VPCs")
    try:
        vpcs = service.list_vpcs().get_result()['vpcs']
    except ApiException as e:
      print("List VPC failed with status code " + str(e.code) + ": " + e.message)
    for vpc in vpcs:
        print(vpc['id'], "\t",  vpc['name'])
        if vpc['name'] == vpc_name:
            id = vpc['id']
            print("vpc found, id: %s, name: %s " % (vpc['id'], vpc['name']))
            return id
    return None        
            
def get_vpc_routing_table_id(vpc_id, table_name):
    list_tables = service.list_vpc_routing_tables(vpc_id).get_result()['routing_tables']
    table_found = False
    for table in list_tables:
        print(table['id'], "\t",  table['name'])
        if table['name'] == table_name:
            table_found = True
            table_id = table['id']
            print("vpc routing table found, id: %s, name: %s: " % (table_id, table_name))
            return table_id
    if not table_found:
        create_vpc_routing_table_response = service.create_vpc_routing_table(vpc_id, name=table_name, routes=None)
        routing_table = create_vpc_routing_table_response.get_result()    
        print(routing_table['id'], "\t",  routing_table['name'])
        table_id = routing_table['id']
    return table_id       
    
    
def attach(source_subnet_id, source_table_id):
    routing_table_identity_model = {'id': source_table_id,}
    service.replace_subnet_routing_table(id=source_subnet_id, routing_table_identity= routing_table_identity_model)              
 
        
def get_vpc_routing_table_route_id(vpc_id, table_id, route_name, next_hop_vsi):   
    list_routes=service.list_vpc_routing_table_routes(vpc_id= vpc_id, routing_table_id=table_id)
    routes = list_routes.get_result()['routes']
    for route in routes:
        print("route ", route)
        if route['next_hop']['address'] == next_hop_vsi: 
            print("vpc routing table routes found, id: %s, name: %s: " % (route['id'], route['name']))
            return route['id']
    return None
    
def create_routing_table_route_id(vpc_id, table_id, route_name, next_hop_vsi):
    zone_identity_model = {'name': zone}
    route_next_hop_prototype_model = {'address': next_hop_vsi}
    create_vpc_routing_table_route_response = service.create_vpc_routing_table_route(vpc_id=vpc_id, routing_table_id=table_id, destination=destination_ipv4_cidr_block, zone=zone_identity_model, action='deliver', next_hop=route_next_hop_prototype_model, name=route_name)
    route = create_vpc_routing_table_route_response.get_result()
    return route['id']     
        
def update_next_hop_routing_table_route_id(vpc_id, table_id, route_id, update_next_hop_vsi):   
    vpc_routing_table_route_response = service.get_vpc_routing_table_route(vpc_id=vpc_id, routing_table_id=table_id, id=route_id) 
    route = vpc_routing_table_route_response.get_result()  
    print("Inside update ", route)
    print("vpc routing table route, id: %s, name: %s, zone: %s, next_hop:%s, destination:%s " % (route['id'], route['name'], route['zone']['name'], route['next_hop']['address'], route['destination']))
    zone_identity_model = {'name': route['zone']['name']}
    route_next_hop_prototype_model = {'address': update_next_hop_vsi}
    # delete old route
    service.delete_vpc_routing_table_route(vpc_id=vpc_id, routing_table_id=table_id, id=route_id)
    # create new route
    create_vpc_routing_table_route_response = service.create_vpc_routing_table_route(vpc_id=vpc_id, routing_table_id=table_id, destination=route['destination'], zone=zone_identity_model, action='deliver', next_hop=route_next_hop_prototype_model, name=route['name'])
    route = create_vpc_routing_table_route_response.get_result()
    return route['id']          
            
# update custom route 
@app.route('/')
def result():
    try:
        print("request received from " + request.remote_addr)
        remote_addr = request.remote_addr
        my_ha_pair = ha_pair
        my_ha_pair.remove(remote_addr)
        update_next_hop_vsi = remote_addr
        next_hop_vsi = my_ha_pair[0]
        vpc_id = get_vpc_id()
        source_table_id = get_vpc_routing_table_id(vpc_id, "source-cr-routing-table")
        attach(source_subnet_id, source_table_id)
        # find all routes of HA1
        route_id = get_vpc_routing_table_route_id(vpc_id, source_table_id, "source-destination-route", next_hop_vsi)
        if route_id is None:
            print('routing table route id is None')
            create_routing_table_route_id(vpc_id, source_table_id, "source-destination-route", next_hop_vsi)
            print('created routing table route')
        else:    
            # delete all routes of next hop HA1
            # create new routes of HA2
            update_next_hop_routing_table_route_id(vpc_id, source_table_id, route_id, update_next_hop_vsi)
            print('updated routing table route')
    except ApiException as e:
      print("Update custom route failed with status code " + str(e.code) + ": " + e.message)
    return "Updated Custom Route"    
    

if __name__ == '__main__':
   app.run()
