import json
import os
import shutil
import sys
import logging

environment = os.environ.get("KINGHORN_ENVIRONMENT", "default")
logging_level = os.environ.get("KINGHORN_LOGGING_LEVEL", "INFO")
logging_std_out = os.environ.get("KINGHORN_LOGGING_OUT", 0)
logging_file = os.environ.get("KINGHORN_LOGGING_FILE", "kinghorn.log")
cache_location = os.environ.get("KINGHORN_CACHE_LOCATION", "~/.kinghorn_cache")

if int(logging_std_out) == 1:
    logging.basicConfig(stream=sys.stdout, level=logging_level)
else:
    logging.basicConfig(filename=logging_file,level=logging_level)
    
logger = logging.getLogger(__name__)

# Eventually paths will be (by default), something like ~/.kinghorn_cache/default/instance/i-123.json for an EC2 instance
cache_path = cache_location + "/" + environment

def create_folder(folder_path):
    logger.debug("Creating folder " + folder_path)

    try:
        os.makedirs(folder_path)
    except:
        pass

def cache_instance_info(ec2_client):
    """cache ec2 instance information"""
    logger.info("Starting EC2 instance caching")
    instance_paginator = ec2_client.get_paginator("describe_instances")
    folder_path = cache_path + "/instance"
    create_folder(folder_path)

    for instance_response in instance_paginator.paginate():
        for reservation in instance_response.get("Reservations"):
            for instance in reservation.get("Instances"):
                file_path = folder_path + "/" + instance.get("InstanceId") + ".json"

                with open(file_path, "w") as out_file:
                    logger.debug("Dumping instance information to " + file_path)
                    json.dump(instance, out_file, default=str)

    logger.info("Finished EC2 instance caching")

def cache_volume_info(ec2_client):
    """cache ec2 volume information"""
    logger.info("Starting EC2 volume caching")
    volume_paginator = ec2_client.get_paginator("describe_volumes")
    folder_path = cache_path + "/volume"
    create_folder(folder_path)

    for volume_response in volume_paginator.paginate():
        for volume in volume_response.get("Volumes"):
            file_path = folder_path + "/" + volume.get("VolumeId") + ".json"

            with open(file_path, "w") as out_file:
                logger.debug("Dumping volume information to " + file_path)
                json.dump(volume, out_file, default=str)

    logger.info("Finished EC2 volume caching")

def cache_snapshot_info(ec2_client):
    """cache ec2 snapshot information"""
    logger.info("Starting EC2 snapshot caching")
    snapshot_paginator = ec2_client.get_paginator("describe_snapshots")
    folder_path = cache_path + "/snapshot"
    create_folder(folder_path)

    for snapshot_response in snapshot_paginator.paginate(OwnerIds=["self"]):
        for snapshot in snapshot_response.get("Snapshots"):
            file_path = folder_path + "/" + snapshot.get("SnapshotId") + ".json"

            with open(file_path, "w") as out_file:
                json.dump(snapshot, out_file, default=str)

def cache_all_ec2(ec2_client):
    """cache all ec2 information"""
    cache_instance_info(ec2_client)
    cache_volume_info(ec2_client)
    cache_snapshot_info(ec2_client)

def clean_cache():
    """clean our cache if it exists"""
    try:
        shutil.rmtree("cache")
    except:
        pass

def load_info_from_cache(entity):
    """load information about an entity from cache"""

    if (entity not in ["instance", "volume", "snapshot"]):
        logger.error(entity + " is not currently supported by Kinghorn")
        return

    entity_info = {}

    folder_path = cache_path + "/" + entity

    for file in os.listdir(folder_path):
        file_path = folder_path + "/" + file
        entity_id = file[:-5]

        with open(file_path, "r") as input_file:
            entity_info[entity_id] = json.load(input_file)

    return entity_info

def get_instance_id_to_name_map(instance_info):
    """generate instance_id to instance_name map.  If an instance has no name it will have value 'unknown'."""
    instance_id_to_name = {}

    for instance_id in instance_info:
        instance = instance_info[instance_id]

        instance_name = "unnamed"

        if "Tags" in instance:
            for tag in instance["Tags"]:
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]

        instance_id_to_name[instance["InstanceId"]] = instance_name

    return instance_id_to_name

def get_instance_name_to_id_map(instance_info):
    """
    generate instance_name to instance_id map.
    Every instance without a name will be given a key 'unknownx', where x is an incrementing number of instances without a key.
    """
    instance_name_to_id = {}
    unknown_instance_count = 0

    for instance_id in instance_info:
        instance = instance_info[instance_id]

        instance_name = "unnamed" + str(unknown_instance_count)

        if "Tags" in instance:
            for tag in instance["Tags"]:
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]

        if instance_name == "unnamed" + str(unknown_instance_count):
            unknown_instance_count = unknown_instance_count + 1

        instance_name_to_id[instance_name] = instance["InstanceId"]

    return instance_name_to_id

def get_instance_id_to_volume_id_map(volume_info):
    """Generate instance_id to volume id map.  Unattached volumes will be ignored."""
    instance_id_to_volume_id_map = {}

    for volume_id in volume_info:
        volume = volume_info.get(volume_id)

        if volume.get("Attachments"):
            # Attached volumes
            ec2_instance_id = volume.get("Attachments")[0].get("InstanceId")
            current_volumes = instance_id_to_volume_id_map.get(ec2_instance_id)

            if current_volumes is None:
                current_volumes = []

            current_volumes.append(volume_id)

            instance_id_to_volume_id_map[ec2_instance_id] = current_volumes

    return instance_id_to_volume_id_map

def get_volume_id_to_instance_id_map(volume_info):
    """Generate volume id to instance id map.  Unattached volumes will be ignored."""
    instance_id_to_volume_id_map = {}

    for volume_id in volume_info:
        volume = volume_info.get(volume_id)

        if volume.get("Attachments"):
            # Attached volumes
            ec2_instance_id = volume.get("Attachments")[0].get("InstanceId")
            instance_id_to_volume_id_map[volume_id] = ec2_instance_id

    return instance_id_to_volume_id_map