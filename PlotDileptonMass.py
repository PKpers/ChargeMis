import ROOT
import numpy as np

def add_Header(title):
    '''
    Adds a title to the top left side of a plot
    arguments
    title: The text to be put as title
    this function shuld be called AFTER <plotobj>.Draw()
    '''
    label = ROOT.TLatex()
    label.SetTextSize(0.04)
    label.DrawLatexNDC(0.16, 0.92, "#bf{"+str(title)+"}")
    return 

def Plot(inFile, name, lables):
    """
    Plots a histogram contained in a specified root file.
    arguments 
    inFile:(str) The name of the root file which contains the hist
    name:(str) The name of the histogram
    lables:(list) The plot title, x axis and y axis labels
    """

    ## Read the file and get the hist object
    myFile=ROOT.TFile.Open(inFile, "READ")
    hist=myFile.Get(name)
    hist.SetDirectory(0)
    myFile.Close()

    ## Unpack the title, x and y labels
    title, xlabel, ylabel = lables

    ## Make the plot 
    hist.GetXaxis().SetRangeUser(50, 300)
    hist.GetXaxis().SetTitle(xlabel)
    hist.GetYaxis().SetTitle(ylabel)
    hist.SetMarkerSize(1)
    hist.Draw()

    add_Header(title)
    return


if __name__ == "__main__":
    ## I/O configuration
    outFile = "LeptonsMassPlot.pdf"
    McNamePrefix = "DY_1of8" # for simulation
    DataNamePrefix = "Data_1of14" # for real data
    namePrefix = [McNamePrefix, DataNamePrefix]
    
    # For muons
    inFileMuons = [pref+"_MuonsHist.root" for pref in namePrefix]
    muonsHistName = "muon_mass_hist"
    print(inFileMuons)

    # For electrons
    inFileElectrons = [pref+"_ElectronsHist.root" for pref in namePrefix]
    electronsHistName = "electron_mass_hist"
    print(inFileElectrons)

    # Grouping them together
    inFiles = inFileMuons + inFileElectrons
    titles = ["MC Muons", "Real Muons", "MC Electrons", "Real Electrons"]
    xlabel = "M_ll (GeV)"
    ylabel = "Counts"
    names = [
        muonsHistName if "Muons" in t else electronsHistName 
        for t in titles
    ]
    print(names)
    

    ## Make the plots
    ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)
    c = ROOT.TCanvas()
    c.SetLogx(0); c.SetLogy(1)
    c.SetCanvasSize(800, 800)
    c.cd()
    c.SaveAs(outFile+"[")
    for i in range(len(inFiles)):
        inFile = inFiles[i]
        name = names[i]
        labels =[titles[i], xlabel, ylabel]
        Plot(inFile, name, labels)
        c.SaveAs(outFile)
    #
    c.SaveAs(outFile+"]")