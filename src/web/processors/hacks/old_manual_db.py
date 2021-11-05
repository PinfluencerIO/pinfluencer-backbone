import os

import boto3

rds_client = boto3.client('rds-data')

DB_PARAMS = {
    'DATABASE_NAME': os.environ['DATABASE_NAME'],
    'DB_CLUSTER_ARN': os.environ['DB_CLUSTER_ARN'],
    'DB_SECRET_ARN': os.environ['DB_SECRET_ARN']
}


def execute_query(sql, sql_parameters=None):
    print(f'sql {sql}')
    print(f'sql parameters {sql_parameters}')
    if sql_parameters is None:
        sql_parameters = []
    response = rds_client.execute_statement(
        secretArn=DB_PARAMS['DB_SECRET_ARN'],
        database=DB_PARAMS['DATABASE_NAME'],
        resourceArn=DB_PARAMS['DB_CLUSTER_ARN'],
        sql=sql,
        parameters=sql_parameters
    )
    print(f'query response {response}')
    return response


def format_field(field):
    if list(field.keys())[0] != 'isNull':
        return list(field.values())[0]
    else:
        return ""


def format_record(record):
    return [format_field(field) for field in record]


def format_records(records):
    return [format_record(record) for record in records]


# the order is important, index number is used in boto3 records lookup for json template creation
def build_json_for_brand(records) -> list[dict]:
    results = []
    for record in records:
        print(f'${record}')
        copy_brand = BRAND_TEMPLATE.copy()
        copy_brand['id'] = record[0]
        copy_brand['name'] = record[1]
        copy_brand['description'] = record[2]
        copy_brand['website'] = record[3]
        copy_brand['email'] = record[4]
        copy_brand['instahandle'] = record[5]
        copy_brand['created'] = record[6]
        results.append(copy_brand)

    return results


COLUMNS_FOR_PRODUCT_FOR_INSERT = ['id', 'name', 'description', 'requirements', 'brand_id']

PRODUCT_TEMPLATE = {
    "id": "",
    "name": "",
    "description": "",
    "requirements": "",
    "brand": {
        "id": "",
        "name": ""
    },
    "created": ""
}

# the order is important, index number is used in boto3 records lookup for json template creation
COLUMNS_FOR_BRAND = ['id', 'name', 'description', 'website', 'email', 'instahandle', 'auth_user_id', 'created']
COLUMNS_FOR_BRAND_FOR_INSERT = ['id', 'name', 'description', 'website', 'email', 'instahandle', 'auth_user_id']

BRAND_TEMPLATE = {
    "id": "",
    "name": "",
    "description": "",
    "instahandle": "",
    "created": ""
}
