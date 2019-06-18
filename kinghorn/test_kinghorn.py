import boto3
import kinghorn

ec2_client = boto3.client(
	service_name="ec2", 
	region_name="us-gov-west-1",
	aws_access_key_id="INSERT KEY HERE",
	aws_secret_access_key="INSERT KEY HERE"
)

route53_client = boto3.client(
	service_name="route53",
	region_name="us-east-1",
	aws_access_key_id="INSERT KEY HERE",
	aws_secret_access_key="INSERT KEY HERE"
)

print("Cleaning cache")
kinghorn.clean_cache()
print("Caching if needed")
kinghorn.cache_all_if_needed(ec2_client, route53_client)
print("Caching all if needed(shouldn't do anything)")
kinghorn.cache_all_if_needed(ec2_client, route53_client)
print("Getting instance info")
instance_info = kinghorn.load_info_from_cache("ec2/instance")
print("Getting volume info")
volume_info = kinghorn.load_info_from_cache("ec2/volume")
print("Getting some record set info")
record_set_info = kinghorn.load_info_from_cache("route53/record_set")
print("Making some maps")
print(kinghorn.get_instance_id_to_name_map(instance_info))
print(kinghorn.get_instance_name_to_id_map(instance_info))
print(kinghorn.get_volume_id_to_instance_id_map(volume_info))
print(kinghorn.get_instance_id_to_volume_id_map(volume_info))
