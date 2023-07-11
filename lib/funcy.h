// Helper FUNctions in C for pYroot
#ifndef FUNCY_H
#define FUNCY_H


using namespace ROOT::VecOps;
using namespace ROOT::Math;
using namespace std;

bool Filter_GetRecoDilepton(const RVec<int>& dilepton, int flavor) {

    // Accepts only reco dilepton events of a specific  flavor
    // Arguments
    // - dilepton: (RVec) vector containing the flavour of dileptons in an event  
    // - flavor: (int) Target flavor

    bool result = true;
    for (int d : dilepton) {
        if (d != flavor) {
            result = false;
            break;
        }
    }
    return result;
}

bool Filter_GetGenDilepton(const RVec<int>& evnt_ids, int PDGId) {

    // Same as functionality as GetrecoDilepton but for gen events
    // Arguments:
    // - event_ids: (RVec) vector of PDGIds present in an event
    // -PDGID: (int) target PDGId 

    Int_t lep_p = 0; // number of anti leptons in each event
    Int_t lep_n = 0; // number of leptons in each event
    Int_t lep_p_idx = -1; // index of the anti lepton
    Int_t lep_n_idx = -1; // index of the lepton

    for (Int_t idx = 0; idx < evnt_ids.size(); ++idx) {
        Int_t id_ = evnt_ids[idx];
        if (id_ == PDGId) {
            lep_p += 1; // count the anti leptons
            lep_p_idx = idx; // update the index. If an event is dilepton then this index will not be updated
        }
        else if (id_ == -PDGId) {
            lep_n += 1; // count the leptons
            lep_n_idx = idx; // update the index. If an event is dilepton then this index will not be updated
        }
    }

    if (lep_p == 1 && lep_n == 1) {
        return true;
    }
    else {
        return false;
    }
}

RVec<int> MapCharge(const RVec<int>& event_ids, RVec<int>& interest_ids) {
    
    // Maps the gen lepton's to their corresponding charge
    // The gen leptons in question are those matched to a reco lepton
    // Arguments:
    // - event_ids: (RVec) vector of the PDGIds precent in a event
    // - interes_ids: (RVec) vector of the indices of the gen particles matching to the reco leptons 
    //                        as stored in the GenPart_ branch in an event. 

    map<int, int> charge;
    charge[13] = -1;   // charge of a muon
    charge[-13] = +1;  // charge of an anti muon
    charge[11] = -1;   // charge of an electron
    charge[-11] = +1;  // charge of an anti electron
    
    Int_t index1 = interest_ids[0]; // Get the index of the first gen lepton 
    Int_t index2 = interest_ids[1]; // Get the index of the second gen lepton

    // Using the above indices, get the flavor of the leptons
    Int_t PDGId1 = event_ids[index1];
    Int_t PDGId2 = event_ids[index2];
    
    // Map the leptons to their charge
    Int_t mappedCharge1 = charge[PDGId1];
    Int_t mappedCharge2 = charge[PDGId2];

    return RVec<int>({mappedCharge1, mappedCharge2});
}


float ComputeInvariantMass(RVec<float>& pt, RVec<float>& eta, RVec<float>& phi, RVec<int>& index){

    // Calculates the invariant mass of a dilepton pair
    // Argumets:
    // - pt:     (RVec) a vector with the particles pts in an event
    // - eta:    (RVec) a vector with the particles etas in an event
    // - phi:    (RVec) a vector with the particles phis in an event
    // - index:  (RVec) a vector with the leptons indeices as stored in pt eta and phi RVecs

    Int_t id1 = index[0]; // the index of the first lepton
    Int_t id2 = index[1]; // the index of the second lepton

    PtEtaPhiMVector p1(pt[id1], eta[id1], phi[id1], 0);
    PtEtaPhiMVector p2(pt[id2], eta[id2], phi[id2], 0);
    return (p1 + p2).M();
}

#endif