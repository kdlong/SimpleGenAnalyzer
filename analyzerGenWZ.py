#!/bin/env python
import os
import sys
from itertools import combinations
import argparse
from utilities.GenEvent import *
import utilities.CutTracker as CutTracker

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ZMASS = 91.1876
#    def pass_preselection(self, rtrow):
#        '''
#        Wrapper for preselection defined by user.
#        '''
#        if 'preselection' in self.cache: return self.cache['preselection']
#        cuts = self.preselection(rtrow)
#        cutResults,self.num = cuts.evaluate(rtrow)
#        self.cache['preselection'] = cutResults
#        return cutResults
#
#    def pass_selection(self,rtrow):
#        '''
#        Wrapper for the selection defined by the user (tight selection whereas preselection
#        is the loose selection for fake rate method).
#        '''
#        if 'selection' in self.cache: return self.cache['selection']
#        cuts = self.selection(rtrow)
#        cutResults,self.num = cuts.evaluate(rtrow)
#        self.cache['selection'] = cutResults
#        return cutResults

class AnalyzerGenWZ(object):
    def __init__(self, root_file_name):
        self.root_file = rtFile = ROOT.TFile(root_file_name)

        self.cut_sequence = CutTracker.CutSequence()
        self.cut_sequence.add(self.fiducial, "Fiducial + loose p_{T}")
        self.cut_sequence.add(self.trigger, "Trigger")
        self.cut_sequence.add(self.mass3l, "3l Mass")
        self.cut_sequence.add(self.zSelection, "Z Mass")
        self.cut_sequence.add(self.wSelection, "W selection")
        self.cut_tracker = CutTracker.CutTracker(self.cut_sequence)
    def track_event(self, event, event_id):
        self.cut_tracker.track_event(event, event_id)
    def store_events(self):
        self.cut_tracker.store_cutflow()
    def print_cutflow(self):
        self.cut_tracker.Print()
    def fiducial(self, event):
        keep = []
        ptCut = 10
        eEta = 2.5
        mEta = 2.4
        for lepton in event.getLeptons():
            etaCut = eEta if abs(lepton.getPdgID()) == 11 else mEta 
            if lepton.Pt() < ptCut:
                continue
            if lepton.Eta() > etaCut:
                continue
            keep.append(lepton)
        
        self.leptons = keep
        return len(self.leptons) > 2
    def mass3l(self, event): 
        #print "3l Mass is %f" % event.get3lMass()
        return event.get3lMass() > 100
    def zSelection(self, event):
        Zcand = event.getZcand()
        #print "Z Mass is %f" % Zcand.M()
        return abs(Zcand.M() - ZMASS) < 20 
    def wSelection(self, event):
        return event.getMET() > 30 and event.getWLepton().Pt() > 20
    def trigger(self, event):
        leptons = event.getLeptons()
        foundEPt12 = False
        foundEPt23 = False
        foundMuPt8 = False
        foundMuPt17 = False
        foundMuPt23 = False

        for lepton in leptons:
            if abs(lepton.getPdgID()) == 11:
                if lepton.Pt() > 23 and not foundEPt23:
                    foundEPt23 = True
                elif lepton.Pt() > 12 and not foundEPt12:
                    foundEPt12 = True
            elif abs(lepton.getPdgID()) == 13:
                if lepton.Pt() > 23 and not foundMuPt23:
                    foundMuPt23 = True
                elif lepton.Pt() > 17 and not foundMuPt17:
                    foundMuPt17 = True
                elif lepton.Pt() > 8:
                    foundMuPt8 = True
        return (foundMuPt17 and foundMuPt8) or \
               (foundEPt23 and foundEPt12) or \
               (foundMuPt8 and foundEPt23) or \
               (foundMuPt23 and foundEPt12)
    def write_events(self, branches):
        ntupleEntry = {}
        for i, lepton in enumerate(self.leptons):
            if i > 3:
                break
            pdgid = lepton.getPdgID()
            obj = "e" if abs(pdgid) == 11 else "m"
            ntupleEntry["l%i.Pt" % (i+1)] = lepton.Pt()
            ntupleEntry["l%i.Eta" % (i+1)] = lepton.Eta()
            ntupleEntry["l%i.Phi" % (i+1)] = lepton.Phi()
            ntupleEntry["l%i.Chg" % (i+1)] = -1 if pdgid < 0 else 1
            ntupleEntry["l%iFlv.Flv" % (i+1)] = obj  

        for key,val in ntupleEntry.iteritems():
            branch, var = key.split('.')
            setattr(branches[branch],var,val)
    def analyze(self):
        tree = self.root_file.Get("demo/Ntuple")

    #    outfile = ROOT.TFile("genWZ.root", 'recreate')
    #    final_states = ['eee','eem','emm','mmm']
    #    initial_states = ['z1','w1'] # in order of leptons returned in choose_objects
    #    object_definitions = {
    #        'w1': ['em','n'],
    #        'z1': ['em','em'],
    #    }
    #    ntuple, branches = buildNtuple(object_definitions,initial_states,'WZ',final_states)

        event = GenEvent()
        numEvents = tree.GetEntries()
        for row in range(numEvents):
            event.reset()
            tree.GetEntry(row)
            for i, pdgid in enumerate(tree.pdgId):
                if abs(pdgid) in [11, 13]:
                    event.foundLepton(pdgid,
                        tree.pt[i],
                        tree.eta[i],
                        tree.phi[i],
                        tree.mass[i])
                if abs(pdgid) in [12, 14, 16]:
                    event.foundMET(tree.pt[i],
                        tree.eta[i],
                        tree.phi[i],
                        tree.mass[i])
            self.track_event(event, row)
        self.store_events()
            #event.Print()
        self.print_cutflow()    
    #    outfile.Write()
#        outfile.Close()

def main():
    args = getComLineArgs()
    analyzer = AnalyzerGenWZ(args["root_file"])
    analyzer.analyze()

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("root_file", type=str,
                        help="Root file with Ntuple to run analysis on")
    return vars(parser.parse_args())
if __name__ == "__main__":
    status = main()
    sys.exit(status)
