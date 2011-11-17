from model.settings import settings
from model.group_manager import GroupManager
from model.group_manager import RealGroupManager
from model.group_manager import MockGroupManager

class MockAutoScaleConnection():
    init_count = 0
    get_all_instances_count = 0

    def __init__(self, *args):
        MockAutoScaleConnection.init_count += 1

    def get_all_instances(self):
        MockAutoScaleConnection.get_all_instances_count += 1
        return []

def test_real_group_manager_exists(monkeypatch):
    monkeypatch.setattr(settings, 'MOCK_GROUP_MANAGER', False)
    gm = GroupManager()
    assert isinstance(gm, RealGroupManager)

def test_group_manager_list_connects_and_lists_once_when_listing(monkeypatch):
    monkeypatch.setattr(settings, 'MOCK_GROUP_MANAGER', False)
    RealGroupManager.connection = MockAutoScaleConnection

    access = 'access_key'
    secret = 'secret_key'

    gm = GroupManager()
    gm.list_groups(access, secret)
    assert 1 == MockAutoScaleConnection.init_count
    assert 1 == MockAutoScaleConnection.get_all_instances_count

def test_mock_group_manager_exists():
    mock_gm = GroupManager()
    assert isinstance(mock_gm, MockGroupManager)

def test_mock_group_creates_groups():
    mock_gm = GroupManager()

    access = 'access_key'
    secret = 'secret_key'
    how_many = 3

    mock_gm.start_group(access, secret, 'first', how_many)
    mock_gm.start_group(access, secret, 'second', how_many)
    groups = mock_gm.list_groups(access, secret)
    assert 2 == len(groups)

def test_mock_group_stops_groups():
    mock_gm = GroupManager()

    access = 'access_key'
    secret = 'secret_key'
    how_many = 3

    mock_gm.start_group(access, secret, 'first', how_many)
    mock_gm.start_group(access, secret, 'second', how_many)
    mock_gm.stop_group(access, secret, 'first')
    groups = mock_gm.list_groups(access, secret)
    assert 1 == len(groups)
