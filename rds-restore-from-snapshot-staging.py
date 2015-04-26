import time
import boto.rds2, boto.rds

#TO DO
#def get_latest_snaphsot_name(conn):
#	latest_db_snapshot = conn.describe_db_snapshots(db_instance_identifier=SOURCE_DB_INSTANCE_IDENTIFIER)['DescribeDBSnapshotsResponse']
#	['DescribeDBSnapshotsResult']['DBSnapshots'][0]['DBSnapshotIdentifier']
#	return latest_db_snapshot
#def create_new_dbinstance(conn, snapshot):
#	db_new = conn.restore_db_instance_from_db_snapshot(TARGET_DB_INSTANCE_IDENTIFIER, latest_db_snapshot, db_instance_class=DB_INSTANCE_TYPE, 
#	db_subnet_group_name=DB_SUBNET_GROUP_NAME, publicly_accessible='true', option_group_name=DB_OPTION_GROUP_NAME)
#	if db_new:
#		rerun "Success"
#def update_dbinstance(conn, TARGET_DB_INSTANCE_IDENTIFIER):
#	dbinstances =  conn.get_all_dbinstances(instance_id=TARGET_DB_INSTANCE_IDENTIFIER)[0]
#	while dbinstances.status != 'available':
#		print '===> db instance is %s' % dbinstances.status
#		time.sleep(10)
#		dbinstances.update()
	#Modify the security group of instance
#	update_sg = rds2_conn.modify_db_instance(TARGET_DB_INSTANCE_IDENTIFIER, vpc_security_group_ids=DB_VPC_SECURITY_GROUP_ID, backup_retention_period=0)

def main():
	AWS_ACCESS_KEY_ID = ''
	AWS_SECRET_ACCESS_KEY = ''
	AWS_REGION = ''
	SOURCE_DB_INSTANCE_IDENTIFIER = ''
	TARGET_DB_INSTANCE_IDENTIFIER = ''
	DB_INSTANCE_TYPE = ''
	DB_OPTION_GROUP_NAME = ''
	DB_SUBNET_GROUP_NAME = ''
	DB_VPC_SECURITY_GROUP_ID = ''
	rds_conn = boto.rds.connect_to_region(AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	rds2_conn = boto.rds2.connect_to_region(AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	#Get the Latest Snapshot identifier
	latest_db_snapshot = rds2_conn.describe_db_snapshots(db_instance_identifier=SOURCE_DB_INSTANCE_IDENTIFIER)['DescribeDBSnapshotsResponse']['DescribeDBSnapshotsResult']['DBSnapshots'][0]['DBSnapshotIdentifier']
	#Create new DB instance from the snaphsot
	dbnew = rds2_conn.restore_db_instance_from_db_snapshot(TARGET_DB_INSTANCE_IDENTIFIER, latest_db_snapshot, db_instance_class=DB_INSTANCE_TYPE, 
	db_subnet_group_name=DB_SUBNET_GROUP_NAME, publicly_accessible='true', option_group_name=DB_OPTION_GROUP_NAME)
	#Wait till instance is in 'availbale' state
	dbinstances = rds_conn.get_all_dbinstances(instance_id=TARGET_DB_INSTANCE_IDENTIFIER)[0]
	while dbinstances.status != 'available':
		print '===> db instance is %s' % dbinstances.status
		time.sleep(10)
		dbinstances.update()
	#Modify the security group of instance
	update_sg = rds2_conn.modify_db_instance(TARGET_DB_INSTANCE_IDENTIFIER, vpc_security_group_ids=DB_VPC_SECURITY_GROUP_ID, backup_retention_period=0)

if __name__ == "__main__":
	main()
