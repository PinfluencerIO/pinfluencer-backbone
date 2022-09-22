import datetime
import json
import random
import re
import typing
import uuid
from enum import Enum
from typing import Union

from src.exceptions import AutoFixtureException


class AutoFixture:

    def create_many_dict(self, dto,
                         ammount,
                         seed=None,
                         num=None,
                         nest=0,
                         list_limit=100):
        return self.create_many(dto=dto,
                                ammount=ammount,
                                seed=seed,
                                num=num,
                                nest=nest,
                                list_limit=list_limit).__dict__

    def create_dict(self, dto,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        return self.create(dto=dto,
                           seed=seed,
                           num=num,
                           nest=nest,
                           list_limit=list_limit).__dict__

    def create_many(self, dto,
                    ammount,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        list_of_dtos = []
        for i in range(0, ammount):
            list_of_dtos.append(self.create(dto=dto,
                                            seed=seed,
                                            num=num,
                                            nest=nest,
                                            list_limit=list_limit))
        return list_of_dtos

    def create(self, dto,
               seed=None,
               num=None,
               nest=0,
               list_limit=100):
        self.__validate_predictable_data(num, seed)

        try:
            new_value = dto()
        except TypeError:
            raise AutoFixtureException("class must empty ctor, if a dataclass, must have fields initialised to "
                                       "sensible defaults or None")

        is_predictable_data = seed is not None and num is not None

        members = dto.__annotations__.items()
        print(f"nest {nest}")
        for (key, _type) in members:

            if _type is str:
                self.__generate_string_field(is_predictable_data, key, new_value, seed)

            if _type is bool:
                self.__generate_bool_field(is_predictable_data, key, new_value, num)

            if _type == datetime.datetime:
                self.__generate_datetime_field(is_predictable_data, key, new_value, num)

            if _type is int:
                self.__generate_int_field(is_predictable_data, key, new_value, num)

            if _type is float:
                self.__generate_float_field(is_predictable_data, key, new_value, num)

            if _type == list[str]:
                self.__generate_str_list_field(is_predictable_data, key, new_value, num, seed, list_limit)

            if _type == list[int]:
                self.__generate_int_list_field(is_predictable_data, key, new_value, num, list_limit)

            if _type == list[bool]:
                self.__generate_bool_list_field(is_predictable_data, key, new_value, num, list_limit)

            if _type == list[datetime.datetime]:
                self.__generate_datetime_list_field(is_predictable_data, key, new_value, num, list_limit)

            if _type == list[float]:
                self.__generate_float_list_field(is_predictable_data, key, new_value, num, list_limit)

            if type(_type) is type(Enum):
                self.__generate_random_enum_field(_type, is_predictable_data, key, new_value, num)

            if bool(typing.get_type_hints(_type)):
                self.__generate_class_field(_type, key, nest, new_value, num, seed)

            if typing.get_origin(_type) is list:
                arg = typing.get_args(_type)[0]
                if type(arg) is type(Enum):
                    self.__generate_list_of_enums_field(arg, is_predictable_data, key, new_value, num, list_limit)
                if bool(typing.get_type_hints(arg)):
                    self.__generate_class_list(arg, is_predictable_data, key, nest, new_value, num, seed, list_limit)

        return new_value

    def __generate_class_field(self, _type, key, nest, new_value, num, seed):
        setattr(new_value, key, self.create(dto=_type,
                                            seed=seed,
                                            num=num,
                                            nest=nest + 1))

    def __generate_class_list(self, _type, is_predictable_data, key, nest, new_value, num, seed, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(self.create(dto=_type,
                                                          seed=seed,
                                                          num=num,
                                                          nest=nest + 1))
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(self.create(dto=_type,
                                                          seed=seed,
                                                          num=num,
                                                          nest=nest + 1))
        setattr(new_value, key, value_for_given_member)

    def __generate_list_of_enums_field(self, _type, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                enum_iterable = list(_type)
                length = len(enum_iterable)
                index = num % length
                value_for_given_member.append(enum_iterable[index])
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(random.choice(list(_type)))
        setattr(new_value, key, value_for_given_member)

    def __generate_random_enum_field(self, _type, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            enum_iterable = list(_type)
            length = len(enum_iterable)
            index = num % length
            value_for_given_member = enum_iterable[index]
        else:
            value_for_given_member = random.choice(list(_type))
        setattr(new_value, key, value_for_given_member)

    def __generate_datetime_list_field(self, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(datetime.datetime(2, 2, 2, 2, 2, 2))
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(datetime.datetime.utcnow())
        setattr(new_value, key, value_for_given_member)

    def __generate_bool_list_field(self, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(bool(num))
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(random.choice([True, False]))
        setattr(new_value, key, value_for_given_member)

    def __generate_datetime_field(self, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = datetime.datetime(num, num, num, num, num, num)
        else:
            value_for_given_member = datetime.datetime.utcnow()
        setattr(new_value, key, value_for_given_member)

    def __generate_bool_field(self, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = bool(num)
        else:
            value_for_given_member = random.choice([True, False])
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_float_list_field(is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                trailing_decimals = ""
                for i in range(0, num):
                    trailing_decimals = f"{trailing_decimals}{num}"
                value_for_given_member_item = float(f"{num}.{trailing_decimals}")
                value_for_given_member.append(value_for_given_member_item)
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(random.uniform(0, 100))
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_int_list_field(is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(num + i)
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member.append(random.randint(0, 100))
        setattr(new_value, key, value_for_given_member)

    def __generate_str_list_field(self, is_predictable_data, key, new_value, num, seed, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member_item = key
                value_for_given_member_item = f"{value_for_given_member_item}{seed}{i}"
                value_for_given_member.append(value_for_given_member_item)
        else:
            value_for_given_member = []
            for i in range(0, random.randint(0, list_limit)):
                value_for_given_member_item = key
                value_for_given_member_item = f"{value_for_given_member_item}{self.__generate_random_seed()}"
                value_for_given_member.append(value_for_given_member_item)
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_random_seed() -> str:
        return str(uuid.uuid4()).split("-")[0]

    @staticmethod
    def __validate_predictable_data(num, seed):
        if seed is not None and num is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")
        if seed is not None and num is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")

    @staticmethod
    def __generate_float_field(is_predictable_data, key, new_value, num):
        if is_predictable_data:
            trailing_decimals = ""
            for i in range(0, num):
                trailing_decimals = f"{trailing_decimals}{num}"
            value_for_given_member = float(f"{num}.{trailing_decimals}")
        else:
            value_for_given_member = random.uniform(0, 100)
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_int_field(is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = num
        else:
            value_for_given_member = random.randint(0, 100)
        setattr(new_value, key, value_for_given_member)

    def __generate_string_field(self, is_predictable_data, key, new_value, seed):
        value_for_given_member = key
        if is_predictable_data:
            value_for_given_member = f'{value_for_given_member}{seed}'
        else:
            value_for_given_member = f'{value_for_given_member}{self.__generate_random_seed()}'
        setattr(new_value, key, value_for_given_member)


class PinfluencerObjectMapper:

    def map(self, _from, to):
        return self.__generic_map(_from=_from,
                                  to=to,
                                  propValues=vars(_from).items())

    def map_from_dict(self, _from, to):
        return self.__generic_map(_from=_from,
                                  to=to,
                                  propValues=_from.items())

    def __generic_map(self, _from, to, propValues):
        new_dto = to()
        dict_to = to.__annotations__
        for property, value in propValues:
            if property in dict_to:
                setattr(new_dto, property, value)
                if bool(typing.get_type_hints(dict_to[property])):
                    setattr(new_dto, property, self.map(_from=value, to=dict_to[property]))
        return new_dto


def print_exception(e):
    print(''.join(['Exception ', str(type(e))]))
    print(''.join(['Exception ', str(e)]))


class JsonSnakeToCamelSerializer:

    def serialize(self, data: Union[dict, list]) -> str:
        return json.dumps(self.__snake_case_to_camel_case_dict(d=data), default=str)

    def __snake_case_to_camel_case_dict(self, d):
        if isinstance(d, list):
            return [self.__snake_case_to_camel_case_dict(i) if isinstance(i, (dict, list)) else i for i in d]
        return {self.__snake_case_key_to_camel_case(a): self.__snake_case_to_camel_case_dict(b) if isinstance(b, (
            dict, list)) else b for a, b in d.items()}

    @staticmethod
    def __snake_case_key_to_camel_case(key: str) -> str:
        components = key.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])


class JsonCamelToSnakeCaseDeserializer:

    def deserialize(self, data: str) -> Union[dict, list]:
        data_dict = json.loads(data)
        return self.__camel_case_to_snake_case_dict(d=data_dict)

    def __camel_case_to_snake_case_dict(self, d):
        if isinstance(d, list):
            return [self.__camel_case_to_snake_case_dict(i) if isinstance(i, (dict, list)) else i for i in d]
        return {self.__camel_case_key_to_snake_case(a): self.__camel_case_to_snake_case_dict(b) if isinstance(b, (
            dict, list)) else b for a, b in d.items()}

    @staticmethod
    def __camel_case_key_to_snake_case(key: str) -> str:
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', key)
        return '_'.join(map(str.lower, words))


def valid_uuid(id_):
    try:
        val = uuid.UUID(id_, version=4)
        # If uuid_string is valid hex, but invalid uuid4, UUID.__init__ converts to valid uuid4.
        # This is bad for validation purposes, so try and match str with UUID
        if str(val) == id_:
            return True
        else:
            print_exception(f'equality failed {val} {id_}')
    except ValueError as ve:
        print_exception(ve)
    except AttributeError as e:
        print_exception(e)

    return False
