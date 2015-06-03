from sqlalchemy.sql.expression import or_, and_
from sqlalchemy import types, Column, Table, ForeignKey, func, CheckConstraint
import vdm.sqlalchemy
import types as _types
from ckan.model import domain_object
from ckan.model.meta import metadata, Session, mapper
from sqlalchemy.orm import relationship, backref
from ckan.model.user import User
import uuid


def make_uuid():
    return unicode(uuid.uuid4())

#CheckConstraint(and_('rate_rq_s>=0', 'rate_rq_s<10'))
sla_table = Table('sla', metadata,
                        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                        Column('name', types.UnicodeText, nullable=False),
                        Column('level', types.Integer, nullable=False, unique=True),
                        Column('rate_rq_s', types.Integer, CheckConstraint('rate_rq_s>=0'), nullable=False),
                        Column('speed_bytes_s', types.Integer, CheckConstraint('speed_bytes_s>=0'), nullable=False),
                        Column('timeout_s', types.Integer, CheckConstraint('timeout_s>=0'), nullable=False),
                        )
 
sla_mapping_table = Table('sla_mapping', metadata,
                            Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                            Column('sla_id',  types.UnicodeText, ForeignKey('sla.id'), nullable=False),
                            Column('user_id', types.UnicodeText, ForeignKey('user.id'), nullable=False)
                        )
    
 
class SLA(domain_object.DomainObject):
    def __init__(self, name, level, rate_rq_s, speed_bytes_s, timeout_s):
        assert name
        assert level
        assert rate_rq_s
        assert speed_bytes_s
        assert timeout_s
        self.name = name
        self.level = level
        self.rate_rq_s = rate_rq_s
        self.speed_bytes_s = speed_bytes_s
        self.timeout_s = timeout_s
    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kw).all()
    @classmethod
    def getAll(cls, **kw):
        query = Session.query(cls).autoflush(False)
        query = query.order_by(cls.name).filter(cls.name != '')
        return query.all()
    @classmethod
    def delete(cls, **kw):
        query = Session.query(cls).autoflush(False).filter_by(**kw).all()
        for i in query:
            Session.delete(i)
        return
    @classmethod
    def getCountUserPerSLA(cls, **kw):
        query = Session.query(cls, func.count(SLA_Mapping.user_id)).autoflush(False)
        query = query.filter_by(**kw)
        query = query.outerjoin(SLA_Mapping, cls.id==SLA_Mapping.sla_id)
        query = query.group_by(cls.id, cls.name)
        return query.all()
     
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
    
    @classmethod
    def getAllDetails(cls, **kw):
        query = Session.query(User, SLA).autoflush(False)
        query = query.join(cls, User.id==cls.user_id)
        query = query.filter_by(**kw)
        query = query.join(SLA, SLA.id==cls.sla_id)
        return query.all()
    
    @classmethod
    def getCountUserPerSLA(cls, **kw):
        query = Session.query(cls.sla_id, SLA.name, func.count(cls.user_id)).autoflush(False)
        query = query.join(SLA, SLA.id==cls.sla_id)
        query = query.group_by(cls.sla_id, SLA.name)
        query = query.filter_by(**kw)
        return query.all()
    
    @classmethod
    def getSLA(cls, **kw):
        query = Session.query(SLA).autoflush(False)
        query = query.join(cls, SLA.id==cls.sla_id)
        query = query.filter_by(**kw)
        return query.all()
    

mapper(SLA, sla_table)
mapper(SLA_Mapping, sla_mapping_table)
