#!/usr/bin/env python
from modules.database import database, Resource, Endpoint, Backlink


database.create_tables([Resource, Endpoint, Backlink])
