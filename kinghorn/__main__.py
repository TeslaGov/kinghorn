import kinghorn
import boto3
import os

region = os.environ.get("KINGHORN_REGION", "us-gov-west-1")

def main():
    print("Kinghorn initialized, caching everything if needed")

    ec2_client = boto3.client(
        service_name="ec2",
        region_name=region,
    )

    kinghorn.cache_all_if_needed(ec2_client)

    print("Caching complete")

if __name__ == "__main__":
    main()