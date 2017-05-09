#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dbuser = os.environ.get("WEBDBUSER", "")
dbpass = os.environ.get("WEBDBPASS", "")
dbhost = os.environ.get("HOSTDB", "")
mysql_conn = 'mysql://%s:%s@%s/proeng' % (dbuser, dbpass, dbhost)
engine = create_engine(mysql_conn, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)