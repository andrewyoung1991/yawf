import os

from yawf import Settings


s = Settings()

s.base_dir = os.path.dirname(os.path.abspath(__file__))
s.debug = True
s.secret_key = "${secret}"
