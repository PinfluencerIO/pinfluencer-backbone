from unittest import TestCase

from src.crosscutting import JsonSnakeToCamelSerializer, JsonCamelToSnakeCaseDeserializer

TEST_DICT_JSON = "{\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2}"
TEST_LIST_SERIALIZATION_JSON = "[{\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2}, {\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2}, {\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2}]"
TEST_LIST_SERIALIZATION_EMPTY_JSON = "[]"
TEST_DICT_NESTED_JSON = "{\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2, \"nestedObject\": {\"name\": \"dennis reynolds\", \"snakeValue\": 3}, \"arrayValue\": [\"apples\", \"pears\", \"oranges\"]}"
TEST_DICT_JSON_WITH_CAPS_KEY = "{\"name\": \"adam raymond\", \"snakeInValue\": \"snake_in_value\", \"value2To3Values\": 2, \"capitalLETTERSValue\": 1}"

TEST_DICT = {
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2
}


TEST_LIST_SERIALIZATION_EMPTY = []


TEST_LIST_SERIALIZATION = [{
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2
},{
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2
},{
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2
}]

TEST_NESTED_DICT = {
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2,
    "nested_object": {
        "name": "dennis reynolds",
        "snake_value": 3
    },
    "array_value": ["apples", "pears", "oranges"]
}


TEST_DICT_WITH_CAPS_KEY = {
    "name": "adam raymond",
    "snake_in_value": "snake_in_value",
    "value_2_to_3_values": 2,
    "capital_letters_value": 1
}


class TestJsonSnakeToCamelSerializer(TestCase):

    def setUp(self):
        self.__json_snake_to_camel_serializer = JsonSnakeToCamelSerializer()

    def test_serialize(self):

        # arrange
        input_data = TEST_DICT
        expected = TEST_DICT_JSON

        # act
        actual = self.__json_snake_to_camel_serializer.serialize(input_data)

        # assert
        assert expected == actual

    def test_serialize_nested(self):

        # arrange
        input_data = TEST_NESTED_DICT
        expected = TEST_DICT_NESTED_JSON

        # act
        actual = self.__json_snake_to_camel_serializer.serialize(input_data)

        # assert
        assert expected == actual

    def test_serialize_collection(self):

        # arrange
        input_data = TEST_LIST_SERIALIZATION
        expected = TEST_LIST_SERIALIZATION_JSON

        # act
        actual = self.__json_snake_to_camel_serializer.serialize(input_data)

        # assert
        assert expected == actual

    def test_serialize_collection_empty(self):

        # arrange
        input_data = TEST_LIST_SERIALIZATION_EMPTY
        expected = TEST_LIST_SERIALIZATION_EMPTY_JSON

        # act
        actual = self.__json_snake_to_camel_serializer.serialize(input_data)

        # assert
        assert expected == actual

class TestJsonCamelToSnakeCaseDeserializer(TestCase):

    def setUp(self):
        self.__json_camel_to_snake_case_deserializer = JsonCamelToSnakeCaseDeserializer()

    def test_deserialize(self):

        # arrange
        expected = TEST_DICT_WITH_CAPS_KEY
        input_data = TEST_DICT_JSON_WITH_CAPS_KEY

        # act
        actual = self.__json_camel_to_snake_case_deserializer.deserialize(input_data)

        # assert
        assert expected == actual

    def test_deserialize_nested(self):

        # arrange
        expected = TEST_NESTED_DICT
        input_data = TEST_DICT_NESTED_JSON

        # act
        actual = self.__json_camel_to_snake_case_deserializer.deserialize(input_data)

        # assert
        assert expected == actual

    def test_deserialize_collection(self):

        # arrange
        expected = TEST_LIST_SERIALIZATION
        input_data = TEST_LIST_SERIALIZATION_JSON

        # act
        actual = self.__json_camel_to_snake_case_deserializer.deserialize(input_data)

        # assert
        assert expected == actual

    def test_serialize_collection_empty(self):

        # arrange
        expected = TEST_LIST_SERIALIZATION_EMPTY
        input_data = TEST_LIST_SERIALIZATION_EMPTY_JSON

        # act
        actual = self.__json_camel_to_snake_case_deserializer.deserialize(input_data)

        # assert
        assert expected == actual
