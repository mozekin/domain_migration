import requests
import json
import boto3
import logging

# set up logging
logging.basicConfig(filename='extract_records.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# GoDaddy API endpoint for retrieving domain records
godaddy_url = "https://api.godaddy.com/v1/domains/{domain}/records"

# Replace with your GoDaddy API key and secret
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# Replace with your domain name
domain = "orbit3.io

# connect to AWS Route 53
route53 = boto3.client('route53')

# specify the hosted zone ID
hosted_zone_id = 'ZONEID'

try:
    # extract records from GoDaddy API
    response = requests.get(godaddy_url.format(domain=domain),
                            headers={
                                "Authorization": f"sso-key {api_key}:{api_secret}"
                            })

    if response.status_code == 200:
        records = json.loads(response.text)
    else:
        raise Exception(f"Failed to retrieve domain records. Status code: {response.status_code}")

    # create records in AWS Route 53
    for record in records:
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': 'Creating record from GoDaddy API',
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': record['name'],
                            'Type': record['type'],
                            'TTL': record['ttl'],
                            'ResourceRecords': [
                                {
                                    'Value': record['data']
                                }
                            ]
                        }
                    }
                ]
            }
        )

        # log the response
        logging.info(f"Record created: {record['name']}. Response: {response}")

except Exception as e:
    logging.error(f"Error creating records: {e}")
