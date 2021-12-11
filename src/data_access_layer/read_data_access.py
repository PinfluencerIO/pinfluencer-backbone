from src.data_access_layer import BaseEntity
from src.data_access_layer.brand import Brand
from src.data_access_layer.product import Product
from src.interfaces.data_manager_interface import DataManagerInterface


def load_by_id(id_, resource: BaseEntity, data_manager: DataManagerInterface):
    try:
        return (data_manager.session
                .query(resource)
                .filter(resource.id == id_)
                .first())
    finally:
        data_manager.session.commit()


def load_brand_by_auth_id(id_, data_manager: DataManagerInterface):
    print(f'load_brand_by_auth_id({id_})')
    try:
        brand = (data_manager.session.query(Brand).filter(Brand.auth_user_id == id_).first())
        print(f'loaded by auth_id {brand}')
        return brand
    finally:
        data_manager.session.commit()


def load_brands(data_manager: DataManagerInterface):
    try:
        return data_manager.session.query(Brand).all()
    finally:
        data_manager.session.commit()


def load_max_3_products_for_brand(id_, data_manager: DataManagerInterface):
    try:
        return data_manager.session.query(Product).filter(Product.brand_id == id_).limit(3).all()
    finally:
        data_manager.session.commit()


def load_all_products_for_brand_id(id_, data_manager):
    try:
        return data_manager.session.query(Product).filter(Product.brand_id == id_).all()
    finally:
        data_manager.session.commit()


def load_all_products(data_manager):
    try:
        return data_manager.session.query(Product).all()
    finally:
        data_manager.session.commit()


def load_product_by_id_owned_by_brand(product_id, brand_dict, data_manager):
    try:
        return data_manager.session.query(Product).filter((Product.brand_id == brand_dict['id']),
                                                          (Product.id == product_id)).first()
    finally:
        data_manager.session.commit()
