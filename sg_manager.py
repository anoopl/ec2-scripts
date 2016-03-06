import logging
import argparse
import boto3
import botocore
import yaml
import boto.ec2


def read_from_yaml(yml_file):
    """Read yaml and return dictionary
    """
    logging.info("reading yaml file: %s" % yml_file)
    sg_dict = {}
    yaml_stream = open(yml_file, "r")
    security_groups = yaml.load_all(yaml_stream)
    for security_group in security_groups:
        sg_dict = {sg_name: sg_attributes for (sg_name, sg_attributes) in security_group.items()}
        yaml_stream.close()
        logging.debug("sg_dict: %s" % sg_dict)
        return sg_dict


def get_sg_not_defined(sg,sg_dict):
    """Get Security Groups not defined on yaml file
    """
    logging.info("Getting security groups not defined on yaml")
    sg_not_defined = []
    for group in sg:
        if group.group_name not in sg_dict.keys():
            sg_not_defined.append(group.group_name)
            logging.info("security group not defined in yml: {0}".format(sg_not_defined))
    return sg_not_defined


def check_sg_rules(all_sg,sg_not_defined,sg_dict,region,dry_run):
    """Check Security Group Rules and modify
    """
    logging.info("Checking secuiry Group rules")
    client = boto3.client('ec2',region_name=region)
    ec2 = boto3.resource('ec2',region_name=region)
    for sec_group in sg_dict.keys():
        try:
            sec_group_rules = client.describe_security_groups(GroupNames=[sec_group])
            for rule_type in 'ingress-rules', 'egress-rules':
                if rule_type == 'ingress-rules':
                    rules_list = sec_group_rules['SecurityGroups'][0]['IpPermissions']
                else:
                    rules_list = sec_group_rules['SecurityGroups'][0]['IpPermissionsEgress']
                for rule in sg_dict[sec_group][rule_type]:
                    if not isinstance(rule, int):
                        from_port, to_port = rule.split('-')
                    else:
                        from_port = rule
                        to_port = rule
                    if not any(d.get('FromPort') == int(from_port) and d.get('ToPort') == int(to_port) for d in rules_list):
                        protocol = sg_dict[sec_group][rule_type][rule]
                        logging.info("Rule for port: {0} {1} not found in group:{2}".format(from_port,to_port,sec_group))
                        if not dry_run:
                            logging.info("Creating new Rule, port: {0} {1} and protocol: {2}".format(from_port,to_port,protocol))
                            if rule_type == 'ingress-rules':
                                client.authorize_security_group_ingress(GroupName=sec_group,IpProtocol=protocol,
                                                                CidrIp="0.0.0.0/0",FromPort=from_port,ToPort=to_port)
                            elif rule_type == 'egress-rules':
                                group_id = sec_group_rules['SecurityGroups'][0]['GroupId']
                                conn = boto.ec2.connect_to_region(region)
                                conn.authorize_security_group_egress(group_id, 'tcp', from_port=int(from_port), to_port=int(to_port), cidr_ip='0.0.0.0/0')
                                #client.authorize_security_group_egress(GroupId=group_id,IpProtocol='tcp',
                                #CidrIp="0.0.0.0/0",FromPort=int(from_port),ToPort=int(to_port))

                                #client.authorize_security_group_egress(GroupId=group_id,IpProtocol='tcp',
                                                                #CidrIp="0.0.0.0/0",FromPort=from_port,ToPort=to_port)


                    else:
                        logging.info("Matching Rule for port: {0} found in group:{1}".format(rule,sec_group))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
                logging.info("Security group not found: {0}".format(sec_group))
                if not dry_run:
                    logging.info("Creating Security Group: {0}".format(sec_group))
                    client.create_security_group(GroupName=sec_group,Description=sg_dict[sec_group]['description'])
                    continue

            else:
                logging.warning("Unexpected Error: {0}".format(e))


def get_all_security_groups(region):
    """Get all security Groups
    """
    ec2 = boto3.resource('ec2',region_name=region)
    sec_groups = ec2.security_groups.all()
    return sec_groups


def configure_logging(log_level):
    """Logging function
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level)


def parse_arguments():
    parser = argparse.ArgumentParser(description='AWS Security Group Manager')
    parser.add_argument('--version','-V', action='version', version='%(prog)s 1.0')
    parser.add_argument('--log','-l', default='WARN', type=str.upper ,
                        choices=['DEBUG','INFO','WARN','ERROR'],
                        help='Log level')
    parser.add_argument('--region',default='us-east-1',type=str,help='EC2 region to use')
    parser.add_argument('--yaml',default='sg_manager.yml',type=str,help='YAML File with rules')
    parser.add_argument('--dry_run',default=False,action='store_true',help='Dry run for audit')
    args = parser.parse_args()
    return args


def main(args):
    sg_yml_dict = read_from_yaml(args.yaml)
    all_sec_groups = get_all_security_groups(args.region)
    sg_not_defined = get_sg_not_defined(all_sec_groups,sg_yml_dict)
    check_sg_rules(all_sec_groups,sg_not_defined,sg_yml_dict,args.region,args.dry_run)


if __name__ == "__main__":
    PARSED_ARGS = parse_arguments()
    configure_logging(PARSED_ARGS.log)
    main(PARSED_ARGS)
