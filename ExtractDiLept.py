import ROOT
import numpy as np

def getPtEtaPhiMCharge(event):
    '''
    Takes a dilepton event as an input 
    Returns a list of the Pts etas and phis 
    of the two leptons
    Returns the invariant mass of the pair.
    Arguments
    entry: ROOT.Tree entry
    '''
    lepton0 = ROOT.TLorentzVector()
    lepton1 = ROOT.TLorentzVector()
    
    Pt = event.LightLepton_Pt
    Eta = event.LightLepton_Eta
    Phi = event.LightLepton_Phi
    Charge = event.LightLepton_Charge
    
        
    PtEtaPhiCharge = [
        Pt[0], Eta[0], Phi[0], Charge[0],
        Pt[1], Eta[1], Phi[1], Charge[1]
    ]
    
    lepton0.SetPtEtaPhiM(Pt[0], Eta[0], Phi[0], 0)
    lepton1.SetPtEtaPhiM(Pt[1], Eta[1], Phi[1], 0)

    dilepton_pair = lepton0 + lepton1
    dileptonMass = dilepton_pair.M()
    return PtEtaPhiCharge, dileptonMass

def define_branches(num_branches, branch_names, var):
    '''
    Define the branches of data frame
    Returns a dictionary, {branch1: nparray(...), ...}
    Args
    num_branches:(int) number of branches
    branch_name:(str) branch names
    var:(any ROOT compatible array form) the content of each branch
    '''
    import numpy as np
    vars_ = {}
    for i in range(num_branches):
        vars_[branch_names[i]] = np.array(var[i])
    #
    return vars_

if __name__=="__main__":
    ## Input configuration
    inDir = "/cms/multilepton-4/jvora/ULnano/Skims/05Apr23/MC/2LOS_Skim_medium_2018/"
    inFileName="Snapshot_DY_1of8.root"
    #inDir = "/cms/multilepton-4/anton/ULnano/Skims/16June23/2LOS_Skim_medium_2018/"
    #inFileName = "/Snapshot_Data_1of14.root"

    inFile = inDir + inFileName
    treeName="skimTree"
    RFile = ROOT.TFile.Open(inFile)
    tree=RFile.Get(treeName)

    ## Output configuration
    outFileName = "DY_1of8" # Simulation
    #outFileName = "Data_1of14" # Real data
    #outFilePath = '/home/kpapad/UG_thesis/Thesis/Analysis/out/Data/' 

    ## Event loop
    muons = list()
    electrons = list()

    muon_mass_hist = ROOT.TH1D("muon_mass_hist", "", 50,0, 1000) 
    electron_mass_hist = ROOT.TH1D("electron_mass_hist", "", 50,0, 1000) 
    k = 0
    e = 0
    for entry in tree:
        #if k ==10: break
        dilepton = entry.LightLepton_Flavor 
        coords, mass = getPtEtaPhiMCharge(entry)
    
        if all(d == 2 for d in dilepton): # True if dilepton = {2, 2}
            muons.append(coords)
            muon_mass_hist.Fill(mass)
        
        elif all(d == 1 for d in dilepton): # True if dilepton = {1,1}
            electrons.append(coords)
            electron_mass_hist.Fill(mass)
        
        else: continue
        #k += 1
    #
    muon_mass_hist.SetDirectory(0)
    electron_mass_hist.SetDirectory(0)
    RFile.Close()

    ## Writing the dimuon invariant mass histogram to a root file 
    outHistMuons = ROOT.TFile.Open(outFileName+'_MuonsHist.root' ,"RECREATE")
    outHistMuons.cd()
    print('Writing {} to {}'.format('dimuon mass hist', outFileName+'_MuonsHist.root'))
    muon_mass_hist.Write()
    outHistMuons.Close()

    ## Writing the dielectron invariant mass histogram to a root file 
    outHistElectrons = ROOT.TFile.Open(outFileName+'_ElectronsHist.root' ,"RECREATE")
    outHistElectrons.cd()
    print('Writing {} to {}'.format('dielectron mass hist', outFileName+'_ElectronsHist.root'))
    electron_mass_hist.Write()
    outHistElectrons.Close()

    ## Write the coordinates and Charge to a root file
    tree_name = "myTree"
    myTree = ROOT.TTree(treeName, treeName)
    num_branches_mu= len(muons[0])
    num_branches_el= len(electrons[0])
    #
    bn= [
        ['Pt'+str(i), 'Eta'+str(i), 'Phi'+str(i), 'Charge'+str(i)]
        for i in (1,2)
    ]
    branchName= bn[0]+bn[1]

    muons = np.array(muons, dtype=np.float32).T # from [[event 1], [event2], ...] to [[px], [py], ...]]
    electrons = np.array(electrons, dtype=np.float32).T
    branches_mu = define_branches(num_branches_mu, branchName, muons)
    branches_el = define_branches(num_branches_el, branchName, electrons)

    fNameSuffix = ("_mu", "_el")
    for i, branch in enumerate([branches_mu, branches_el]):
        print('Writing {} to {} at {}'.format(branchName, tree_name, outFileName+'_Vars{}.root'.format(fNameSuffix[i])))
        df = ROOT.RDF.MakeNumpyDataFrame(branch)\
                    .Snapshot('tree', outFileName+'_Vars{}.root'.format(fNameSuffix[i]))



