import uuid
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

PRODUCT_TBL_NAME = 'product'
BRAND_TBL_NAME = 'brand'


def uuid4_str():
    return str(uuid.uuid4())


@dataclass
class BaseEntity:
    id: str = Column(String(length=36), primary_key=True, default=uuid4_str, nullable=False)
    created: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    @abstractmethod
    def as_dict(self):
        pass


Base = declarative_base()


def to_list(data):
    data_dict = []
    for data_item in data:
        data_dict.append(data_item.as_dict())
    return data_dict


class ValueEnum(Enum):
    Sustainable = "Sustainable"
    Organic = "Organic"
    Recycled = "Recycled"
    Vegan = "Vegan"


class CategoryEnum(Enum):
    Food = "Food"
    Fashion = "Fashion"
    Fitness = "Fitness"
    Pet = "Pet"
