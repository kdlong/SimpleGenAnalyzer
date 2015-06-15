from itertools import combinations
import argparse
import ROOT

ZMASS = 91.1876

class ParticleVector(ROOT.TLorentzVector):
    def __init__(self, pdgid):
        self.pdgid = pdgid
        super(ParticleVector, self).__init__()
    def getPdgID(self):
        return self.pdgid
class GenEvent(object):
    def __init__(self):
        self.leptons = []
        self.MET = ROOT.TLorentzVector()
        self.WLepton = ROOT.TLorentzVector()
    def reset(self):
        self.leptons = []
    def foundLepton(self, pdgid, pt, eta, phi, mass):
        lepton = ParticleVector(pdgid)
        lepton.SetPtEtaPhiM(pt, eta, phi, mass)
        self.leptons.append(lepton)
    def foundMET(self, pt, eta, phi, mass):
        nu = ROOT.TLorentzVector()
        nu.SetPtEtaPhiM(pt, eta, phi, mass)
        self.MET += nu
    def getMET(self):
        return self.MET.Pt()
    def getZcand(self):
        MASS_DIFF_CUT = 20
        Zcand = ParticleVector(-1)
        lepsNoZ = list(self.leptons)
        for lepton_pair in combinations(self.leptons, 2):
            (l1, l2) = lepton_pair
            if l1.getPdgID() + l2.getPdgID() != 0:
                continue
            massDiff = abs((l1 + l2).M() - ZMASS) 
            if massDiff < abs(Zcand.M() - ZMASS):
                Zcand = l1 + l2
                lepsNoZ = list(self.leptons)
                lepsNoZ.remove(l1)
                lepsNoZ.remove(l2)
        lepsNoZ.sort(key=lambda x: x.Pt())
        if len(lepsNoZ) > 0:
            self.WLepton = lepsNoZ[0]
        return Zcand
    def getLeptons(self):
        self.leptons.sort(key=lambda x: x.Pt())
        return self.leptons
    def get3lMass(self):
        if len(self.leptons) < 3:
            return 0
        Zcand = self.getZcand()
        return (Zcand + self.WLepton).M()
    def getWLepton(self):
        return self.WLepton
    def Print(self):
        print "---------------------------------------------"
        print "Num leptons is %i" % len(self.leptons)

