#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PdbFile(Base):

    __tablename__ = 'pdb_file'

    pdbid = Column(String(4), primary_key=True)
    resolution = Column(Float(precision=2))
    structure_method = Column(Integer)

    def __init__(self, pdbid, resolution, sm):
        self.pdbid = pdbid
        self.resolution = resolution
        self.structure_method = sm


class ChainAlign(Base):

    __tablename__ = 'chain'

    id_c = Column(String(15), primary_key=True)
    name = Column(String(1))
    pdbid = Column(String(4), ForeignKey('pdb_file.pdbid'))

    def __init__(self, id, name, pdbid):
        self.id_c = id
        self.name = name
        self.pdbid = pdbid


class ResidueAlign(Base):

    __tablename__ = 'residue'

    res_id = Column(String(15), primary_key=True)
    id_c = Column(String(15), ForeignKey('chain.id_c'))
    name = Column(String(1))
    position = Column(Integer)

    def __init__(self, id, name, position):
        self.id_c = id
        self.name = name
        self.position = position


class ResidueContactAlign(Base):

    __tablename__ = 'residue_contact'

    id_contact = Column(Integer, primary_key=True)
    id_c = Column(String(15), nullable=False)
    ctt_atoms = Column(String(10), nullable=False)
    ctt_type = Column(String(2), nullable=False)
    ctt_distance = Column(Float(precision=2), nullable=False)
    ctt_p = Column(Integer)  # used when the ctt is in process
    r1_id = Column(String(15), nullable=False)
    r1_name = Column(String(1), nullable=False)
    r1_position = Column(Integer, nullable=False)
    r1_prv = Column(String(15), nullable=False)
    r1_nxt = Column(String(15), nullable=False)
    r2_id = Column(String(15), nullable=False)
    r2_name = Column(String(1), nullable=False)
    r2_position = Column(Integer, nullable=False)
    r2_prv = Column(String(15), nullable=False)
    r2_nxt = Column(String(15), nullable=False)

    def __init__(self, chain, atm, tp, dst, r1id, r1n, r1p, r1pv, r1nx,
                 r2id, r2n, r2p, r2pv, r2nx, prc=0):
        self.id_c = chain
        self.ctt_atoms = atm
        self.ctt_type = tp
        self.ctt_distance = dst
        self.ctt_p = prc
        self.r1_id = r1id
        self.r1_name = r1n
        self.r1_position = r1p
        self.r1_prv = r1pv
        self.r1_nxt = r1nx
        self.r2_id = r2id
        self.r2_name = r2n
        self.r2_position = r2p
        self.r2_prv = r2pv
        self.r2_nxt = r2nx


class AtomAlign(Base):

    __tablename__ = 'atom'

    id_atm = Column(Integer, primary_key=True)
    res_id = Column(String(15))
    type = Column(Integer)
    name = Column(String(5))
    level = Column(String(5))
    bfactor = Column(Float)
    occupancy = Column(Float)
    element = Column(String(10))
    serial_number = Column(Integer)
    fullname = Column(String(10))
    coord = Column(String(35))

    def __init__(self, res_id, type, nm, lv, bf, oc, el, sn, fn, co):
        self.res_id = res_id
        self.type = type
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co


class Align(Base):

    __tablename__ = 'align'

    id_ali = Column(Integer, primary_key=True)
    ctt_begin = Column(Integer)
    ctt_end = Column(Integer)
    rmsd = Column(Float(precision=3))
    name = Column(String(2))
    ngb_size = Column(Integer)

    def __init__(self, ctt_b, ctt_e, score, type, ngb=1):
        self.ctt_begin = ctt_b
        self.ctt_end = ctt_e
        self.rmsd = score
        self.name = type
        self.ngb_size = ngb

