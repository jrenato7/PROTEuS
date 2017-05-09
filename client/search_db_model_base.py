from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ResidueContactSearchBase(Base):

    __tablename__ = 'residue_contact'

    id_contact = Column(Integer, primary_key=True)
    ctt_chain = Column(String(4), nullable=False)
    ctt_pdbid = Column(String(4), nullable=False)
    ctt_type = Column(String(2), nullable=False)
    r1_name = Column(String(1), nullable=False)
    r1_position = Column(Integer, nullable=False)
    r2_name = Column(String(1), nullable=False)
    r2_position = Column(Integer, nullable=False)
    dca = Column(Float, nullable=False)

    def __init__(self, pdb, chain, tp, r1n, r1p, r2n, r2p, dca):
        self.ctt_pdbid = pdb
        self.ctt_chain = chain
        self.ctt_type = tp
        self.r1_name = r1n
        self.r1_position = r1p
        self.r2_name = r2n
        self.r2_position = r2p
        self.dca = dca


class AtomSearchBase(Base):

    __tablename__ = 'atom'

    id_atm = Column(Integer, primary_key=True)
    id_ctt = Column(Integer, ForeignKey('residue_contact.id_contact'),
                    nullable=False)
    name = Column(String(5), nullable=False)
    level = Column(String(5), nullable=False)
    bfactor = Column(Float, nullable=False)
    occupancy = Column(Float, nullable=False)
    element = Column(String(10), nullable=False)
    serial_number = Column(Integer, nullable=False)
    fullname = Column(String(10), nullable=False)
    coord = Column(String(25), nullable=False)

    def __init__(self, id_c, nm, lv, bf, oc, el, sn, fn, co):
        self.id_ctt = id_c
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co


def start_db(server, dbname, user, passwd):
    eng = 'mysql://' + user + ':' + passwd + '@' + server + '/' + dbname
    engine = create_engine(eng, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                             bind=engine))
    # Base.query = db_session.query_property()
    return db_session


if __name__ == '__main__':

    dbs = ['arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'his', 'lys', 'ser',
           'thr', 'trp', 'tyr']
    dbs_up = {}
    for db in dbs:
        dbs_up[db] = start_db('127.0.0.1', db, 'root', 'root')
