import subprocess
import sys

def test_notice_prints_to_stderr():
    res = subprocess.run([sys.executable, "-c", "import browserbridge._genesis; browserbridge._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert 'ko-fi.com/johannschiffer' in res.stderr
    assert '100% Free & Open Source' in res.stderr

def test_notice_suppression():
    import os
    env = os.environ.copy()
    env["GENESIS_NO_NOTICE"] = "1"
    res = subprocess.run([sys.executable, "-c", "import browserbridge._genesis; browserbridge._genesis.print_upgrade_notice()"], env=env, capture_output=True, text=True)
    assert 'ko-fi.com' not in res.stderr
