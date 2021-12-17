from src.data_access_layer import BaseEntity
from src.data_access_layer.brand import Brand
from src.data_access_layer.product import Product
from src.interfaces.data_manager_interface import DataManagerInterface
from src.processors import types


def load_item(resource: BaseEntity, data_manager: DataManagerInterface) -> BaseEntity:
    try:
        return data_manager.session.query(resource).first()
    finally:
        data_manager.session.commit()


def load_collection(resource: BaseEntity, data_manager: DataManagerInterface) -> list[BaseEntity]:
    try:
        return data_manager.session.query(resource).all()
    finally:
        data_manager.session.commit()


def load_by_id(id_, resource: BaseEntity, data_manager: DataManagerInterface):
    try:
        return (data_manager.session
                .query(resource)
                .filter(resource.id == id_)
                .first())
    finally:
        data_manager.session.commit()


def load_brand_for_authenticated_user(auth_user_id, data_manager: DataManagerInterface):
    try:
        first = data_manager.session.query(Brand).filter(Brand.auth_user_id == auth_user_id).first()
        print(f'load_brand_for_authenticated_user: {first}')
        return first
    finally:
        data_manager.session.commit()


def load_products_for_authenticated_user(auth_user_id, data_manager: DataManagerInterface):
    try:
        return (data_manager.session.query(Product).join(Brand).filter(
            Brand.auth_user_id == auth_user_id).all())
    finally:
        data_manager.session.commit()


def load_product_by_id_for_auth_id(product_id, auth_user_id, data_manager: DataManagerInterface):
    print(f'load_product_by_id_for_auth_id({product_id}, {auth_user_id})')
    try:
        loaded = (data_manager.session.query(Product).join(Brand).filter(
            Brand.auth_user_id == auth_user_id, Product.id == product_id).first())
        print(f'load_product_by_id_for_auth_id: {loaded}')
        return loaded
    finally:
        data_manager.session.commit()


def load_max_3_products_for_brand(type_, data_manager: DataManagerInterface):
    try:
        # Ignore type for this special case
        brands = load_collection(types['brand']['type'], data_manager)
        products = []
        for brand in brands:
            products.extend(data_manager.session.query(Product).filter(Product.brand_id == brand.id).limit(3).all())

        return products
    finally:
        data_manager.session.commit()


def load_all_products_for_brand_id(id_, data_manager):
    try:
        return data_manager.session.query(Product).filter(Product.brand_id == id_).all()
    finally:
        data_manager.session.commit()
