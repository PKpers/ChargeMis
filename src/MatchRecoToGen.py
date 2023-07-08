import ROOT 


## Functions 
def IsDilepton(evnt_ids, pdgid):
    '''
    Loops through the particle ids of a single event
    It returns
    True:  if the event has exactly two leptons of the specified flavor
    False: otherwise
    Arguments
    event_ids: (list) the PDGIds of a signle event
    pdgid: (int) the flavor of the lepton in question
    '''
    lep_p = 0 #number of anti leptons in each event
    lep_n = 0 #number of leptons in each evnt
    for idx, id_ in enumerate(evnt_ids) :
        if id_ == pdgid:
            lep_p +=1 # count the anti leptons
            lep_p_idx = idx # update the index if an event is dilepton then this index will not be updated
        elif id_ == -pdgid:
            lep_n += 1 # count the leptons
            lep_n_idx = idx # update the index if an event is dilepton then this index will not be updated
        else: continue
    #
    if (lep_p, lep_n) == (1, 1) :
        return (True, lep_p_idx, lep_n_idx)
    else:
        return (False, None, None)
#

def GetRecoLeptons(event):
    '''
    Takes a reconstructed dilepton event as an input 
    Returns the two leptons as TLorenz objects  
    Arguments
    event: ROOT.Tree entry
    '''
    lepton0 = ROOT.TLorentzVector()
    lepton1 = ROOT.TLorentzVector()

    Pt = event.LightLepton_Pt
    Eta = event.LightLepton_Eta
    Phi = event.LightLepton_Phi
    
    lepton0.SetPtEtaPhiM(Pt[0], Eta[0], Phi[0], 0)
    lepton1.SetPtEtaPhiM(Pt[1], Eta[1], Phi[1], 0)
    return (lepton0, lepton1)

def GetGenLeptons(event, id0, id1): 
    '''
    Takes a generator level dilepton event as input
    returns the two Leptons as TLorentz objects
    Arguments
    event: ROOT.Tree entry
    id0, id1: (int) the list indices of the two leptons of the event
    '''
    lepton0 = ROOT.TLorentzVector()
    lepton1 = ROOT.TLorentzVector()

    Pt = event.GenPart_Pt
    Eta = event.GenPart_Eta
    Phi = event.GenPart_Phi

    lepton0.SetPtEtaPhiE(Pt[id0], Eta[id0], Phi[id0], 0)
    lepton1.SetPtEtaPhiE(Pt[id1], Eta[id1], Phi[id1], 0)

    return (lepton0, lepton1)

def define_columns(num_columns, var_names, var):
    '''
    defince the variables of data frame
    '''
    import numpy as np
    vars_ = {}
    for i in range(num_columns):
        vars_[var_names[i]] = np.array(var[i])
    #
    return vars_

## Import the tree
if __name__=='__main__':
    ## Input configuration
    inPath = "/cms/multilepton-4/jvora/ULnano/Skims/05Apr23/MC/2LOS_Skim_medium_2018/"
    inFileName="Snapshot_DY_1of8.root"
    inFile = inPath + inFileName

    ## Output confuguration
    outNameMuons = "DY_1of8_Muons_Snapshot"
    outNameElectrons = "DY_1of8_Electrons_Snapshot"
    outPath = "/home/kpapad/charge_mis/out/data/"

    treeName = "skimTree"
    RFile = ROOT.TFile.Open(inFile)
    tree=RFile.Get(treeName)
    ## Event loop

    k = 0
    # Get the simulated mass from dir name. We need it to automatically set the limits of the hist
    matchedMuons = []
    for entry in tree:
        if k == 10: break
        dileptonReco = entry.LightLepton_Flavor 

        if all(d == 2 for d in dileptonReco): # Begin with reco muons 
            recoLept0, recoLept1 = GetRecoLeptons(entry)# Get the reco leptons

            for genEntry in tree: # Loop over all the gen leptons to match the reconstructed one.
                genId = genEntry.GenPart_PDGId # get the gen particle ids of each event
                dimuon, id_mup, id_mun = IsDilepton(genId, 13)
            
                match_mapping = {0: id_mup, 1: id_mun, 2: id_mup, 3: id_mun}

                if dimuon: # we are interested only in W->ll leptons
                    genLept0, genLept1 = GetGenLeptons(genEntry, id_mup, id_mun) # Get the Gen leptons
                    ## compute the possible matches
                    # The first row of the match table, contains the DeltaR between 0th reco lepton and 0th and 1st gen letpon
                    # The second row contains the DeltaR between the 1st reco lepto and the 0th and 1st gen lepton
                    # Thus, in check, the first two elements (0, 1) correspond to the matches of the 1st reco lepton
                    # if ceck[0] == True --> recoLept0 == genLept0
                    # if check[1] == True --> recoLept0 == genLept1
                    # and the last two(2, 3) to the matches of the second one. 
                    # With this in mind we can construct the mapping

                    matches = [ROOT.Math.VectorUtil.DeltaR(recoLept0, genLept) for genLept in (genLept0, genLept1)]
                    matches += [ROOT.Math.VectorUtil.DeltaR(recoLept1, genLept) for genLept in (genLept0, genLept1)] 

                    check = [m < 0.1 for m in matches] # check if any of the matches meet the criterion
                    indices = [i for i, c in enumerate(check) if c ] # store the indices of those who do.
                    matched = [match_mapping[i] for i in indices]

                    if len(matched) == 2:
                        print(matched) #file=open("/home/kpapad/charge_mis/out/data/matches.txt", "a"))
                        break
                    else: continue 

                else: continue

            print(k)
            k+=1
    #
    exit()
    

































  
