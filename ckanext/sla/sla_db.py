from sqlalchemy.sql.expression import or_
from sqlalchemy import types, Column, Table, ForeignKey
import vdm.sqlalchemy
import types as _types
from ckan.model import domain_object
from ckan.model.meta import metadata, Session, mapper
from sqlalchemy.orm import relationship, backref
from ckan.model.user import User
import uuid


def make_uuid():
    return unicode(uuid.uuid4())

sla_table = Table('sla', metadata,
                        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                        Column('name', types.UnicodeText, default=''),
                        Column('level', types.Integer, default=0),
                        Column('rate_rq_s', types.BigInteger, default=0),
                        Column('speed_mb_s', types.Float, default=0),
                        Column('priority', types.Integer, default=0),
                        )

sla_mapping_table = Table('sla_mapping', metadata,
                            Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                            Column('user_id', ForeignKey('user.id')),
                            Column('sla_id', ForeignKey('sla.id')),
                            )

class SLA(domain_object.DomainObject):
    def __init__(self, name, level, rate_rq_s=None, speed_mb_s=None, priority=None):
        assert name
        assert level
        self.name = name
        self.level = level
        self.rate_rq_s = rate_rq_s
        self.speed_mb_s = speed_mb_s
        self.priority = priority
    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kw).all()
    @classmethod
    def getAll(cls, **kw):
        query = Session.query(cls).autoflush(False)
        return query.all()
    @classmethod
    def delete(cls, **kw):
        query = Session.query(cls).autoflush(False).filter_by(**kw).all()
        for i in query:
            Session.delete(i)
        return
    
class SLA_Mapping(domain_object.DomainObject):
    def __init__(self, user_id, sla_id):
        assert user_id
        assert sla_id
        self.user_id = user_id
        self.sla_id = sla_id
        
    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kw).all()
    @classmethod
    def getAll(cls, **kw):
        query = Session.query(cls).autoflush(False)
        return query.all()
    @classmethod
    def delete(cls, **kw):
        query = Session.query(cls).autoflush(False).filter_by(**kw).all()
        for i in query:
            Session.delete(i)
        return
#properties={
#    "sla" : relationship(Package, single_parent=True, backref=backref('sla', cascade="all, delete, delete-orphan"))
#    }
mapper(SLA, sla_table)
mapper(SLA_Mapping, sla_mapping_table, properties={
    "sla_mapping": relationship(User, backref=backref('sla_mapping', cascade="all, delete, delete-orphan"))#,
#    "sla_mapping": relationship(SLA, backref=backref('sla_mapping', cascade="all, delete, delete-orphan"))                            )
})