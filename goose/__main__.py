#!/usr/bin/env python3
import os
import sys

from . import Goose

import logging
logging.basicConfig()
logger = logging.getLogger("goose")
logger.setLevel(logging.DEBUG)

token = os.getenv("TOKEN")
if not token:
    logger.error("Please set the TOKEN environment variable")
    sys.exit(1)

goose = Goose()
goose.run(token)
