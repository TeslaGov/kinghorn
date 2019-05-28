## [Kinghorn](https://en.wikipedia.org/wiki/Australian_scrub_python)
####  *Python 3 library for caching AWS resources*

#### Purpose
This library provides caching of AWS resources, which can save development time and money making API calls, as well as reduce the chances of errors taking place from running scripts against resources in flux. I use it to cache resources such as EC2 instances, volumes, and snapshots for retrieval in later scripts. I disliked having to call an API and perform an O(n^2) operation to unwrap my instance metadata every time I did something with boto3. With Kinghorn I can easily place resources in dictionaries for constant time access.

#### Opinions
I've chosen to discard metadata and "unwrap" entity metadata for storage. I've used clients instead of resources for Kinghorn to make it easy to alter the library to access low level API functions if needed. The library expects appropriate credentials in ~/.aws/credentials.

#### Installation instructions for Mac OS X
ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"  
brew install python
curl -O http://python-distribute.org/distribute_setup.py
python distribute_setup.py  
curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py  
python get-pip.py  
pip3 install boto3
python3 -m kinghorn

#### Configuration
Configuration is handled with environment variables, as follows:
 - KINGHORN_REGION - Which region you want to use
 - KINGHORN_ENVIRONMENT - Which environment your API credentials are for, for example factory, production, etc.
 - KINGHORN_LOGGING_OUT - Set to 1 to log to std out, useful for local testing and debugging
 - KINGHORN_LOGGING_LEVEL
 - KINGHORN_LOGGING_FILE
 - KINGHORN_CACHE_LOCATION


#### Files
 - kinghorn.py - The library  
 - test_kinghorn.py - An example file describing some ways to use the library and testing all functions
 
#### Future feature ideas
  - Additional entities for different services in AWS as I need them
  - Automated configurable cache expiration
  - Passthrough to the AWS API on cache miss