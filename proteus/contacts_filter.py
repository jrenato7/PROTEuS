#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Bio.PDB.Residue import Residue
from Bio.PDB.Chain import Chain
from Bio.PDB.Atom import Atom
from Bio.PDB import PDBIO
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import db_protein_align_model as pam
import numpy as np
import os


RESIDUELIST = ['ALA', 'ARG', 'ASP', 'ASN', 'CYS', 'GLU', 'GLN', 'GLY', 'HIS',
               'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP',
               'TYR', 'VAL']

RESIDUEDICT = {'ALA': 'A', 'ARG': 'R', 'ASP': 'D', 'ASN': 'N', 'CYS': 'C',
               'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
               'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
               'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}

RESIDUEDICT2 = {'A': 'ALA', 'R': 'ARG', 'D': 'ASP', 'N': 'ASN', 'C': 'CYS',
                'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE',
                'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO',
                'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL'}

ATOMLIST_old = ['C', 'CA', 'CB', 'CD', 'CD1', 'CD2', 'CE', 'CE1', 'CE2', 'CE3',
                'CG', 'CG1', 'CG2', 'CH2', 'CZ', 'CZ2', 'CZ3', 'N', 'ND1',
                'ND2', 'NE', 'NE1', 'NE2', 'NH1', 'NH2', 'NZ', 'O', 'OXT',
                'OD1', 'OD2', 'OE1', 'OE2', 'OG', 'OG1', 'OH', 'SD', 'SG']

ATOMLIST = ['OH', 'NE1', 'OG', 'OG1', 'ND2', 'NE2', 'OE1', 'SG', 'NZ', 'NE',
            'NH1', 'NH2', 'ND1', 'OD1', 'OD2', 'OE2', 'CZ', 'CD2', 'CE1',
            'CG', 'CD', 'SD']

G2 = ['TYROH', 'TRPNE1', 'SEROG', 'THROG1', 'ASNND2', 'ASNOD1', 'GLNNE2',
      'GLNOE1']
G3 = ['CYSSG']
G4 = ['LYSNZ', 'ARGNE', 'ARGNH1', 'ARGNH2', 'HISND1', 'HISNE2']
G5 = ['ASPOD1', 'ASPOD2', 'GLUOE1', 'GLUOE2']

ACCEPTOR_FILTER = ['ALAN', 'ARGN', 'ASNN', 'ASPN', 'CYSN', 'VALN', 'GLNN',
                   'GLUN', 'GLYN', 'HISN', 'ILEN', 'LEUN', 'LYSN', 'METN',
                   'PHEN', 'SERN', 'THRN', 'TRPN', 'TYRN']

DONOR_FILTER = ['ALAO', 'ARGO', 'ASNO', 'ASPO', 'CYSO', 'GLNO', 'GLUO', 'GLYO',
                'HISO', 'ILEO', 'LEUO', 'LYSO', 'METO', 'PHEO', 'PROO', 'SERO',
                'THRO', 'TRPO', 'TYRO', 'VALO']

# hydrogenbond = Grupos G2 a G5

# positive charge
CATION_FILTER = ['ARGCZ', 'HISCD2', 'HISCE1', 'HISCG']

# negative charge
ANION_FILTER = ['ASPCG', 'ASPOD1', 'ASPOD2', 'GLUCD']

# AROMATIC = nope

DISULPHIDE_FILTER = ['CYSSG', 'METSD']

MAINCHAIN = ["N", "CA", "C", "O"]


def parser_atom(a):
    # type: (dict) -> Bio.PDB.Atom
    """
        :param a: dict with atoms fields
        :return: Objeto Atom da classe Bio.PDB.Atom.Atom
    """

    crd = a.coord.replace("[", "").replace("]", "")
    crd = crd.split(',') if crd.find(';') == -1 else crd.split(';')
    coord = np.array(map(lambda x: round(float(x), 3), crd))
    try:
        atm = Atom(str(a.name), coord, round(float(a.bfactor), 2),
                   round(float(a.occupancy), 2), ' ', str(a.fullname),
                   int(a.serial_number), element=str(a.element))
    except:
        atm = None
    return atm


def get_full_residue(g, r_id, type=1, atms=[]):
    """
    :param r_id: id of residue
    :param type: Atom.type: 1 = main chain, 0 = side chain
    :return: Residue with atoms
    """
    res = g.query(pam.ResidueAlign)\
           .filter(pam.ResidueAlign.res_id == r_id)\
           .first()
    '''if type == 1:
        atms = g.query(pam.AtomAlign)\
                .filter(pam.AtomAlign.res_id == r_id)\
                .filter(pam.AtomAlign.type == type)\
                .order_by(pam.AtomAlign.serial_number)
    else:
        atms = g.query(pam.AtomAlign)\
                .filter(pam.AtomAlign.res_id == r_id)\
                .order_by(pam.AtomAlign.serial_number)'''
    atml = []
    for a in atms:
        atml.append(parser_atom(a))
    pos = int(res.position)
    res_return = Residue((' ', pos, ' '),
                         RESIDUEDICT2[res.name], pos)
    for a in atml:
        res_return.add(a)

    return res_return


def create_mutate_pdb(rc_id, out_file, tp=0, atms=[]):
    dbuser = os.environ.get("FULLDBUSER", "")
    dbpass = os.environ.get("FULLDBPASS", "")
    dbhost = os.environ.get("HOSTDB", "")
    eng = 'mysql://%s:%s@%s/protein_align' % (dbuser, dbpass, dbhost)
    engine = create_engine(eng, convert_unicode=True)
    g = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                    bind=engine))
    rc = g.query(pam.ResidueContactAlign)\
          .filter(pam.ResidueContactAlign.id_contact == rc_id)\
          .first()
    ch = g.query(pam.ChainAlign).filter(pam.ChainAlign.id_c == rc.id_c)\
          .first()
    try:
        chain = Chain(str(ch.name))
        chain.add(get_full_residue(g, rc.r1_prv, atms=atms[0:4]))
        chain.add(get_full_residue(g, rc.r1_id, tp, atms=atms[4:8]))
        chain.add(get_full_residue(g, rc.r1_nxt, atms=atms[8:12]))
        chain.add(get_full_residue(g, rc.r2_prv, atms=atms[12:16]))
        chain.add(get_full_residue(g, rc.r2_id, tp, atms=atms[16:20]))
        chain.add(get_full_residue(g, rc.r2_nxt, atms=atms[20:24]))

        w = PDBIO()
        w.set_structure(chain)
        w.save(out_file)
    except:
        out_file = None
    g.close()
    return out_file


def get_atom_dict(at):
    # type: (Atom) -> dict
    ret = {}
    coord = "[%.3f; %.3f; %.3f]" % (at['coord'][0],
                                    at['coord'][1],
                                    at['coord'][2])
    ret['name'] = at['name']
    ret['level'] = at['level']
    ret['bfactor'] = "%.2f" % (at['bfactor'])
    ret['occupancy'] = "%.2f" % (at['occupancy'])
    ret['element'] = at['element']
    ret['coord'] = coord
    ret['serial_number'] = at['serial_number']
    ret['fullname'] = at['fullname']
    return ret


def treat_pdb_id(pdb_id):
    # type: (str) -> str
    '''
    :param file upload:
    :return: pdbid or the first part of upload file.
    '''
    return pdb_id.replace(".pdb", "").replace(".ent", "")


def calc_neighborhood(residue_id, neighborhood_size):
    # type: (int, int) -> list
    ret = []
    for i in range(neighborhood_size, 0, -1):
        ret.append(residue_id + i)
        ret.append(residue_id - i)
    return ret


def prepare_res_align_aux(r, gc):
    # type (int, GenerateContactsPdbFile) -> list
    full_n = gc.get_neighborhood_residue(r)
    lst = []
    for fn in full_n:
        if fn == r:
            lst.append(gc.residues[fn][1])
        else:
            tmp = []
            for rngb in gc.residues[fn][1]:
                if rngb['name'] in MAINCHAIN:
                    tmp.append(rngb)
            lst.append(tmp)
    return lst


def prepare_res_align(gc):
    # type (GenerateContactsPdbFile) -> dict
    """
    :param gc: object of GenerateContactsPdbFile class.
    :return:dict key = residue_id; value = list atoms of triple.
    [[Atom N, Atom CA, Atom C, Atom O], [Atom N,
    Atom CA, Atom C, Atom O], [Atom N, Atom CA, Atom C,
    Atom O]]
    """
    dict_ret = {}
    for ctc in gc.contacts:
        if ctc[0] not in dict_ret:
            ret = prepare_res_align_aux(ctc[0], gc)
            if len(ret) > 0:
                dict_ret[ctc[0]] = ret[:]
        if ctc[1] not in dict_ret:
            ret2 = prepare_res_align_aux(ctc[1], gc)
            if len(ret2) > 0:
                dict_ret[ctc[1]] = ret2[:]
    return dict_ret


def is_hydrogen_bond(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if ((res_atom_name_1 in G2) and (res_atom_name_2 in G2) or
        (res_atom_name_1 in G3) and (res_atom_name_2 in G3) or
        (res_atom_name_1 in G4) and (res_atom_name_2 in G4) or
        (res_atom_name_1 in G5) and (res_atom_name_2 in G5) or
        (res_atom_name_1 in G2) and (res_atom_name_2 in G4) or
        (res_atom_name_1 in G4) and (res_atom_name_2 in G2) or
        (res_atom_name_1 in G2) and (res_atom_name_2 in G5) or
        (res_atom_name_1 in G5) and (res_atom_name_2 in G2) or
        (res_atom_name_1 in G4) and (res_atom_name_2 in G5) or
        (res_atom_name_1 in G5) and (res_atom_name_2 in G4)) and \
            dtc < 3.50:
        return True
    else:
        return False


def is_attractive(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if ((res_atom_name_1 in CATION_FILTER) and (res_atom_name_2 in ANION_FILTER) or
                (res_atom_name_1 in ANION_FILTER) and (res_atom_name_2 in CATION_FILTER)) and \
                    dtc < 6.00:
        return True
    else:
        return False


def is_repulsive(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if ((res_atom_name_1 in CATION_FILTER) and (res_atom_name_2 in CATION_FILTER) or
                (res_atom_name_1 in ANION_FILTER) and (res_atom_name_2 in ANION_FILTER)) and \
                    dtc < 6.00:
        return True
    else:
        return False


def is_disulphide(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if res_atom_name_1 in DISULPHIDE_FILTER \
            and res_atom_name_2 in DISULPHIDE_FILTER and \
                    dtc < 2.08:
        return True
    else:
        return False
