#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from scipy.spatial import distance
from Bio.PDB import PDBParser
from Bio.PDB import NeighborSearch
from contacts_filter import *


class GenerateContactsPdbFile:

    def __init__(self, pdb_file, neighborhood_size=1, chain='A'):
        # type: (str, int) -> GenerateContactsPdbFile
        self.pdb_id = treat_pdb_id(pdb_file)
        self.pdb_file = self.parser_pdb(pdb_file)
        self.nsize = neighborhood_size
        self.chain = chain
        self.messages = []

        # Residues with neighborhood measure equal to neighborhood_size
        self.res_full_neighbours = []  # [20, 32, 35, 187,...]

        # Ids of residues that are in contact:
        self.contacts = []  # [(49, 178), (20, 78), ...]
        # dict of residues where the keys is the residue id and the
        # value is a tuple with residue name and  the atoms of main chain.
        self.residues = {}  # {10: ('SER', [Atom, Atom, Atom, Atom]), ...}
        self.set_atoms_of_residue()
        self.set_residue_full_neighborhood()
        self.set_contacts()

    def parser_pdb(self, pdb_file):
        """
        Return the parser object of PDBParser.
        Arguments:
            o pdb_file - string with the pdb file path.
        """
        return PDBParser(QUIET=1).get_structure(self.pdb_id, pdb_file)

    def set_residue_full_neighborhood(self):
        for res in self.residues.keys():
            neighbors = calc_neighborhood(res, self.nsize)
            t = True
            for n in neighbors:
                if n not in self.residues.keys():
                    t = False
            if t:
                self.res_full_neighbours.append(res)

    def has_neighborhood(self, residue_id):
        return True if residue_id in self.res_full_neighbours else False

    def check_neighborhood(self, r1, r2):
        # type: (int, int) -> int
        """
        :param l1: list
        :param l2: list
        """
        l1 = calc_neighborhood(r1, self.nsize)
        l1.append(r1)
        l2 = calc_neighborhood(r2, self.nsize)
        l2.append(r2)
        tipo = 3
        if len(l1) == len(l2):
            ct = 0
            for k in l1:
                if k in l2:
                    ct += 1
            if ct == 0:
                tipo = 6
            elif ct == 1:
                tipo = 5
            else:
                tipo = 4
        return tipo

    def set_atoms_of_residue(self):
        """
            Create a dict of residues where the keys is the residue id and the
            value is a tuple with residue name and  all atoms
            self.residues = {10: ('SER', [Atom, Atom, Atom, ..., Atom]),
            11: ('HIS', [Atom, Atom, Atom, Atom]), 12: ('CYS',
             [Atom, Atom, Atom, Atom])}
        """
        for c in self.pdb_file.get_chains():
            if c.id == self.chain:
                self.chain = c
                break
        if isinstance(self.chain, basestring):
            msg = 'Chain {} not found! We used the model 0 instead.'
            self.messages.append(msg.format(self.chain))
            self.chain = self.pdb_file[0]
        for res in self.chain.get_residues():  # chain:
            rn = res.id[1]
            if res.resname not in RESIDUELIST:
                continue
            atoms = []
            for a in res:
                adc = a.__dict__
                at = None
                if 'child_dict' in adc:
                    try:
                        at = get_atom_dict(adc['selected_child'].__dict__)
                    except:
                        print("Error during parsing of PDB ID: " + self.pdb_id)
                        raise
                else:
                    at = get_atom_dict(adc)
                if at is None or at['name'].find('H') == 0:
                                # or \
                                # at['name'] not in MAINCHAIN:
                    continue
                # atoms.append(parser_atom(at))
                atoms.append(at)
            '''if len(atoms) == 4:
                # self.residues[rn] = (RESIDUEDICT[res.resname], atoms)
                self.residues[rn] = (res.resname, atoms)'''
            self.residues[rn] = (res.resname, atoms)

    def set_contacts(self):
        """
            Fill in the contact list
            self.contacts = [(id residue 1, id residue 2), (id residue 1,
            id residue 2), (id residue 1, id residue 2), ...].
            All those contacts will be search in available DBs.
        """
        model0_atoms = self.chain.get_atoms()
        atoms_pairs = NeighborSearch(list(model0_atoms)).search_all(6.1)

        for atom_pair in atoms_pairs:
            at1 = atom_pair[0]
            at2 = atom_pair[1]
            chain1 = at1.parent.parent.id
            chain2 = at2.parent.parent.id
            if chain1 != chain2:
                continue
            res_name1 = at1.parent.get_resname().rstrip().lstrip()
            res_name2 = at2.parent.get_resname().rstrip().lstrip()
            atm_name1 = at1.get_fullname().rstrip().lstrip()
            atm_name2 = at2.get_fullname().rstrip().lstrip()
            res_id1 = at1.parent.get_id()[1]  # res number
            res_id2 = at2.parent.get_id()[1]  # res number
            if res_id1 == res_id2:
                continue
            if (res_id1 == res_id2 + 3) or (res_id2 == res_id1 + 3):
                continue
            if self.check_neighborhood(res_id1, res_id2) != 6:
                continue
            if not self.has_neighborhood(res_id1) or \
                    not self.has_neighborhood(res_id2):
                continue
            if res_name1 in RESIDUELIST and res_name2 in RESIDUELIST and \
               atm_name1 == 'CA' and atm_name2 == 'CA':
                dstc = distance.euclidean(at1.coord, at2.coord)
                if 3.35 <= dstc <= 16.4:
                    if res_id1 < res_id2 and (res_id1, res_id2) \
                       not in self.contacts:
                        self.contacts.append((res_id1, res_id2))
                    elif res_id2 < res_id1 and (res_id2, res_id1) \
                            not in self.contacts:
                        self.contacts.append((res_id2, res_id1))
                    else:
                        continue

    def get_neighborhood_residue(self, r_id):
        nbh = calc_neighborhood(r_id, self.nsize)
        nbh.append(r_id)
        nbh = sorted(nbh)
        return nbh


if __name__ == "__main__":
    gc = GenerateContactsPdbFile('upload/4iid.pdb')
    for ctc in gc.contacts:
        print (ctc)
        print(gc.residues[ctc[0]][0], gc.residues[ctc[1]][0])
        '''for a in gc.residues[ctc[0]][1]:
            print type(a), a
        print(gc.residues[ctc[1]][0])
        for a in gc.residues[ctc[1]][1]:
            print type(a), a'''
