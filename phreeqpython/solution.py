import re
import numbers

class Solution(object):
    """ PhreeqPy Solution Class """

    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.factor = 1
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_solution(self.number)

    def add(self, element, mmol):
        self.pp.change_solution(self.number, {element:mmol})
    def remove(self, element, mmol):
        mmol = -mmol
        self.pp.change_solution(self.number, {element:mmol})
    def remove_fraction(self, species, fraction):
        current = self.total(species)
        to_remove = 1000 * current * fraction
        self.remove(species, to_remove)

    # this function can precipitate and dissolve!
    def saturate(self, phase, to_si=0, partial_pressure = 10):
        self.pp.equalize_solution(self.number, phase, to_si, partial_pressure)

    # this function can only precipitate
    def desaturate(self, phase, to_si=0):
        self.pp.equalize_solution(self.number, phase, to_si, 0)

    # change the ph
    def change_ph(self, to_pH, with_chemical=None):
        # default to NaOH and HCl
        if not with_chemical:
            if to_pH < self.pH:
                # dose HCl to lower pH
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "HCl")
            else:
                # dose NaOH to raise pH
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "NaOH")
        else:
            self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, with_chemical)

    def change_temperature(self, to_temperature):
        self.pp.change_solution_temperature(self.number, to_temperature)

    def total(self, element):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species.iteritems():
            if re.search(regexp, species):
                total += amount
        return total

    def total_element(self, element):
        """ Returns to total any given element (FAST!) """
        return self.pp.ip.get_total_element(self.number, element)

    def tacc(self,temperature=90):
        """ Calculate the Calcium Carbonate Precipitation Potential (CCPP)"""
        # create temporary solution
        tmp = self.copy()
        # raise temperature
        tmp.change_temperature(temperature)
        ca_pre = tmp.total_element('Ca')
        # use saturate instead of desaturate to allow dissolution in addition to precipitation
        tmp.saturate('Calcite',0.0)
        # calculate tacc
        tacc = ca_pre - tmp.total_element('Ca')
        # cleanup
        self.pp.remove_solutions([tmp.number])
        return tacc * 1000 #mmol

    def si(self, phase):
        """ Calculate the TACC """
        return self.pp.ip.get_si(self.number, phase)

    def forget(self):
        """ remove this solution from VIPhreeqc memory """
        self.pp.remove_solutions([self.number])


    # Magic functions
    def __add__(self, other):
        """ add two solutions """
        if not isinstance(other,Solution):
            raise TypeError("Invalid operation, only addition of two solutions is allowed")
        mixture= {self:self.factor, other:other.factor}
        #print mixture
        mixture = self.pp.mix_solutions({self:self.factor,other:other.factor})
        # reset factors to 1
        self.factor = 1
        other.factor = 1

        return mixture

    def __div__(self, other):
        """ set devision factor """
        if not isinstance(other,numbers.Real):
            raise TypeError("Invalid operation, only divisiion by a number is allowed")
        self.factor = 1/float(other)
        return self

    def __mul__(self, other):
        """ set multiplication factor """
        if not isinstance(other,numbers.Real):
            raise TypeError("Invalid operation, only divisiion by a number is allowed")
        self.factor = float(other)
        return self

    # Accessor methods
    @property
    def pH(self):
        return self.pp.ip.get_ph(self.number)
    @property
    def sc(self):
        return self.pp.ip.get_sc(self.number)
    @property
    def temperature(self):
        return self.pp.ip.get_temperature(self.number)
    @property
    def mass(self):
        return self.pp.ip.get_mass(self.number)
    @property
    def pe(self):
        return self.pp.ip.get_pe(self.number)
    @property
    def phases(self):
        return self.pp.ip.get_phases_si(self.number)
    @property
    def elements(self):
        return self.pp.ip.get_elements_totals(self.number)
    @property
    def species(self):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_moles(self):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_molalities(self):
        return self.pp.ip.get_species_moles(self.number)

    # vitens TACC90 calculation
    @property
    def tacc90(self):
        return self.tacc(90)

