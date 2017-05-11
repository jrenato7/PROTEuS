#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from Bio.PDB.Atom import Atom
from search_db_model_base import start_db
import numpy as np


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


def connect_dbs(graphs, dbs, ip_base, passwd_base, user):
    for db in dbs:
        try:
            graphs[db] = start_db(ip_base, db, user, passwd_base)

        except:
            print "Database %s isn't up!" % db
    return graphs


def get_available_dbs(graphs={}):
    # type: () -> dict
    # Return the available contacts databases (C.D.N.s)
    #dbs_101 = ['arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'his', 'lys', 'ser',
    #           'thr', 'trp', 'tyr']
    dbs_101 = ['cys']
    # dbs_101 = ['thr']
    ip_101 = "127.0.0.1"  # '150.164.203.92'
    passwd_101 = "root"  # 'rootlbspdbc0nt1cts'
    user_101 = "root"  # 'prtaln'
    graphs = connect_dbs(graphs, dbs_101, ip_101, passwd_101, user_101)
    return graphs


def get_atom_dict(at):
    # type: (Atom) -> dict
    ret = {}
    coord = "[%.3f, %.3f, %.3f]" % (at['coord'][0],
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
    if ((res_atom_name_1 in CATION_FILTER) and
            (res_atom_name_2 in ANION_FILTER) or
            (res_atom_name_1 in ANION_FILTER) and
            (res_atom_name_2 in CATION_FILTER)) and dtc < 6.00:
        return True
    else:
        return False


def is_repulsive(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if ((res_atom_name_1 in CATION_FILTER) and
            (res_atom_name_2 in CATION_FILTER) or
            (res_atom_name_1 in ANION_FILTER) and
            (res_atom_name_2 in ANION_FILTER)) and dtc < 6.00:
        return True
    else:
        return False


def is_disulphide(res_atom_name_1, res_atom_name_2, dtc):
    # type: (str, str, float) -> bool
    if res_atom_name_1 in DISULPHIDE_FILTER \
            and res_atom_name_2 in DISULPHIDE_FILTER and dtc < 2.08:
        return True
    else:
        return False
