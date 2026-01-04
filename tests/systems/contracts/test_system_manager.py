import pytest
from opsflow.systems.debian.debian_manager import DebianManager
from opsflow.systems.ubuntu.ubuntu_manager import UbuntuManager

SYSTEM_MANAGERS = [DebianManager, UbuntuManager]


@pytest.mark.parametrize("manager_cls", SYSTEM_MANAGERS)
def test_contract_methods_exist_and_return_bool(make_manager, manager_cls):
    mgr = make_manager(manager_cls)

    assert isinstance(mgr._is_reboot_required(), bool)
    assert isinstance(mgr._is_new_stable_os_available(), bool)


@pytest.mark.parametrize("manager_cls", SYSTEM_MANAGERS)
def test_contract_never_raises(make_manager, manager_cls):
    mgr = make_manager(manager_cls)

    try:
        mgr._is_reboot_required()
        mgr._is_new_stable_os_available()
    except Exception as e:
        pytest.fail(f"{manager_cls.__name__} raised {e}")
