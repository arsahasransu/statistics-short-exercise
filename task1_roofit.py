from ROOT import *

MH = RooRealVar("MH", "mass of hypothetical particle in GeV", 125, 120, 130)
MH.setVal(130)
mass = RooRealVar("mass", "invariant mass of decay particles in GeV", 100, 80, 200)
sigma = RooRealVar("sigma", "variance in mass of decay particles in GeV", 10, 0, 20)
#MH.Print()
#print MH.getVal()

func = RooFormulaVar("R", "@0/@1", RooArgList(sigma,mass))
gauss = RooGaussian("gauss", "f(m|M_{H},#sigma)", mass, MH, sigma)
#func.Print("v")
#gauss.Print("v")

can = TCanvas()
plot = mass.frame()

gauss.plotOn(plot,RooFit.LineColor(kGreen+3))
MH.setVal(125)
gauss.plotOn(plot,RooFit.LineColor(kRed))
MH.setVal(120)
gauss.plotOn(plot,RooFit.LineColor(kBlue))
MH.setVal(115)
gauss.plotOn(plot,RooFit.LineColor(kGreen),RooFit.LineStyle(2))

plot.Draw()
can.Draw()
can.SaveAs("gaussians.pdf")
