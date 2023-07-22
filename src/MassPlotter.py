import ROOT
from os import chdir, getcwd
import sys
sys.path.insert(0, '/home/kpapad/charge_mis/lib')
from pyrplot import set_axes_title, set_axes_range, add_Header, create_legend

## Include my C libs 
workingDIR = getcwd()
chdir('/home/kpapad/charge_mis/lib/')
ROOT.gInterpreter.ProcessLine('#include "funcy.h"')
chdir(workingDIR)

## Some general plot settings
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)


## Input configuration
#inPath = "/cms/multilepton-4/jvora/ULnano/Skims/05Apr23/MC/2LOS_Skim_medium_2018/"
#inFileName="Snapshot_DY_2LSS.root"
#inFile = inPath + inFileName
# Same sign MC
inFile = "/cms/multilepton-4/jvora/ULnano/Skims/12Jul23/Data/2LSS_Skim_medium_2018/Snapshot_Data.root"

treeName = "skimTree"
df = ROOT.RDataFrame(treeName, inFile)#.Range(100)

## Output configuration
outPath = "/cms/multilepton-2/kpapad/charge_mis/out/plots/"
outNameMuons = "Data_2LSS_Muons_MassHist.pdf"# 2 Leptons Same sign
outNameElectrons = "Data_2LSS_Electrons_MassHist.pdf"
outFileMuons, outFileElectrons = [outPath + name for name in (outNameMuons, outNameElectrons)] 

## Plot muons --------------------------------------------------------------------------------------------------------
muons = df.Filter("Filter_GetRecoDilepton(LightLepton_Flavor, 2)") \
    .Define("LightLepton_Idx", "RVec<int>{0, 1}") \
    .Define("LightLepton_InvMass", "ComputeInvariantMass(LightLepton_Pt, LightLepton_Eta, LightLepton_Phi, LightLepton_Idx)")\

numMuons = muons.Count().GetValue() # Total number of Drell-Yan dimuon events

# Plot the charge product histogram
c = ROOT.TCanvas()
c.SetLogx(0); c.SetLogy(1)
c.SetCanvasSize(800, 800)
c.SetLeftMargin(0.15)
c.cd()
c.SaveAs(outFileMuons+"[")

LightMuonsMass = muons.Histo1D( ("LightMuonsMass", "", 50, 50, 300), "LightLepton_InvMass")
set_axes_title(LightMuonsMass, "M_ll", "counts")
LightMuonsMass.Draw()
add_Header("light muons mass")
c.SaveAs(outFileMuons)
c.SaveAs(outFileMuons+"]")

## Plot electrons ----------------------------------------------------------------------------------------------------------
electrons = df.Filter("Filter_GetRecoDilepton(LightLepton_Flavor, 1)") \
    .Define("LightLepton_Idx", "RVec<int>{0, 1}") \
    .Define("LightLepton_InvMass", "ComputeInvariantMass(LightLepton_Pt, LightLepton_Eta, LightLepton_Phi, LightLepton_Idx)")\
#
numElectrons = electrons.Count().GetValue() # Total number of Drell-Yan dielectron events

# Plot the charge product histogram
c = ROOT.TCanvas()
c.SetLogx(0); c.SetLogy(0)
c.SetCanvasSize(800, 800)
c.SetLeftMargin(0.15)
c.cd()
c.SaveAs(outFileElectrons+"[")

LightElectronsMass = electrons.Histo1D( ("LightElectronsMass", "", 50, 50, 300), "LightLepton_InvMass")
set_axes_title(LightElectronsMass, "M_ll", "counts")
LightElectronsMass.Draw()
add_Header("light electrons mass")
c.SaveAs(outFileElectrons)
c.SaveAs(outFileElectrons+"]")

