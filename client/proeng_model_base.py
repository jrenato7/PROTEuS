from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserProeng(Base):

    __tablename__ = 'user'

    id_u = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)

    def __init__(self, name, email):

        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


class ProcessingProeng(Base):

    __tablename__ = 'processing'

    id_p = Column(Integer, primary_key=True)
    id_user = Column(Integer)
    status = Column(Integer)
    pdbid = Column(String)
    cutoff = Column(Float(precision=2))
    url = Column(String(64))
    notification_user = Column(Integer)

    def __init__(self, id_u, pdbid, cutoff, url, status=0, nus=0):
        self.id_user = id_u
        self.pdbid = pdbid
        self.cutoff = cutoff
        self.url = url
        self.status = status
        self.notification_user = nus


class ContactProeng(Base):

    __tablename__ = 'contact'

    id_ctt = Column(Integer, primary_key=True)
    id_p = Column(Integer)
    ctt_type = Column(String(30))
    ctt_status = Column(Integer)
    ctt_chain = Column(String(4))
    ctt_sequence = Column(Integer)

    def __init__(self, id_p, tp, status, chain, seq):
        self.id_p = id_p
        self.ctt_type = tp
        self.ctt_status = status
        self.ctt_chain = chain
        self.ctt_sequence = seq


class AtomProeng(Base):

    __tablename__ = 'atom'

    id_atom = Column(Integer, primary_key=True)
    id_ctt = Column(Integer)
    sequence = Column(Integer)
    name = Column(String(5))
    level = Column(String(5))
    bfactor = Column(Float)
    occupancy = Column(Float)
    element = Column(String(10))
    serial_number = Column(Integer)
    fullname = Column(String(10))
    coord = Column(String(25))
    type = Column(Integer)

    def __init__(self, id_c, seq, nm, lv, bf, oc, el, sn, fn, co, tp=1):
        self.id_ctt = id_c
        self.sequence = seq
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co
        self.type = tp


class AlignProeng(Base):

    __tablename__ = 'align'

    id_alg = Column(Integer, primary_key=True)
    id_ctt = Column(Integer)
    id_ctt_search_db = Column(Integer)
    al_score = Column(Float)
    al_type = Column(String(7))
    pdbid = Column(String(4))
    chain = Column(String(4))
    r1 = Column(String(7))
    r2 = Column(String(7))
    rotation = Column(Text)
    translation = Column(Text)

    def __init__(self, id_ctt, id_rc, score, type, pdbid, chain, r1, r2, r, t):
        self.id_ctt = id_ctt
        self.id_ctt_search_db = id_rc
        self.al_score = round(score, 2)
        self.al_type = type
        self.pdbid = pdbid
        self.chain = chain
        self.r1 = r1
        self.r2 = r2
        self.rotation = r
        self.translation = t


class AtomAlignProeng(Base):

    __tablename__ = 'atom_align'

    id_atom = Column(Integer, primary_key=True)
    id_align = Column(Integer)
    name = Column(String(5))
    level = Column(String(5))
    bfactor = Column(Float)
    occupancy = Column(Float)
    element = Column(String(10))
    serial_number = Column(Integer)
    fullname = Column(String(10))
    coord = Column(String(25))

    def __init__(self, id_c, nm, lv, bf, oc, el, sn, fn, co):
        self.id_align = id_c
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co
