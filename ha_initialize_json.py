#!/usr/bin/python

"""
#*===================================================================
#*
#* Licensed Materials - Property of IBM
#* IBM Cloud Network
#* Copyright IBM Corporation 2020. All Rights Reserved.
#*
#*===================================================================
"""


import json
import datetime
import logging, logging.handlers
import click


class InitializeJson(object):
    """
    This is a class to initialize the json file for High Availability Custom route update

    This can be invoked as a CLI as well as by passing arguments in constructor
    """
    APIKEY = "apikey"
    VPC_ID = "vpc_id"
    VPC_URL = "vpc_url"
    ROUTING_TABLE = "routing_table_name"
    ROUTING_TABLE_ROUTE_NAME = "routing_table_route_name"
    DESTINATION_IPV4_CIDR_BLOCK = "destination_ipv4_cidr_block"
    ZONE = "zone"
    HA_PAIR = "ha_pair"
    MGMT_IP = "mgmt_ip"
    EXT_IP = "ext_ip"
    CONFIGFILE = "config.json"
    HA_TABLE_NAME = "ha-routing-table"
    HA_TABLE_NAME_ROUTE = "ha-routing-table-route"

    def __init__(self, logger, **kwargs):
        """
        The constructor for this class.

        Pass the user input arguments to constructor
        :param logger: Logger where the initializer prints the output logs
        :param kwargs: Command options dictionary
        """
        self.apikey = kwargs.get('apikey', None)
        self.vpcid = kwargs.get('vpcid', None)
        self.vpcurl = kwargs.get(
            'vpcurl', 'https://us-south.iaas.cloud.ibm.com')
        self.tablename = kwargs.get('tablename', 'ha-routing-table')
        self.routename = kwargs.get('routename', 'ha-routing-table-route')
        self.cidr = kwargs.get('cidr', None)
        self.zone = kwargs.get('zone', "us-south-1")
        self.mgmtip1 = kwargs.get('mgmtip1', None)
        self.extip1 = kwargs.get('extip1', None)
        self.mgmtip2 = kwargs.get('mgmtip2', None)
        self.extip2 = kwargs.get('extip2', None)
        self.logger = logger

    def validate_params(self):
        """
        The method to process the user input arguments, validate the arguments and fail

        :return: void
        """
        # check if the code is called with apikey, vpcid, url, etc
        if self.vpcurl is None:
            self.vpcurl = 'https://us-south.iaas.cloud.ibm.com'
        if self.tablename is None:
            self.tablename = self.HA_TABLE_NAME
        if self.routename is None:
            self.routename = self.HA_TABLE_NAME_ROUTE
        if self.apikey is None or self.vpcid is None or self.cidr is None or \
            self.mgmtip1 is None or self.extip1 is None or self.mgmtip2 is None or self.extip2 is None:
            excmsg = 'VPC id, apikey, destination cidr, mgmt ip1, external ip1, mgmt ip2, external ip2 of HA Pair is none. '
            excmsg = excmsg + 'Either apikey/vpcid/mgmt_ip1/ext_ip1/mgmt_ip2/ext_ip2 is empty. Pass the apikey, vpcid, ' \
                'mgmt_ip1, ext_ip1, mgmt_ip2, ext_ip2 as command line arguments or specify config file with all these argument values. '
            excmsg = excmsg + ' Run the command: "python3 ha_initialize_json.py --help" for more details.'    
            self.logger.info(excmsg)
            excmsg = "Exception occurred while validating arguments"
            raise EnvironmentError(excmsg)

    def update_json_file(self):
        """
        The method to process the user input arguments, validate the arguments and fail

        :return: void
        """
        # check if the code is called with apikey, vpcid, url, etc
        self.validate_params()
        try:        
            with open(self.CONFIGFILE) as config_json:
                config = json.load(config_json)
            for item in config:
                if item == self.APIKEY:
                    config[self.APIKEY] = self.apikey
                if item == self.VPC_ID:
                    config[self.VPC_ID] = self.vpcid
                if item == self.VPC_URL:
                    config[self.VPC_URL] = self.vpcurl
                if item == self.ROUTING_TABLE:
                    config[self.ROUTING_TABLE] = self.tablename
                if item == self.ROUTING_TABLE_ROUTE_NAME:
                    config[self.ROUTING_TABLE_ROUTE_NAME] = self.routename
                if item == self.DESTINATION_IPV4_CIDR_BLOCK:
                    config[self.DESTINATION_IPV4_CIDR_BLOCK] = self.cidr
                if item == self.ZONE:
                    config[self.ZONE] = self.zone
                if item == self.HA_PAIR:
                    config[self.HA_PAIR][0][self.MGMT_IP] = self.mgmtip1
                    config[self.HA_PAIR][0][self.EXT_IP] = self.extip1
                    config[self.HA_PAIR][1][self.MGMT_IP] = self.mgmtip2
                    config[self.HA_PAIR][1][self.EXT_IP] = self.extip2
            json_data = json.dumps(config, indent=4)
            with open(self.CONFIGFILE, "w") as config_json:
                config_json.write(json_data)
        except:
            self.logger.info("Exception occurred while updating config.json")

@click.command()
@click.option('--apikey',
              '-k',
              help='The apikey of admin user to update custom route in HA Pair',
              type=click.STRING)
@click.option('--vpcid', '-v', help='The vpcid of HA Pair', type=click.STRING)
@click.option('--vpcurl', '-u',
              help="The vpc service url region", type=click.STRING)
@click.option('--tablename', '-t',
              help='The vpc routing table name', type=click.STRING)
@click.option('--routename', '-r',
              help='The vpc routing table route name', type=click.STRING)
@click.option('--cidr', '-c',
              help='The destination ipv4 cidr block', type=click.STRING)
@click.option("--zone", "-z", help="The vpc zone", type=click.STRING)
@click.option("--mgmtip1",
              "-mip1",
              help="The management interface ip address of HA pair 1",
              type=click.STRING)
@click.option("--extip1",
              "-eip1",
              help="The external interface ip address of HA pair 1",
              type=click.STRING)
@click.option("--mgmtip2",
              "-mip2",
              help="The management interface ip address of HA pair 2",
              type=click.STRING)
@click.option("--extip2",
              "-eip2",
              help="The external interface ip address of HA pair 2",
              type=click.STRING)
def main(**kwargs):
    """
    The method that is invoked, when run with CLI arguments

    :param kwargs:
    :return: void
    """
    logfile = 'initialize_json.log'
    logging.basicConfig(
        filename='initialize_json.log',
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO)
    loghandler = logging.handlers.TimedRotatingFileHandler(logfile,when="midnight")
    logger = logging.getLogger(__name__)
    logger.addHandler(loghandler)
    
    initialize = InitializeJson(logger, **kwargs)
    initialize.update_json_file()
    

if __name__ == '__main__':
    main()
