import json
import os
import shutil

class Kinghorn:
    def __init__(self, cache_path, logger):
        self.cache_path = cache_path
        self.logger = logger

    def create_folder(self, folder_path):
        self.logger.debug("Creating folder " + folder_path)

        try:
            os.makedirs(folder_path)
        except:
            pass

    def cache_instance_info(self, ec2_client):
        """cache ec2 instance information"""
        self.logger.info("Starting EC2 instance caching")
        instance_paginator = ec2_client.get_paginator("describe_instances")
        folder_path = self.cache_path + "/instance"
        self.create_folder(folder_path)

        for instance_response in instance_paginator.paginate():
            for reservation in instance_response.get("Reservations"):
                for instance in reservation.get("Instances"):
                    file_path = folder_path + "/" + instance.get("InstanceId") + ".json"

                    with open(file_path, "w") as out_file:
                        self.logger.debug("Dumping instance information to " + file_path)
                        json.dump(instance, out_file, default=str)

        self.logger.info("Finished EC2 instance caching")

    def cache_volume_info(self, ec2_client):
        """cache ec2 volume information"""
        self.logger.info("Starting EC2 volume caching")
        volume_paginator = ec2_client.get_paginator("describe_volumes")
        folder_path = self.cache_path + "/volume"
        self.create_folder(folder_path)

        for volume_response in volume_paginator.paginate():
            for volume in volume_response.get("Volumes"):
                file_path = folder_path + "/" + volume.get("VolumeId") + ".json"

                with open(file_path, "w") as out_file:
                    self.logger.debug("Dumping volume information to " + file_path)
                    json.dump(volume, out_file, default=str)

        self.logger.info("Finished EC2 volume caching")

    def cache_snapshot_info(self, ec2_client):
        """cache ec2 snapshot information"""
        self.logger.info("Starting EC2 snapshot caching")
        snapshot_paginator = ec2_client.get_paginator("describe_snapshots")
        folder_path = self.cache_path + "/snapshot"
        self.create_folder(folder_path)

        for snapshot_response in snapshot_paginator.paginate(OwnerIds=["self"]):
            for snapshot in snapshot_response.get("Snapshots"):
                file_path = folder_path + "/" + snapshot.get("SnapshotId") + ".json"

                with open(file_path, "w") as out_file:
                    json.dump(snapshot, out_file, default=str)

    def cache_all_if_needed(self, ec2_client):
        """cache all ec2 information if needed"""
        if not os.path.exists(self.cache_path + "/instance"):
            self.cache_instance_info(ec2_client)

        if not os.path.exists(self.cache_path + "/volume"):
            self.cache_volume_info(ec2_client)

        if not os.path.exists(self.cache_path + "/snapshot"):
            self.cache_snapshot_info(ec2_client)

    def cache_all_ec2(self, ec2_client):
        """cache all ec2 information"""
        self.cache_instance_info(ec2_client)
        self.cache_volume_info(ec2_client)
        self.cache_snapshot_info(ec2_client)

    def clean_cache(self):
        """clean our cache if it exists"""
        try:
            shutil.rmtree("cache")
        except:
            pass

    def load_info_from_cache(self, entity):
        """load information about an entity from cache"""

        if (entity not in ["instance", "volume", "snapshot"]):
            self.logger.error(entity + " is not currently supported by Kinghorn")
            return

        entity_info = {}

        folder_path = self.cache_path + "/" + entity

        for file in os.listdir(folder_path):
            file_path = folder_path + "/" + file
            entity_id = file[:-5]

            with open(file_path, "r") as input_file:
                entity_info[entity_id] = json.load(input_file)

        return entity_info

    def get_instance_id_to_name_map(self, instance_info):
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

    def get_instance_name_to_id_map(self, instance_info):
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

    def get_instance_id_to_volume_id_map(self, volume_info):
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

    def get_volume_id_to_instance_id_map(self, volume_info):
        """Generate volume id to instance id map.  Unattached volumes will be ignored."""
        instance_id_to_volume_id_map = {}

        for volume_id in volume_info:
            volume = volume_info.get(volume_id)

            if volume.get("Attachments"):
                # Attached volumes
                ec2_instance_id = volume.get("Attachments")[0].get("InstanceId")
                instance_id_to_volume_id_map[volume_id] = ec2_instance_id

        return instance_id_to_volume_id_map