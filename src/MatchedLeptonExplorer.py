import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)

## Declare some helper functions
# They will be added to a C header file latter on. 

ROOT.gInterpreter.Declare('''

using namespace ROOT::VecOps;
using namespace std;

bool Filter_GetRecoDilepton(const RVec<int>& dilepton, int flavor) {
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

using Vec_t = const RVec<float>;

float ComputeInvariantMass(Vec_t& pt, Vec_t& eta, Vec_t& phi, Vec_t& index){
    Int_t id1 = index[0]; // the index of the first gen lepton
    Int_t id2 = index[1]; // the index of the second gen lepton

    ROOT::Math::PtEtaPhiMVector p1(pt[id1], eta[id1], phi[id1], 0);
    ROOT::Math::PtEtaPhiMVector p2(pt[id2], eta[id2], phi[id2], 0);
    return (p1 + p2).M();
}
''')

def set_axes_range(pltObj, Xrange, Yrange):
    pltObj.GetXaxis().SetRangeUser(Xrange[0], Xrange[1])
    pltObj.GetYaxis().SetRangeUser(Yrange[0], Yrange[1])
    return
#

def add_Header(title):
    label = ROOT.TLatex()
    label.SetTextSize(0.04)
    label.DrawLatexNDC(0.18, 0.92, "#bf{"+str(title)+"}")
    return
#

def set_axes_title(pltObj, xtitle, ytitle):
    pltObj.GetXaxis().SetTitle(str(xtitle))
    pltObj.GetYaxis().SetTitle(str(ytitle))
    return
#


## Input configuration
inPath = "/cms/multilepton-4/jvora/ULnano/Skims/05Apr23/MC/2LOS_Skim_medium_2018/"
inFileName="Snapshot_DY_1of8.root"
inFile = inPath + inFileName

treeName = "skimTree"
df = ROOT.RDataFrame(treeName, inFile)#.Range(10)

## Output configuration
outPath = "/home/kpapad/charge_mis/out/plots/"
outNameMuons = "DY_1of8_Muons_FlipHist.pdf"
outNameElectrons = "DY_1of8_Electrons_FlipHist.pdf"
outFileMuons, outFileElectrons = [outPath + name for name in (outNameMuons, outNameElectrons)] 

## Begin with muons --------------------------------------------------------------------------------------------------------
muons = df.Filter("Filter_GetRecoDilepton(LightLepton_Flavor, 2)") \
    .Define("GenLepton_InvMass", "ComputeInvariantMass(GenPart_Pt, GenPart_Eta, GenPart_Phi, LightLepton_GenPartIndex)") \
    .Define("GenLepton_Charge", "MapCharge(GenPart_PDGId, LightLepton_GenPartIndex)") \
    .Define("GenTimesLight_Charge", "LightLepton_Charge*GenLepton_Charge") \
    .Define("LightLepton_ChargeSum", "LightLepton_Charge[0]+LightLepton_Charge[1]") 
#
numMuons = muons.Count().GetValue() # Total number of Drell-Yan dimuon events
## One way of estimating the charge flip ratio 
# is to compare the charge of a reco mu to the charge of its corresponding gen mu  
# If there is no charge flip the product charge of gen mu x charge of gen mu = 1  
# otherwise it will be -1
# This gives the true number of charge flips

muonsProdFliped = muons.Filter("Any(GenTimesLight_Charge == -1)").Count().GetValue() #  events with charge flips
muonsProdFlipRatio = muonsProdFliped / numMuons
print("the ture rate of charge flip for muons is: ", muonsProdFlipRatio)

# Plot the charge product histogram
c = ROOT.TCanvas()
c.SetLogx(0); c.SetLogy(0)
c.SetCanvasSize(800, 800)
c.SetLeftMargin(0.15)
c.cd()
c.SaveAs(outFileMuons+"[")

# Plot the invariant mass of the gen lepton pair at first
c.SetLogy(1)
genMuonsMass = muons.Histo1D( ("genMuonsMass", "", 50, 50, 300), "GenLepton_InvMass")
set_axes_title(genMuonsMass, "M_ll", "counts")
genMuonsMass.Draw()
add_Header("gen muons mass")
c.SaveAs(outFileMuons)

c.SetLogy(0)
muonsProdLeading_Hist = muons.Define("GenTimesLight_ChLeading", "GenTimesLight_Charge[0]") \
.Histo1D( ("muonsProdLeading_Hist", "", 50, -2, 2), "GenTimesLight_ChLeading" )

set_axes_title(muonsProdLeading_Hist, "gen charge x reco charge", "counts")
muonsProdLeading_Hist.SetLineColor(1)
muonsProdLeading_Hist.Draw()

muonsProdSub_Hist = muons.Define("GenTimesLight_ChSub", "GenTimesLight_Charge[1]") \
.Histo1D( ("muonsProdSub_Hist", "", 50, -2, 2), "GenTimesLight_ChSub")
muonsProdSub_Hist.SetLineColor(3)
muonsProdSub_Hist.SetLineStyle(2)

muonsProdSub_Hist.Draw("same")

legend = ROOT.TLegend(0.35, 0.72, 0.45, 0.85)
legend.AddEntry(muonsProdLeading_Hist.GetValue(), "Leading muon", "l")
legend.AddEntry(muonsProdSub_Hist.GetValue(), "Subleading muon", "l")
legend.SetFillColor(0)
legend.SetBorderSize(0)
legend.SetTextSize(0.03)
legend.Draw("same")

label = ROOT.TLatex()
label.SetTextSize(0.03)
label.DrawLatexNDC(0.35, 0.68,"charge flip events: {}".format(muonsProdFliped) )

c.SaveAs(outFileMuons)

## Another way of estimating the charge flip ratio 
# is to examine the total charge of the ll pair.
# The DY dimuons are charge neutral and thus in case of a flip, the total charge will be != 0. 

dimuonFlipped = muons.Filter("LightLepton_ChargeSum != 0").Count().GetValue()
dimuonFlippRatio = dimuonFlipped / numMuons
print("the estimated rate of charge flip for muons is: ",dimuonFlippRatio)

# Plot the total charge histogram
dimuonCharge_Hist = muons.Histo1D( ("dimuonCharge_Hist", "", 50, -2, 2), "LightLepton_ChargeSum" )

set_axes_title(dimuonCharge_Hist, "Total Charge", "counts")
dimuonCharge_Hist.SetLineColor(1)
dimuonCharge_Hist.Draw()

label = ROOT.TLatex()
label.SetTextSize(0.03)
label.DrawLatexNDC(0.25, 0.68, "charge flip events: {}".format(dimuonFlipped))

c.SaveAs(outFileMuons)

c.SaveAs(outFileMuons+"]")

## Continue with electrons --------------------------------------------------------------------------------------------------------
electrons = df.Filter("Filter_GetRecoDilepton(LightLepton_Flavor, 1)") \
    .Define("GenLepton_InvMass", "ComputeInvariantMass(GenPart_Pt, GenPart_Eta, GenPart_Phi, LightLepton_GenPartIndex)") \
    .Define("GenLepton_Charge", "MapCharge(GenPart_PDGId, LightLepton_GenPartIndex)") \
    .Define("GenTimesLight_Charge", "LightLepton_Charge*GenLepton_Charge") \
    .Define("LightLepton_ChargeSum", "LightLepton_Charge[0]+LightLepton_Charge[1]") 
#
numElectrons = electrons.Count().GetValue() # Total number of Drell-Yan dielectron events

## Compare the charge of a reco e to the charge of its corresponding gen e  

electronsProdFliped = electrons.Filter("Any(GenTimesLight_Charge == -1)").Count().GetValue() #  events with charge flips
electronsProdFlipRatio = electronsProdFliped / numElectrons
print("the ture rate of charge flip for electrons is: ", electronsProdFlipRatio)

# Plot the charge product histogram
c = ROOT.TCanvas()
c.SetLogx(0); c.SetLogy(0)
c.SetCanvasSize(800, 800)
c.SetLeftMargin(0.15)
c.cd()
c.SaveAs(outFileElectrons+"[")

# Plot the invariant mass of the gen electrons
c.SetLogy(1)
genElectronsMass = electrons.Histo1D( ("genElectronsMass", "", 50, 50, 300), "GenLepton_InvMass")
set_axes_title(genElectronsMass, "M_ll", "counts")
genElectronsMass.Draw()
add_Header("gen electrons mass")
c.SaveAs(outFileElectrons)

c.SetLogy(0)
electronsProdLeading_Hist = electrons.Define("GenTimesLight_ChLeading", "GenTimesLight_Charge[0]") \
.Histo1D( ("electronsProdLeading_Hist", "", 50, -2, 2), "GenTimesLight_ChLeading" )

set_axes_title(electronsProdLeading_Hist, "gen charge x reco charge", "counts")
electronsProdLeading_Hist.SetLineColor(1)
electronsProdLeading_Hist.Draw()

electronsProdSub_Hist = electrons.Define("GenTimesLight_ChSub", "GenTimesLight_Charge[1]") \
.Histo1D( ("electronsProdSub_Hist", "", 50, -2, 2), "GenTimesLight_ChSub")
electronsProdSub_Hist.SetLineColor(3)
electronsProdSub_Hist.SetLineStyle(2)

electronsProdSub_Hist.Draw("same")

legend = ROOT.TLegend(0.35, 0.72, 0.45, 0.85)
legend.AddEntry(electronsProdLeading_Hist.GetValue(), "Leading electron", "l")
legend.AddEntry(electronsProdSub_Hist.GetValue(), "Subleading electron", "l")
legend.SetFillColor(0)
legend.SetBorderSize(0)
legend.SetTextSize(0.03)
legend.Draw("same")

label = ROOT.TLatex()
label.SetTextSize(0.03)
label.DrawLatexNDC(0.35, 0.68, "charge flip events: {}".format(electronsProdFliped))

c.SaveAs(outFileElectrons)

# Examine the total charge of the ll pair.

dielectronFlipped = electrons.Filter("LightLepton_ChargeSum != 0").Count().GetValue()
dielectronFlippRatio = dielectronFlipped / numElectrons
print("the estimated rate of charge flip for electrons is: ",dielectronFlippRatio)

# Plot the total charge histogram
dielectronCharge_Hist = electrons.Histo1D( ("dielectronCharge_Hist", "", 50, -2, 2), "LightLepton_ChargeSum" )

set_axes_title(dielectronCharge_Hist, "Total Charge", "counts")
dielectronCharge_Hist.SetLineColor(1)
dielectronCharge_Hist.Draw()

label = ROOT.TLatex()
label.SetTextSize(0.03)
label.DrawLatexNDC(0.2, 0.68, "charge flip events: {}".format(dielectronFlipped) )

c.SaveAs(outFileElectrons)

c.SaveAs(outFileElectrons+"]")
