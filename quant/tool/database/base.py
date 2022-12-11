# -*- encoding:utf-8 -*-
"""
date: 2020/8/17
author: Berserker
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.orm import scoped_session
from config.secure import *
from contextlib import contextmanager
from quant.models.base import Base


class XQuery(Query):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = True
        return super(Query, self).filter_by(**kwargs)


class SQLAlchemy(object):
    _engine = create_engine(
        SQLALCHEMY_DATABASE_URI,
        pool_size=16,
        echo=SQLALCHEMY_ECHO or False,
        connect_args={
            'auth_plugin': "mysql_native_password",
            'charset': 'utf8'
        }
    )
    _session_factory = sessionmaker(bind=_engine, query_cls=XQuery)
    # Session = scoped_session(_session_factory)
    Session = _session_factory

    @classmethod
    def create_all(cls):
        Base.metadata.create_all(cls._engine)

    @classmethod
    def session_connector(cls, func):
        def decorator(*args, **kwargs):
            session = cls.Session()
            ret = func(*args, **kwargs, session=session)
            session.close()
            return ret
        return decorator

    @staticmethod
    @contextmanager
    def auto_commit(session, is_throw=True):
        try:
            yield
            session.commit()
        except Exception as e:
            session.rollback()
            if is_throw:
                raise e
            else:
                print(str(e))

    @classmethod
    @contextmanager
    def session_context(cls):
        session = cls.Session()
        yield session
        session.close()   
       
    @classmethod
    @contextmanager
    def connect_context(cls):
        conn = cls._engine.connect()
        yield conn
        conn.close()
    
    @classmethod
    @contextmanager
    def engine_begin(cls, is_throw=True):
        conn = cls._engine.connect()
        trans = conn.begin()
        yield conn
        try:
            trans.commit()
        except Exception as e:
            trans.rollback()
            if is_throw:
                raise e
            else:
                print(str(e))
        conn.close()
    

