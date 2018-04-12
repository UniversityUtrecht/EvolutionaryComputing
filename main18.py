import pyximport; pyximport.install()
import subprocess

subprocess.call(["cython", "-a", "test_qwe.pyx"])

import test_qwe
test_qwe.run_main(18)