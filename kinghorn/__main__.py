import boto3
from kinghorn import Kinghorn
import sys
import logging
import os

def main():
    region = os.environ.get("KINGHORN_REGION", "us-gov-west-1")
    environment = os.environ.get("KINGHORN_ENVIRONMENT", "default")
    logging_level = os.environ.get("KINGHORN_LOGGING_LEVEL", "INFO")
    logging_std_out = os.environ.get("KINGHORN_LOGGING_OUT", 0)
    logging_file = os.environ.get("KINGHORN_LOGGING_FILE", "kinghorn.log")
    cache_location = os.environ.get("KINGHORN_CACHE_LOCATION", "/tmp/.kinghorn_cache")

    if int(logging_std_out) == 1:
        logging.basicConfig(stream=sys.stdout, level=logging_level)
    else:
        logging.basicConfig(filename=logging_file,level=logging_level)

    logger = logging.getLogger(__name__)

    # Eventually paths will be (by default), something like /tmp/.kinghorn_cache/default/instance/i-123.json for an EC2 instance
    cache_path = cache_location + "/" + environment

    kinghorn = Kinghorn(cache_path, logger)

    logger.info("Kinghorn initialized, caching everything if needed")

    ec2_client = boto3.client(
        service_name="ec2",
        region_name=region,
    )

    kinghorn.cache_all_if_needed(ec2_client)

    logger.info("Caching complete")

if __name__ == "__main__":
    main()