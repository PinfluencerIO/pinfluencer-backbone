import base64
import datetime
import json
import uuid
import boto3
import filetype as filetype
import io

from src.web.processors.hacks import brand_helps, product_helps
from src.web.processors.hacks.brand_helps import select_brand_by_auth_user_id
from src.web.processors.hacks.old_manual_db import execute_query, \
    COLUMNS_FOR_BRAND, COLUMNS_FOR_PRODUCT, PRODUCT_TEMPLATE, build_json_for_product, \
    format_records
from src.web.processors.hacks.product_helps import select_product_by_id
from src.web.http_util import PinfluencerResponse

s3 = boto3.client('s3')


def get_feed():
    product_number = 1
    brand_number = 1
    result = []
    for i in range(20):
        item = PRODUCT_TEMPLATE.copy()
        item_b = PRODUCT_TEMPLATE['brand'].copy()
        item['id'] = f'{product_number}_{brand_number}'
        item['name'] = f'Product {product_number}_{brand_number}'
        item['description'] = f'This is the description for product {product_number}_{brand_number}'
        item_b['id'] = f'{brand_number}'
        item_b['name'] = f'Brand {brand_number}'
        item['brand'] = item_b
        result.append(item)
        product_number = product_number + 1
        if product_number > 3:
            product_number = 1
            brand_number = brand_number + 1

    return PinfluencerResponse(body=result)


def get_all_brands() -> PinfluencerResponse:
    return PinfluencerResponse(body=brand_helps.select_all_brands())


def get_brand_by_id(event) -> PinfluencerResponse:
    return PinfluencerResponse(body=event['brand'])


def get_all_products_for_brand_with_id(event):
    brand = event['brand']
    products = product_helps.select_all_products_for_brand_with_id(brand['id'])
    return PinfluencerResponse(body=products)


def get_all_products():
    return PinfluencerResponse(body=product_helps.select_all_products())


def get_product_by_id(event) -> PinfluencerResponse:
    return PinfluencerResponse(body=event['product'])


def get_user(event):
    return event['requestContext']['authorizer']['jwt']['claims']['cognito:username']


def update_authenticated_brand(event):
    body = json.loads(event['body'])
    email = get_email(body, event)
    brand = event['auth_brand']
    sql = "\
        UPDATE brand \
            SET name = :name,\
                description = :description,\
                website = :website,\
                email = :email, \
                instahandle = :instahandle\
            WHERE id = :id\
        "
    sql_parameters = [
        {'name': 'id', 'value': {'stringValue': brand['id']}},
        {'name': 'name', 'value': {'stringValue': body['name']}},
        {'name': 'description', 'value': {'stringValue': body['description']}},
        {'name': 'website', 'value': {'stringValue': body['website']}},
        {'name': 'email', 'value': {'stringValue': email}},
        {'name': 'instahandle', 'value': {'stringValue': body['instahandle']}}
    ]
    query_results = execute_query(sql, sql_parameters)
    if query_results['numberOfRecordsUpdated'] == 1:
        updated_brand = select_brand_by_auth_user_id(get_user(event))
        return PinfluencerResponse(body=updated_brand)
    else:
        return PinfluencerResponse.as_500_error('Failed update brand')


def create_authenticated_brand(event):
    body = json.loads(event['body'])
    id_ = str(uuid.uuid4())
    email = get_email(body, event)
    user = get_user(event)
    sql = "INSERT INTO brand(" + " ,".join(COLUMNS_FOR_BRAND) + ") " \
        "VALUES (:id, :name, :description, :website, :email, :instahandle, :auth_user_id, :created)"

    sql_parameters = [
        {'name': 'id', 'value': {'stringValue': id_}},
        {'name': 'name', 'value': {'stringValue': body['name']}},
        {'name': 'description', 'value': {'stringValue': body['description']}},
        {'name': 'website', 'value': {'stringValue': body['website']}},
        {'name': 'email', 'value': {'stringValue': email}},
        {'name': 'instahandle', 'value': {'stringValue': body['instahandle']}},
        {'name': 'auth_user_id', 'value': {'stringValue': user}},
        {'name': 'created', 'value': {'stringValue': str(datetime.datetime.utcnow())}},
    ]
    query_results = execute_query(sql, sql_parameters)
    if query_results['numberOfRecordsUpdated'] == 1:
        upload_image_to_s3(id_, None, body['image'])
        new_brand = select_brand_by_auth_user_id(user)
        return PinfluencerResponse(body=new_brand)
    else:
        return PinfluencerResponse.as_500_error('Failed to create brand')


def get_authenticated_products(event):
    brand = event['auth_brand']
    sql = "SELECT " + ', '.join(COLUMNS_FOR_PRODUCT) + " FROM product WHERE brand_id=:id"
    parameters = [{'name': 'id', 'value': {'stringValue': brand['id']}}]
    query_results = execute_query(sql, parameters)
    records = format_records(query_results['records'])
    return PinfluencerResponse(body=build_json_for_product(records))


def create_authenticated_product(event):
    body = json.loads(event['body'])
    brand = event['auth_brand']
    sql = " \
        INSERT INTO product \
        (" + ",".join(COLUMNS_FOR_PRODUCT) + ") \
        VALUES \
        (:id, :name, :description, :requirements, :brand_id, :brand_name, :created)"

    id_ = str(uuid.uuid4())
    sql_parameters = [
        {'name': 'id', 'value': {'stringValue': id_}},
        {'name': 'name', 'value': {'stringValue': body['name']}},
        {'name': 'description', 'value': {'stringValue': body['description']}},
        {'name': 'requirements', 'value': {'stringValue': body['requirements']}},
        {'name': 'brand_id', 'value': {'stringValue': brand['id']}},
        {'name': 'brand_name', 'value': {'stringValue': brand['name']}},
        {'name': 'created', 'value': {'stringValue': str(datetime.datetime.utcnow())}},
    ]

    query_results = execute_query(sql, sql_parameters)
    if query_results['numberOfRecordsUpdated'] == 1:
        upload_image_to_s3(brand['id'], id_, body['image'])
        new_product = select_product_by_id(id_)
        return PinfluencerResponse(body=new_product)
    else:
        return PinfluencerResponse.as_500_error('Failed to create product')


def update_authenticated_product(event):
    body = json.loads(event['body'])
    product = event['product']
    sql = "\
            UPDATE product \
                SET name = :name,\
                    description = :description,\
                    requirements = :requirements\
                WHERE id = :id\
            "

    sql_parameters = [
        {'name': 'id', 'value': {'stringValue': product['id']}},
        {'name': 'name', 'value': {'stringValue': body['name']}},
        {'name': 'description', 'value': {'stringValue': body['description']}},
        {'name': 'requirements', 'value': {'stringValue': body['requirements']}},
    ]

    query_results = execute_query(sql, sql_parameters)
    if query_results['numberOfRecordsUpdated'] == 1:
        updated_product = select_product_by_id(product['id'])
        return PinfluencerResponse(body=updated_product)
    else:
        return PinfluencerResponse.as_500_error('Failed to create product')


def patch_product_image(event):
    etag = upload_image_to_s3(event['auth_brand']['id'], event['product']['id'], json.loads(event['body'])['image'])
    return PinfluencerResponse(status_code=200, body=etag)


def patch_brand_image(event):
    etag = upload_image_to_s3(event['auth_brand']['id'],  None, image_base64_encoded=json.loads(event['body'])['image'])
    return PinfluencerResponse(status_code=200, body=etag)


# Todo: When implementing this again in OO, use SQS so failures can be mitigated
def upload_image_to_s3(brand_id: str, product_id_, image_base64_encoded:str):
    print(f'brand {brand_id}, product{product_id_}')
    image = base64.b64decode(image_base64_encoded)
    f = io.BytesIO(image)
    file_type = filetype.guess(f)
    if file_type is not None:
        mime = file_type.MIME
        print(f'the interrupted mime for image bytes are ${mime}')
    else:
        mime = 'image/jpg'
        print(f'the interrupted mime failed for image bytes setting to ${mime}')

    if product_id_ is None:
        key = f'{brand_id}/image'
    else:
        key = f'{brand_id}/{product_id_}/image'
    s3_object = s3.put_object(Bucket='pinfluencer-product-images',
                              Key=key, Body=image,
                              ContentType=mime,
                              Tagging='public=yes')

    return {"etag": s3_object['ETag']}


def get_email(body, event):
    if ('email' in event['requestContext']['authorizer']['jwt']['claims'] and
            event['requestContext']['authorizer']['jwt']['claims']['email'] is not None):
        email = event['requestContext']['authorizer']['jwt']['claims']['email']
    else:
        email = body['email']
    return email


def delete_authenticated_product(event):
    results = execute_query("DELETE FROM product WHERE id=:id",
                            [{'name': 'id', 'value': {'stringValue': event['product']['id']}}])
    if results['numberOfRecordsUpdated'] == 1:
        return PinfluencerResponse(status_code=200, body={"message": f"Product {event['product']['id']} deleted"})
    else:
        return PinfluencerResponse(status_code=500,
                                   body={"message": f"Failed to delete product {event['product']['id']}"})
