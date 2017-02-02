#!/usr/bin/python
import requests
import json
import yaml
import time
import argparse

# TODO!
#

def setupArgs():
    parser = argparse.ArgumentParser(description='Split template params into per-region config files.')
    parser.add_argument('--opsc-ip', type=str, help='Public ip of OpsCenter instance.')
    parser.add_argument('--s3bucket', type=str, help='S3 bucket for taskcat deploy')
    parser.add_argument('--pubkey', type=str, help='Public key corresponding to private key in LCM')
    parser.add_argument('--clustername', type=str, help='Name of cluster.')
    parser.add_argument('--datacenters',type=str, help="List of dc names")
    parser.add_argument('--regions',type=str, help="List of AWS regions")
    parser.add_argument('--keys',type=str, help="List of key pairs to use")
    parser.add_argument('--instances',type=str, help="List of instances")
    parser.add_argument('--dcsizes',type=str, help="List of dc sizes")
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Verbose flag, right now a NO-OP.' )
    return parser

def checkArgs(lists):
    for l in lists:
        if (l==None):
            print "Error: argument missing"
            exit(1)
    length = len(lists[0])

    for l in lists:
        if (len(l) != length):
            print "Error: list arguments must be the same length"
            exit(1)

def writeYAML(args):
    conf = {'global': {
              'project': 'dse',
              'owner': 'foo@foo.com',
              'notification': True,
              'reporting': True,
              'report_email-to-owner': True,
              'report_publish-to-s3': True,
              'report_s3bucket': args.s3bucket,
              's3bucket': args.s3bucket,
              'regions': args.regions
            },
            'tests': {}
           }
    count = 0

    for r in args.regions:
        count += 1
        name = 'datacenter-'+str(count)
        datacenter = {'parameter_input':name+'.json',
                      'regions': [r],
                      'template_file': 'cfn-datacenter-lcm.json'
                     }
        conf['tests'][name] = datacenter

    with open('config.yaml', 'w') as outfile:
      yaml.dump(conf, outfile, default_flow_style=False)

def writeConfig(params, filename):
    conf = []
    for key in params:
        conf.append({"ParameterKey": key, "ParameterValue": params[key]})
    with open(filename, 'w') as outfile:
      json.dump(conf, outfile, sort_keys=True, indent=4)

def main():
    parser = setupArgs()
    args = parser.parse_args()
    args.datacenters = args.datacenters.split(",")
    args.regions = args.regions.split(",")
    args.keys = args.keys.split(",")
    args.instances = args.instances.split(",")
    args.dcsizes = args.dcsizes.split(",")
    checkArgs([args.datacenters,args.keys,args.regions,args.instances,args.dcsizes])

    writeYAML(args)
    count = 0
    for i in range(len(args.regions)):
        count += 1
        conf = {}
        conf['OpsCenterPubIP'] = args.opsc_ip
        conf['ClusterName'] = args.clustername
        conf['PublicKey'] = args.pubkey
        conf['KeyName'] = args.keys[i]
        conf['InstanceType'] = args.instances[i]
        conf['DataCenterName'] = args.datacenters[i]
        conf['DataCenterSize'] = args.dcsizes[i]
        filename = "datacenter-"+str(count)+".json"
        writeConfig(conf,filename)


# ----------------------------
if __name__ == "__main__":
    main()