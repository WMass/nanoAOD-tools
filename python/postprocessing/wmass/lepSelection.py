import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class leptonSelection(Module):
    def __init__(self):
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("GenPart_bareMuonIdx", "I");
        self.out.branch("GenPart_preFSRMuonIdx", "I");
        self.out.branch("GenPart_NeutrinoIdx", "I");
        self.out.branch("GenDressedLepton_dressMuonIdx", "I");
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        ############################################## bare and preFSR muon selection from GenPart collection
        genParticles = Collection(event, "GenPart")

        baremuons =[]
        neutrinos =[]
        myIdx = -99
        myNuIdx = -99
        
        for i,g in enumerate(genParticles) :
            if not ((g.statusFlags & (1 << 0)) and g.status==1 ): continue
            if abs(g.pdgId)==13: baremuons.append((i,g))# muon is prompt
            if abs(g.pdgId)==14: neutrinos.append((i,g)) # neutrino is prompt
            

        #take the most energetic ones in case there are more than 1 muon and/or neutrino
        if len(baremuons)>0:
            baremuons.sort(key = lambda x: x[1].pt, reverse=True ) #order by pt in decreasing order
            neutrinos.sort(key = lambda x: x[1].pt, reverse=True )
            myIdx = baremuons[0][0]
            myNuIdx = neutrinos[0][0]

        else: return False #keep control on bare muon only for now

        self.out.fillBranch("GenPart_bareMuonIdx",myIdx)
        self.out.fillBranch("GenPart_NeutrinoIdx", myNuIdx);
        
        muons =[]
        myIdx = -99
        
        for i,g in enumerate(genParticles) :
            if abs(g.pdgId)==13 and g.status==1 and (g.statusFlags & (1 << 8)): muons.append((i,g)) # muon is fromHardProcess

        if len(muons)>0:
            muons.sort(key = lambda x: x[1].pt, reverse=True ) #order by pt in decreasing order
            myIdx = muons[0][0]
            myMuon = genParticles[myIdx]
            
            if myMuon.genPartIdxMother > 0:
                while (genParticles[myMuon.genPartIdxMother].pdgId == myMuon.pdgId): # the muon has a muon as mother
                    if (genParticles[myMuon.genPartIdxMother].statusFlags & (1 << 14)): # muon is LastCopyBeforeFSR
                        myIdx = myMuon.genPartIdxMother
                        break
                    
                    myMuon = genParticles[myMuon.genPartIdxMother]
                    if myMuon.genPartIdxMother < 0:
                        break 
                    
        self.out.fillBranch("GenPart_preFSRMuonIdx",myIdx)

        ############################################## dressed muon selection from GenDressedLepton collection
        genDressedLeptons = Collection(event,"GenDressedLepton")

        myIdx = -99
        dressmuons = []
        for i,l in enumerate(genDressedLeptons) :
            if abs(l.pdgId)==13: dressmuons.append((i,l))
        
        if len(dressmuons)>0:
            dressmuons.sort(key = lambda x: x[1].pt, reverse=True ) #order by pt in decreasing order
            myIdx = dressmuons[0][0]

        self.out.fillBranch("GenDressedLepton_dressMuonIdx",myIdx)

        
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

leptonSelectModule = lambda : leptonSelection() 
 