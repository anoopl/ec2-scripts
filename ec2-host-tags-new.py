#!/usr/bin/python
import time
import boto.ec2
import boto.exception

class EC2_tags_pubdns:
	def __init__(self, AWS_REGION):
		self.AWS_REGION = AWS_REGION
		#self.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
		#self.AWS_SECRET_ACCESS_KEY =  AWS_SECRET_ACCESS_KEY
		self.ec2_conn = self.create_ec2_conn()
		#self.ec2_conn = boto.ec2.connect_to_region(self.AWS_REGION)

	def create_ec2_conn(self):
		print "Creating EC2 Connection"
		#print self.AWS_REGION
		self.ec2_conn = boto.ec2.connect_to_region(self.AWS_REGION)
		#print self.ec2_conn 
		return self.ec2_conn

	def get_tags_pubdns(self):
		print "Getting info:"
		instances = []
		reservations = self.ec2_conn.get_all_instances()
		for reservation in reservations:
			for instance in reservation.instances:
				instance_name = instance.tags.get('Name')
			#if instance.public_dns_name:
				pair = (instance_name, instance.ip_address)
				instances.append(pair)
		for instance in sorted(instances):
			print "%s\t%s" % (instance[0], instance[1])

def main():
	AWS_REGION = 'us-east-1'
	tag_dns_display = EC2_tags_pubdns('us-east-1')
	#tag_dns_display.create_ec2_conn()
	tag_dns_display.get_tags_pubdns()



if __name__ == "__main__":
	main()
