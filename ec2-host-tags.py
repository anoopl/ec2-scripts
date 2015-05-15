#!/usr/bin/python
import time
import boto.ec2
import boto.exception

def main():
	AWS_REGION = 'us-east-1'
	ec2_conn =  boto.ec2.connect_to_region(AWS_REGION)
	instances = []
	reservations = ec2_conn.get_all_instances()
	for reservation in reservations:
		for instance in reservation.instances:
			instance_name = instance.tags.get('Name')
			#if instance.public_dns_name:
			pair = (instance_name, instance.public_dns_name)
			instances.append(pair)
	for instance in sorted(instances):
		print "%s\t%s" % (instance[0], instance[1])
if __name__ == "__main__":
	main()
