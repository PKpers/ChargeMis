# PyROOT plotting functions 
import ROOT

def set_axes_range(pltObj, Xrange, Yrange):
    # Set the raange of the axes
    # Args:
    # - pltObj: any of the pyroot ploting classes (i.e TH1F)  
    # - Xrange: (list or tuple) the x axis range starting and ending points
    # - Yrange: (list or tuple) the y axis range starting and ending points
    # To set only one axis range provide an empty list/tuple for the other one. 

    if not Yrange : 
        pltObj.GetXaxis().SetRangeUser(Xrange[0], Xrange[1])
        return
    elif not Xrange :
        pltObj.GetYaxis().SetRangeUser(Yrange[0], Yrange[1])
        return
    else:
        pltObj.GetXaxis().SetRangeUser(Xrange[0], Xrange[1])
        pltObj.GetYaxis().SetRangeUser(Yrange[0], Yrange[1])
        return
#

def add_Header(title):
    # Adds a title to the top left corner of the plot
    # Arguments:
    # - title: (str) the title of the plot
    # Use this function after <pltobj>.Draw(), as it changes the TCanvas 

    label = ROOT.TLatex()
    label.SetTextSize(0.04)
    label.DrawLatexNDC(0.18, 0.92, "#bf{"+str(title)+"}")
    return
#

def set_axes_title(pltObj, xtitle, ytitle):
    # Set the title of the axes
    # Args:
    # - pltObj: any of the pyroot ploting classes (i.e TH1F)  
    # - Xtitle: (str) the x axis title
    # - Ytitle: (str) the y axis title

    pltObj.GetXaxis().SetTitle(str(xtitle))
    pltObj.GetYaxis().SetTitle(str(ytitle))
    return
#

def create_legend(position, entries):
    # Creates a legend 
    # Arguments:
    # position: (list/tuple) starting and ending x and y coordinates of the legend
    # entries: (dictionary) dict containing the entries to be added to the legend
    # the keys of the dict should be the pltobjects name 
    # and the objects should be a list containing the objects title and the linestyle apearing on the legend
    # don't forget to Draw() the legend after create_legend

    xmin, ymin, xmax, ymax = position
    legend = ROOT.TLegend(xmin, ymin, xmax, ymax)
    legend.SetFillColor(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.03)
    for entry, attribs in entries.items():
        _name = entry
        _title, _linestyle = attribs
        legend.AddEntry(_name, _title, _linestyle)
    #
    #legend.Draw('same')
    return legend

