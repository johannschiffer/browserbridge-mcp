import subprocess
import sys

def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import browserbridge._genesis; browserbridge._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import browserbridge._genesis
    assert browserbridge._genesis.NOTICE == ""
