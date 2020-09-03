from ROOT import *

MH = RooRealVar("MH", "mass of hypothetical particle in GeV", 125, 120, 130)
mass = RooRealVar("mass", "invariant mass of decay particles in GeV", 100, 80, 200)
sigma = RooRealVar("sigma", "variance in mass of decay particles in GeV", 10, 0, 20)
#MH.Print()
#MH.setVal(130)
#print MH.getVal()

func = RooFormulaVar("R", "@0/@1", RooArgList(sigma,mass))
gauss = RooGaussian("gauss", "f(m|M_{H},#sigma)", mass, MH, sigma)
#func.Print("v")
#gauss.Print("v")

can = TCanvas()
plot = mass.frame()

