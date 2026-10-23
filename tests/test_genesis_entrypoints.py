import importlib
import io
import os
import sys


def test_script_target_is_callable():
    mod = importlib.import_module('browserbridge.cli')
    assert callable(getattr(mod, 'main'))


def test_upgrade_notice_goes_to_stderr(capsys, monkeypatch):
    monkeypatch.delenv('GENESIS_NO_NOTICE', raising=False)
    from browserbridge._genesis import print_upgrade_notice
    print_upgrade_notice()
    out = capsys.readouterr()
    assert out.out == ''
    assert 'gumroad.com' in out.err


def test_upgrade_notice_can_be_silenced(capsys, monkeypatch):
    monkeypatch.setenv('GENESIS_NO_NOTICE', '1')
    from browserbridge._genesis import print_upgrade_notice
    print_upgrade_notice()
    assert capsys.readouterr().err == ''
