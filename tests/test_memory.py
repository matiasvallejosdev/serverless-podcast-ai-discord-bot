import pytest
from src.memory import InMemory


@pytest.fixture
def system_message_list():
    return [{"role": "system", "content": "You're a podcast assitant."}]


@pytest.fixture
def system_message_dict():
    return {"role": "system", "content": "You're a podcast assitant."}


@pytest.fixture
def user_id():
    return 1458


@pytest.fixture
def message():
    return {"role": "user", "content": "Hello, how are you?"}


@pytest.fixture
def inmemory():
    return InMemory()


def test_default_storage(user_id, inmemory):
    inmemory._initialize(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory[0] == {"role": "system", "content": "You're a general assitant."}


def test_initialize_dict(inmemory, user_id, system_message_dict):
    inmemory.system_message = system_message_dict
    inmemory._initialize(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory[0] == system_message_dict


def test_initialize_list(inmemory, user_id, system_message_list):
    inmemory.system_message = system_message_list
    inmemory._initialize(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory[0] == system_message_list[0]


def test_initialize_string(inmemory, user_id):
    message = "You're a robot."
    inmemory.system_message = message
    inmemory._initialize(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory[0]["role"] == "system"
    assert user_memory[0]["content"] == "You're a robot."


def test_append_default_initialization(inmemory, user_id, message, system_message_dict):
    inmemory.system_message = system_message_dict
    inmemory.append(user_id, message)
    user_memory = inmemory.get(user_id)
    assert user_memory[0] == system_message_dict
    assert user_memory[1] == message


def test_append_empty_initialization(inmemory, user_id, message):
    inmemory.append(user_id, message)
    user_memory = inmemory.get(user_id)
    assert user_memory[0]["role"] == "system"
    assert user_memory[0]["content"] == "You're a general assitant."


def test_append_valid_message(inmemory, user_id, message):
    inmemory._initialize(user_id)
    inmemory.append(user_id, message)
    user_memory = inmemory.get(user_id)
    assert user_memory[1] == message


def test_append_invalid_message_format(inmemory, user_id):
    with pytest.raises(ValueError) as e:
        inmemory.append(user_id, "message")

    assert str(e.value) == "Message should be a dictionary."


def test_remove_memory(inmemory, user_id, message):
    inmemory.append(user_id, message)
    inmemory.remove(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory == []


def test_remove_memory_invalid_user_id(inmemory, user_id):
    user_id_invalid = 1234
    inmemory._initialize(user_id)
    memory = inmemory.remove(user_id_invalid)
    assert memory == f"'User {user_id_invalid} does not exist.'"


def test_get_memory(inmemory, user_id, message):
    inmemory.append(user_id, message)
    user_memory = inmemory.get(user_id)
    assert user_memory == [
        {"role": "system", "content": "You're a general assitant."},
        message,
    ]


def test_get_memory_empty(inmemory, user_id):
    inmemory._initialize(user_id)
    user_memory = inmemory.get(user_id)
    assert user_memory == [{"role": "system", "content": "You're a general assitant."}]


def test_get_memory_invalid_user_id(inmemory, user_id):
    user_id_invalid = 1234
    inmemory._initialize(user_id)

    with pytest.raises(KeyError) as e:
        inmemory.get(user_id_invalid)

    assert str(e.value) == f"'User {user_id_invalid} does not exist.'"

def test_inmemory_str(inmemory):
    assert str(inmemory) == "Storage: InMemory. Be careful, it will be lost when the program ends."