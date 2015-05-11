 #!/usr/bin/python
import time
import boto.rds2
import boto.exception

def main():
	AWS_REGION = ''
	SOURCE_DB_INSTANCE_IDENTIFIER = ''
	TARGET_DB_INSTANCE_IDENTIFIER = ''
	DB_INSTANCE_TYPE = 'db.t2.medium'
	DB_OPTION_GROUP_NAME = ''
	DB_SUBNET_GROUP_NAME = ''
	DB_VPC_SECURITY_GROUP_ID = ''
	BACKUP_RETENTION=0
	rds2_conn = boto.rds2.connect_to_region(AWS_REGION)
	latest_db_snapshot = rds2_conn.describe_db_snapshots(db_instance_identifier=SOURCE_DB_INSTANCE_IDENTIFIER)['DescribeDBSnapshotsResponse']['DescribeDBSnapshotsResult']['DBSnapshots'][-1]['DBSnapshotIdentifier']
	print 'DB Snapshot name %s' % latest_db_snapshot
	try:
		print 'Deleting DB Instance %s' % TARGET_DB_INSTANCE_IDENTIFIER
		dbdel = rds2_conn.delete_db_instance(TARGET_DB_INSTANCE_IDENTIFIER, skip_final_snapshot=True)
		dbi_status = rds2_conn.describe_db_instances(db_instance_identifier=TARGET_DB_INSTANCE_IDENTIFIER)['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['DBInstanceStatus']
		print "status=" + dbi_status
		while dbi_status == 'deleting':
			print '===> db instance is %s' % dbi_status
			time.sleep(10)
			dbi_status = rds2_conn.describe_db_instances(db_instance_identifier=TARGET_DB_INSTANCE_IDENTIFIER)['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['DBInstanceStatus']
	except:
		print 'Creating DB Instance %s' % TARGET_DB_INSTANCE_IDENTIFIER
		time.sleep(10)
		dbnew = rds2_conn.restore_db_instance_from_db_snapshot(TARGET_DB_INSTANCE_IDENTIFIER, latest_db_snapshot, db_instance_class=DB_INSTANCE_TYPE, 
		db_subnet_group_name=DB_SUBNET_GROUP_NAME, publicly_accessible='true', option_group_name=DB_OPTION_GROUP_NAME)
		dbi_status = rds2_conn.describe_db_instances(db_instance_identifier=TARGET_DB_INSTANCE_IDENTIFIER)['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['DBInstanceStatus']
		while dbi_status != 'available':
			print '===> db instance is %s' % dbi_status
			time.sleep(10)
			dbi_status = rds2_conn.describe_db_instances(db_instance_identifier=TARGET_DB_INSTANCE_IDENTIFIER)['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['DBInstanceStatus']
		print "DB instance is %s" % dbi_status
		print "Modifying Instance Security Group"
		update_sg = rds2_conn.modify_db_instance(TARGET_DB_INSTANCE_IDENTIFIER, vpc_security_group_ids=DB_VPC_SECURITY_GROUP_ID, backup_retention_period=0)
		while dbi_status != 'available':
			print '===> db instance is %s' % dbi_status
			time.sleep(10)
			dbi_status = rds2_conn.describe_db_instances(db_instance_identifier=TARGET_DB_INSTANCE_IDENTIFIER)['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['DBInstanceStatus']
		print "Updated Securiy group"

if __name__ == "__main__":
	main()
