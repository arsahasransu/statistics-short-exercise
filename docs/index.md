## Introduction to statistical methods

In these exercises we will be focussing on some of the tools you can use to produce the statistical results for your analysis, not the theoretical principles of statistics for particle physics. If you are not familiar with the main concepts we'd recommend that, before you start, you read [this short article from Physics Today](http://web.ipac.caltech.edu/staff/fmasci/home/astro_refs/ParticleStatistics_PhysToday_2012.pdf) which introduces likelihoods, bayesian vs frequentist statistics, hypothesis testing etc.

If you'd like more theoretical background you can also have a look at:

- [The Academic Training Lectures series on Statistics](https://indico.cern.ch/event/358542/)
- [The ATLAS-CMS note on the procedure for the Higgs combination](https://cds.cern.ch/record/1379837/files/NOTE2011_005.pdf); this includes a discussion of many of the conventions we use on ATLAS and CMS for the statistical analysis
- [A paper on the asymptotic approximation](https://arxiv.org/abs/1007.1727)

## Getting started

We need to set up a new CMSSW area and checkout the combine package: 

```shell
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout v8.1.0

cd $CMSSW_BASE/src
```
We will also make use another package, `CombineHarvester`, which contains some high-level tools for working with combine. The following command will  checkout the repository:
```shell
git clone https://github.com/cms-analysis/CombineHarvester.git
```
Now make sure the CMSSW area is compiled:
```shell 
scramv1 b clean; scramv1 b
```
Finally we will checkout the working directory for these tutorials - this contains all the inputs needed to run the exercises below:

```shell
cd $CMSSW_BASE/src
git clone https://github.com/CMSDAS/statistics-short-exercise.git
cd statistics-short-exercise
```

## RooFit
RooFit is an object-oriented analysis environment built on ROOT, with a collection of classes designed to augment ROOT for data modelling. Combine is in turn built on RooFit, so before learning about Combine, it is useful to get to grips with a few RooFit basics. We will do that in this section.

We will use python syntax in this section; you can either call the commands in an interactive python session, or just put them in a .py script. Make sure to do `from ROOT import *` at the top of your script (or in the interactive session)

### Variables
In RooFit, any variable, data point, function, PDF (etc.) is represented by a c++ object. The most basic of these is the RooRealVar. Let's create one which will represent the mass of some hypothetical particle, name it, and give a hypothetical starting value and range. 

```
MH = RooRealVar("MH","mass of the Hypothetical Boson (H-boson) in GeV",125,120,130)
MH.Print()
```

The output of this is
```
RooRealVar::MH = 125  L(120 - 130)
```

So we now have a RooRealVar called MH, with default value 125 and range 120-130. We can now access the object and change for example its value:

```
MH.setVal(130)
print MH.getVal()
```

Which should print the new value, 130. 

In particle detectors we typically don't observe this particle mass but usually define some observable which is sensitive to it. Let's assume we can detect and reconstruct the decay products of the H boson and measure the invariant mass of those particles. We need to make another variable which represents that invariant mass. Make a RooRealVar "mass" with a default value of 100 GeV and a range 80-200

(solution to show with toggle:)

```
mass = RooRealVar("m","m (GeV)",100,80,200)
```

In the perfect world we would measure the exact mass of the particle in every single event. However, our detectors are usually far from perfect so there will be some resolution effect. Lets assume the resolution of our measurement of the invariant mass is 10 GeV (range 0-20 GeV) and call it "sigma"

```
sigma = RooRealVar("resolution","#sigma",10,0,20)
```
### Functions and PDFs
More exotic variables can be constructed out of these `RooRealVar`s using `RooFormulaVar`s. For example, suppose we wanted to make a function out of the variables which represented the relative resolution as a function of the hypothetical mass MH.

```
func = RooFormulaVar("R","@0/@1",RooArgList(sigma,mass))
func.Print("v")
```

The main objects we are interested in using from RooFit are probability density functions (PDFs). We can construct the PDF $f(m|M_H,\sigma)$ as a Gaussian shape, a `RooGaussian`:

```
gauss = RooGaussian("gauss","f(m|M_{H},#sigma)",mass,MH,sigma)
gauss.Print("v")
```

Notice how the gaussian PDF, like the `RooFormulaVar` depends on our `RooRealVar` objects, these are its servers. Its evaluation will depend on their values.

The main difference between PDFs and functions in RooFit is that PDFs are automatically normalised to unity, hence they represent a probability density, you don't need to normalise yourself. Let's plot it for the different values of $M_H$.

### Plotting
First we need to make a canvas and a `RooPlot` object. This object needs to know what observable is going to be on the x-axis:

```
can = TCanvas()
plot = mass.frame()
```

Now we can plot the gaussian PDF for several mass values. We set $M_H$ to 130 GeV earlier on, so to plot this PDF for $M_H$ of 130 GeV we just do

```
gauss.plotOn(plot,RooFit.LineColor(kGreen+3))
```

Where we're using `kGreen+3` as the line colour. Notice that we need to tell RooFit on which `RooPlot` object we want to plot our PDF, even if we only have one such object.

Let's also plot the PDF with $M_H$ at 120 GeV, in blue, and with $M_H$ 125 GeV, in red:

```
MH.setVal(120)
gauss.plotOn(plot,RooFit.LineColor(kBlue))

MH.setVal(125)
gauss.plotOn(plot,RooFit.LineColor(kRed))
```

Finally, let's try adding this PDF for $M_H$ at 115 GeV in bright green. We'll use a dashed line for this one. Afterwards we'll draw the plot and save the canvas. 

```
MH.setVal(115)
gauss.plotOn(plot,RooFit.LineColor(kGreen),RooFit.LineStyle(2))

plot.Draw()
can.Draw()
can.SaveAs("gaussians.pdf")
```

Why do the blue and bright green lines overlap?

### Workspaces
Before we move on to Combine, we'll look at how to store RooFit objects and links between them. We can do this with a `RooWorkspace`. Let's create one and import our PDF, and the `RooFormulaVar` we created earlier:

```
w = RooWorkspace("w")

getattr(w,'import')(gauss)
getattr(w,'import')(func)

w.writeToFile("workspace.root")
```

Notice that the `RooRealVar`s we created are also getting imported into the workspace as our gaussian PDF depends on all three of them.

Now we can open the file that we've created in root:
```
root workspace.root
.ls
```
<details>
<summary><b>Show output </b></summary>
    
You should see that our workspace, named `w` is in the file:
    
```
TFile**		workspace.root
 TFile*		workspace.root
  KEY: RooWorkspace	w;1	w
  KEY: TProcessID	ProcessID0;1	94b05638-d0c4-11ea-a5b3-84978a89beef
```

</details>
We can inspect its contents:

```
w->Print()
```

<details>
<summary><b>Show output </b></summary>

```
RooWorkspace(w) w contents

variables
---------
(MH,m,resolution)

p.d.f.s
-------
RooGaussian::gauss[ x=m mean=MH sigma=resolution ] = 0.135335

functions
--------
RooFormulaVar::R[ actualVars=(resolution,m) formula="@0/@1" ] = 0.1
```
</details>    

Now we can check the properties of some of the objects, for example:

```
w->pdf("gauss")->Print("v")
```

<details>
<summary><b>Show output </b></summary>


```
--- RooAbsArg ---
  Value State: DIRTY
  Shape State: DIRTY
  Attributes:
  Address: 0x63b62e0
  Clients:
  Servers:
    (0x6781400,V-) RooRealVar::m "m (GeV)"
    (0x687edd0,V-) RooRealVar::MH "mass of the Hypothetical Boson (H-boson) in GeV"
    (0x6795740,V-) RooRealVar::resolution "#sigma"
  Proxies:
    x -> m
    mean -> MH
    sigma -> resolution
--- RooAbsReal ---

  Plot label is "gauss"
--- RooAbsPdf ---
Cached value = 0
```

</details>    

We can also check and change the values of our `RooRealVar`s

```
w->var("MH")->Print()
w->var("MH")->setVal(123)
w->var("MH")->getVal()
```

Gives:
```
RooRealVar::MH = 120  L(120 - 130)
```
and

```
(double) 123.00000
```

Note that if you close the file containing the workspace, open it again and call
```w->var("MH")->getVal()```

You will get the value as set when the workspace was created again, in our case that's 120 GeV:
```
(double) 120.00000
```

## Combine

For this course we will work with a simplified version of a real analysis, that nonetheless will have many features of the full analysis. The analysis is a search for an additional heavy neutral Higgs boson decaying to tau lepton pairs. Such a signature is predicted in many extensions of the standard model, in particular the minimal supersymmetric standard model (MSSM). You can read about the analysis in the paper [here](https://arxiv.org/pdf/1803.06553.pdf). The statistical inference makes use of a variable called the total transverse mass ($M_{\mathrm{T}}^{\mathrm{tot}}$) that provides good discrimination between the resonant high-mass signal and the main backgrounds, which have a falling distribution in this high-mass region. The events selected in the analysis are split into a several categories which target the main di-tau final states as well as the two main production modes: gluon-fusion (ggH) and b-jet associated production (bbH). One example is given below for the fully-hadronic final state in the b-tag category which targets the bbH signal:

![](images/CMS-DAS.003.jpeg)

Initially we will start with the simplest analysis possible: a one-bin counting experiment using just the high $M_{\mathrm{T}}^{\mathrm{tot}}$ region of this distribution, and we will expand on this by turning this into a shape-based analysis. 

## Combine part 1: datacard format and asymptotic limits

### Datacard format

We will begin with a simplified version of a datacard from the MSSM $\phi\rightarrow\tau\tau$ analysis that has been converted to a one-bin counting experiment, as described above. While the full analysis considers a range of signal mass hypotheses, we will start by considering just one: $m_{\phi}$=800GeV. Click the text below to study the datacard (`datacard_part1.txt` in the `cms-das-stats-2020` directory):

<details>
<summary><b>Show datacard</b></summary>
    
```shell
imax    1 number of bins
jmax    4 number of processes minus 1
kmax    * number of nuisance parameters
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
bin          signal_region
observation  10.0
--------------------------------------------------------------------------------
bin                      signal_region   signal_region   signal_region   signal_region   signal_region
process                  ttbar           diboson         Ztautau         jetFakes        bbHtautau
process                  1               2               3               4               0
rate                     4.43803         3.18309         3.7804          1.63396         0.711064
--------------------------------------------------------------------------------
CMS_eff_b          lnN   1.02            1.02            1.02            -               1.02
CMS_eff_t          lnN   1.12            1.12            1.12            -               1.12
CMS_eff_t_highpt   lnN   1.1             1.1             1.1             -               1.1
acceptance_Ztautau lnN   -               -               1.08            -               -
acceptance_bbH     lnN   -               -               -               -               1.05
acceptance_ttbar   lnN   1.005           -               -               -               -
lumi_13TeV         lnN   1.025           1.025           1.025           -               1.025
norm_jetFakes      lnN   -               -               -               1.2             -
xsec_Ztautau       lnN   -               -               1.04            -               -
xsec_diboson       lnN   -               1.05            -               -               -
xsec_ttbar         lnN   1.06            -               -               -               -
```
    
</details>

The layout of the datacard is as follows:

  -   At the top are the numbers `imax`, `jmax` and `kmax` representing the number of bins, processes and nuisance parameters respectively. Here a "bin" can refer to a literal single event count as in this example, or a full distribution we are fitting, in general with many histogram bins, as we will see later. We will refer to both as "channels" from now on. It is possible to replace these numbers with `*` and they will be deduced automatically.
  -   The first line starting with `bin` gives a unique label to each channel, and the following line starting with `observation` gives the number of events observed in data.
  -   In the remaining part of the card there are several columns: each one represents one process in one channel. The first four lines labelled `bin`, `process`, `process` and `rate` give the channel label, the process label, a process identifier (`<=0` for signal, `>0` for background) and the number of expected events respectively.
  -   The remaining lines describe sources of systematic uncertainty. Each line gives the name of the uncertainty, (which will become the name of the nuisance parameter inside our RooFit model), the type of uncertainty ("lnN" = log-normal normalisation uncertainty) and the effect on each process in each channel. E.g. a 20% uncertainty on the yield is written as 1.20.
  -   It is also possible to add a hash symbol (`#`) at the start of a line, which combine will then ignore when it reads the card.


We can now run combine directly using this datacard as input. The general format for running combine is:

```shell
combine -M [method] [datacard] [additional options...]
```

### Asymptotic limits

As we are searching for a signal process that does not exist in the standard model, it's natural to set an upper limit on the cross section times branching fraction of the process (assuming our dataset does not contain a significant discovery of new physics). Combine has dedicated method for calculating upper limits. The most commonly used one is `AsymptoticLimits`, which implements the CLs criterion and uses the profile likelihood ratio as the test statistic. As the name implies, the test statistic distributions are determined analytically in the asymptotic approximation, so there is no need for more time-intensive toy throwing and fitting. Try running the following command:

```shell
combine -M AsymptoticLimits datacard_part1.txt -n .part1A
```

You should see the results of the observed and expected limit calculations printed to the screen. Here we have added an extra option, `-n .part1A`, which is short for `--name`, and is used to label the output file combine produces, which in this case will be called `higgsCombine.part1A.AsymptoticLimits.mH120.root`. The file name depends on the options we ran with, and is of the form: `higgsCombine[name].[method].mH[mass].root`. The file contains a TTree called `limit` which stores the numerical values returned by the limit computation. Note that in our case we did not set a signal mass when running combine (i.e. `-m 800`), so the output file just uses the default value of `120`. This does not affect our result in any way though, just the label that is used on the output file.

The limits are given on a parameter called `r`. This is the default **parameter of interest (POI)** that is added to the model automatically. It is a linear scaling of the normalisation of all signal processes given in the datacard, i.e. if $s_{i,j}$ is the nominal number of signal events in channel $i$ for signal process $j$, then the normalisation of that signal in the model is given as $r\cdot s_{i,j}(\vec{\theta})$, where $\vec{\theta}$ represents the set of nuisance parameters which may also affect the signal normalisation. We therefore have some choice in the interpretation of r: for the measurement of a process with a well defined SM prediction we may enter this as the nominal yield in the datacard, such that $r=1$ corresponds to this SM expectation, whereas for setting limits on BSM processes we may choose the nominal yield to correspond to some cross section, e.g. 1 pb, such that we can interpret the limit as a cross section limit directly. In this example the signal has been normalised to a cross section times branching fraction of 1 fb.

The expected limit is given under the background-only hypothesis. The median value under this hypothesis as well as the quantiles needed to give the 68% and 95% intervals are also calculated. These are all the ingredients needed to produce the standard limit plots you will see in many CMS results, for example the $\sigma \times \mathcal{B}$ limits for the $\text{bb}\phi\rightarrow\tau\tau$ process:

![](images/CMS-DAS.002.jpeg)

In this case we only computed the values for one signal mass hypothesis, indicated by a red dashed line.

**Tasks and questions:**

  -   There are some important uncertainties missing from the datacard above. Add the uncertainty on the luminosity (name: `lumi_13TeV`) which has a 2.5% effect on all processes (except the `jetFakes`, which are taken from data), and uncertainties on the inclusive cross sections of the `Ztautau` and `ttbar` processes (with names `xsec_Ztautau` and `xsec_diboson`) which are 4% and 6% respectively.
  -   Try changing the values of some uncertainties (up or down, or removing them altogether) - how do the expected and observed limits change?
  -   Now try changing the number of observed events. The observed limit will naturally change, but the expected does too - why might this be?


There are other command line options we can supply to combine which will change its behaviour when run. You can see the full set of supported options by doing `combine -h`. Many options are specific to a given method, but others are more general and are applicable to all methods. Throughout this tutorial we will highlight some of the most useful options you may need to use, for example:

  - The range on the signal strength modifier: `--rMin=X` and `--rMax=Y`: In RooFit parameters can optionally have a range specified. The implication of this is that their values cannot be adjusted beyond the limits of this range. The min and max values can be adjusted though, and we might need to do this for our POI `r` if the order of magnitude of our measurement is different from the default range of `[0, 20]`. This will be discussed again later in the tutorial.
  - Verbosity: `-v X`: By default combine does not usually produce much output on the screen other the main result at the end. However, much more detailed information can be printed by setting the `-v N` with N larger than zero. For example at `-v 3` the logs from the minimizer, Minuit, will also be printed. These are very useful for debugging problems with the fit.


## Combine part 2: shape-based analysis


### Setting up the datacard
Now we move to the next step: instead of a one-bin counting experiment we will fit a binned distribution. In a typical analysis we will produce TH1 histograms of some variable sensitive to the presence of signal: one for the data and one for each signal and background processes. Then we add a few extra lines to the datacard to link the declared processes to these shapes which are saved in a ROOT file, for example:

<details>
<summary><b>Show datacard</b></summary>
```shell
imax 1
jmax 1
kmax *
---------------
shapes * * simple-shapes-TH1_input.root $PROCESS $PROCESS_$SYSTEMATIC
shapes signal * simple-shapes-TH1_input.root $PROCESS$MASS $PROCESS$MASS_$SYSTEMATIC
---------------
bin bin1
observation 85
------------------------------
bin             bin1       bin1
process         signal     background
process         0          1
rate            10         100
--------------------------------
lumi     lnN    1.10       1.0
bgnorm   lnN    1.00       1.3
alpha  shape    -          1
```
</details>

Note that as with the one-bin card, the total nominal rate of a given process must be specified in the `rate` line of the datacard. This should agree with the value returned by `TH1::Integral`. However, we can also put a value of `-1` and the Integral value will be substituted automatically.

There are two other differences with respect to the one-bin card:

  - A new block of lines at the top defining how channels and processes are mapped to the histograms (more than one line can be used)
  - In the list of systematic uncertainties some are marked as shape instead of lnN

The syntax of the "shapes" line is: `shapes [process] [channel] [file] [histogram] [histogram_with_systematics]`. It is possible to use the `*` wildcard to map multiple processes and/or channels with one line. The histogram entries can contain the `$PROCESS`, `$CHANNEL` and `$MASS` place-holders which will be substituted when searching for a given (process, channel) combination. The value of `$MASS` is specified by the `-m` argument when combine. By default the observed data process name will be `data_obs`.

Shape uncertainties can be added by supplying two additional histograms for a process, corresponding to the distribution obtained by shifting that parameter up and down by one standard deviation. These shapes will be interpolated with a polynomial for shifts below $1\sigma$ and linearly beyond. The normalizations are interpolated linearly in log scale just like we do for log-normal uncertainties.


The final argument of the "shapes" line above should contain the `$SYSTEMATIC` place-holder which will be substituted by the systematic name given in the datacard.

In the list of uncertainties the interpretation of the values for `shape` lines is a bit different from `lnN`. The effect can be "-" or 0 for no effect, 1 for normal effect, and possibly something different from 1 to test larger or smaller effects (in that case, the unit Gaussian is scaled by that factor before using it as parameter for the interpolation).

In this section we will use a datacard corresponding to the full distribution that was shown at the start of section 1, not just the high mass region. Have a look at `datacard_part2.txt`: this is still currently a one-bin counting experiment, however the yields are much higher since we now consider the full range of $M_{\mathrm{T}}^{\mathrm{tot}}$. If you run the asymptotic limit calculation on this you should find the sensitivity is significantly worse than before.

The **first task** is to convert this to a shape analysis: the file `datacard_part2.shapes.root` contains all the necessary histograms, including those for the relevant shape systematic uncertainties. Add the relevant `shapes` lines to the top of the datacard (after the `kmax` line) to map the processes to the correct TH1s in this file. Hint: you will need a different line for the signal process.

Compared to the counting experiment we must also consider the effect of uncertainties that change the shape of the distribution. Some, like `CMS_eff_t_highpt`, were present before, as it has both a shape and normalisation effect. Others are primarily shape effects so were not included before.

Add the following shape uncertainties: `top_pt_ttbar_shape` affecting `ttbar`,the tau energy scale uncertainties `CMS_scale_t_1prong0pi0_13TeV`, `CMS_scale_t_1prong1pi0_13TeV` and `CMS_scale_t_3prong0pi0_13TeV` affecting all processes except `jetFakes`, and `CMS_eff_t_highpt` also affecting the same processes.

Once this is done you can run the asymptotic limit calculation on this datacard. From now on we will convert the text datacard into a RooFit workspace ourselves instead of combine doing it internally every time we run. This is a good idea for more complex analyses since the conversion step can take a notable amount of time. For this we use the `text2workspace.py` command:

```shell
text2workspace.py datacard_part2.txt -m 800 -o workspace_part2.root
```
And then we can use this as input to combine instead of the text datacard:
```shell
combine -M AsymptoticLimits workspace_part2.root -m 800
```
**Tasks and questions:**

  - Verify that the sensitivity of the shape analysis is indeed improved over the counting analysis in the first part.

### Running combine for a blind analysis
Most analyses are developed and optimised while we are "blind" to the region of data where we expect our signal to be. With `AsymptoticLimits` we can choose just to run the expected limit (`--run expected`), so as not to calculate the observed. However the data is still used, even for the expected, since in the frequentist approach a background-only fit to the data is performed to define the Asimov dataset used to calculate the expected limits. To skip this fit to data and use the pre-fit state of the model the option `--run blind` or `--noFitAsimov` can be used. **Task:** Compare the expected limits calculated with `--run expected` and `--run blind`. Why are they different?

A more general way of blinding is to use combine's toy and Asimov dataset generating functionality. You can read more about this [here](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/runningthetool/#toy-data-generation). These options can be used with any method in combine, not just `AsymptoticLimits`.

**Task:** Calculate a blind limit by generating a background-only Asimov with the `-t -1` option instead of using the `AsymptoticLimits` specific options. You should find the observed limit is the same as the expected. Then see what happens if you inject a signal into the Asimov dataset using the `--expectSignal [X]` option.

### Using FitDiagnostics
We will now explore one of the most commonly used modes of combine: `FitDiagnostics`. As well as allowing us to make a **measurement** of some physical quantity (as opposed to just setting a limit on it), this method is useful to gain additional information about the model and the behaviour of the fit. It performs two fits:

  - A "background-only" (b-only) fit: first POI (usually "r") fixed to zero
  - A "signal+background" (s+b) fit: all POIs are floating
 
With the s+b fit combine will report the best-fit value of our signal strength modifier `r`. As well as the usual output file, a file named `fitdiagnostics.root` is produced which contains additional information. In particular it includes two `RooFitResult` objects, one for the b-only and one for the s+b fit, which store the fitted values of all the **nuisance parameters (NPs)** and POIs as well as estimates of their uncertainties. The covariance matrix from both fits is also included, from which we can learn about the correlations between parameters. Run the `FitDiagnostics` method on our workspace:

```shell
combine -M FitDiagnostics workspace_part2.root -m 800 --rMin -20 --rMax 20
```
Open the resulting `fitDiagnostics.root` interactively and print the contents of the s+b RooFitResult:

```shell
root [1] fit_s->Print()
```
<details>
<summary><b>Show output</b></summary>
    
```shell
 RooFitResult: minimized FCN value: -4.7666, estimated distance to minimum: 3.31389e-05
                covariance matrix quality: Full, accurate covariance matrix
                Status : MINIMIZE=0 HESSE=0

   Floating Parameter    FinalValue +/-  Error
--------------------  --------------------------
             CMS_eff_b   -4.3559e-02 +/-  9.87e-01
             CMS_eff_t   -2.6382e-01 +/-  7.27e-01
      CMS_eff_t_highpt   -4.7214e-01 +/-  9.56e-01
      CMS_scale_t_1prong0pi0_13TeV   -1.5884e-01 +/-  5.89e-01
      CMS_scale_t_1prong1pi0_13TeV   -1.6512e-01 +/-  4.91e-01
      CMS_scale_t_3prong0pi0_13TeV   -3.0668e-01 +/-  6.03e-01
    acceptance_Ztautau   -3.1059e-01 +/-  8.57e-01
        acceptance_bbH   -5.8325e-04 +/-  9.94e-01
      acceptance_ttbar    4.7839e-03 +/-  9.94e-01
            lumi_13TeV   -5.4684e-02 +/-  9.83e-01
         norm_jetFakes   -9.3975e-02 +/-  2.54e-01
                     r   -2.7327e+00 +/-  2.57e+00
    top_pt_ttbar_shape    1.7614e-01 +/-  6.97e-01
          xsec_Ztautau   -1.5991e-01 +/-  9.61e-01
          xsec_diboson    3.8745e-02 +/-  9.94e-01
            xsec_ttbar    5.8025e-02 +/-  9.41e-01
```
</details>

There are several useful pieces of information here. At the top the status codes from the fits that were performed is given. In this case we can see that two algorithms were run: `MINIMIZE` and `HESSE`, both of which returned a successful status code (0). Both of these are routines in the **Minuit2** minimization package - the default minimizer used in RooFit. The first performs the main fit to the data, and the second calculates the covariance matrix at the best-fit point. It is important to always check this second step was successful and the message "Full, accurate covariance matrix" is printed, otherwise the parameter uncertainties can be very inaccurate, even if the fit itself was successful.

Underneath this the best-fit values ($\theta$) and symmetrised uncertainties for all the floating parameters are given. For all the constrained nuisance parameters a convention is used by which the nominal value ($\theta_I$) is zero, corresponding to the mean of a Gaussian constraint PDF with width 1.0, such that the parameter values $\pm 1.0$ correspond to the $\pm 1\sigma$ input uncertainties.

A more useful way of looking at this is to compare the pre- and post-fit values of the parameters, to see how much the fit to data has shifted and constrained these parameters with respect to the input uncertainty. The script `diffNuisances.py` can be used for this:

```shell
python diffNuisances.py fitDiagnostics.root --all
```
<details>
<summary><b>Show output</b></summary>
    
```shell
name                                              b-only fit            s+b fit         rho
CMS_eff_b                                        -0.04, 0.99        -0.04, 0.99       +0.01
CMS_eff_t                                     * -0.24, 0.73*     * -0.26, 0.73*       +0.06
CMS_eff_t_highpt                              * -0.56, 0.93*     * -0.47, 0.96*       +0.03
CMS_scale_t_1prong0pi0_13TeV                  * -0.17, 0.58*     * -0.16, 0.59*       -0.04
CMS_scale_t_1prong1pi0_13TeV                  ! -0.12, 0.45!     ! -0.17, 0.49!       +0.21
CMS_scale_t_3prong0pi0_13TeV                  * -0.31, 0.60*     * -0.31, 0.60*       +0.02
acceptance_Ztautau                            * -0.31, 0.86*     * -0.31, 0.86*       -0.05
acceptance_bbH                                   +0.00, 0.99        -0.00, 0.99       +0.05
acceptance_ttbar                                 +0.01, 0.99        +0.00, 0.99       +0.00
lumi_13TeV                                       -0.05, 0.98        -0.05, 0.98       +0.01
norm_jetFakes                                 ! -0.09, 0.25!     ! -0.09, 0.25!       -0.05
top_pt_ttbar_shape                            * +0.24, 0.69*     * +0.18, 0.70*       +0.23
xsec_Ztautau                                     -0.16, 0.96        -0.16, 0.96       -0.02
xsec_diboson                                     +0.03, 0.99        +0.04, 0.99       -0.02
xsec_ttbar                                       +0.08, 0.94        +0.06, 0.94       +0.02
```

</details>

The numbers in each column are respectively $\frac{\theta-\theta_I}{\sigma_I}$ (often called the **pull**, though note that more than one definition is in use for this), where $\sigma_I$ is the input uncertainty; and the ratio of the post-fit to the pre-fit uncertainty $\frac{\sigma}{\sigma_I}$.

**Tasks and questions:**

  - Which parameter has the largest pull? Which has the tightest constraint?
  - Should we be concerned when a parameter is more strongly constrained than the input uncertainty (i.e. $\frac{\sigma}{\sigma_I}<1.0$)?
  - Check the pulls and constraints on a b-only and s+b asimov dataset instead. This check is [required](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks) for all analyses in the Higgs PAG. It serves both as a closure test (do we fit exactly what signal strength we input?) and a way to check whether there are any infeasibly strong constraints while the analysis is still blind (typical example: something has probably gone wrong if we constrain the luminosity uncertainty to 10% of the input!)

### MC statistical uncertainties

So far there is an important source of uncertainty we have neglected. Our estimates of the backgrounds come either from MC simulation or from sideband regions in data, and in both cases these estimates are subject to a statistical uncertainty on the number of simulated or data events. 
In principle we should include an independent statistical uncertainty for every bin of every process in our model. 
It's important to note that combine/RooFit does not take this into account automatically - statistical fluctuations of the data are implicitly accounted 
for in the likelihood formalism, but statistical uncertainties in the model must be specified by us.

One way to implement these uncertainties is to create a `shape` uncertainty for each bin of each process, in which the up and down histograms have the contents of the bin
 shifted up and down by the $1\sigma$ uncertainty. 
However this makes the likelihood evaluation computationally inefficient, and can lead to a large number of nuisance parameters 
in more complex models. Instead we will use a feature in combine called `autoMCStats` that creates these automatically from the datacard, 
and uses a technique called "Barlow-Beeston-lite" to reduce the number of systematic uncertainties that are created. 
This works on the assumption that for high MC event counts we can model the uncertainty with a Gaussian distribution. Given the uncertainties in different bins are independent, the total uncertainty of several processes in a particular bin is just the sum of $N$ individual Gaussians, which is itself a Gaussian distribution. 
So instead of $N$ nuisance parameters we need only one. This breaks down when the number of events is small and we are not in the Gaussian regime. 
The `autoMCStats` tool has a threshold setting on the number of events below which the the Barlow-Beeston-lite approach is not used, and instead a 
Poisson PDF is used to model per-process uncertainties in that bin.

After reading the full documentation on `autoMCStats` [here](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/bin-wise-stats/), add the corresponding line to your datacard. 
Start by setting a threshold of 0, i.e. `[channel] autoMCStats 0`, to force the use of Barlow-Beeston-lite in all bins.

**Tasks and questions:**

  - Check how much the cross section measurement and uncertainties change using `FitDiagnostics`.
  - It is also useful to check how the expected uncertainty changes using an Asimov dataset, say with `r=10` injected.
  - **Advanced task:** See what happens if the Poisson threshold is increased. Based on your results, what threshold would you recommend for this analysis?

### Nuisance parameter impacts

For this section we're going to use a different datacard - the only reason for this is that what we're going to do next is more informative for a lower mass point (at 200 GeV). So we will first make a new workspace:

```shell
text2workspace.py datacard_part2b.txt -m 200 -o workspace_part2b.root
```

It is often useful to examine in detail the effects the systematic uncertainties have on the signal strength measurement. This is often referred to as calculating the "impact" of each uncertainty. What this means is to determine the shift in the signal strength, with respect to the best-fit, that is induced if a given nuisance parameter is shifted by its $\pm1\sigma$ post-fit uncertainty values. If the signal strength shifts a lot, it tells us that it has a strong dependency on this systematic uncertainty. In fact, what we are measuring here is strongly related to the correlation coefficient between the signal strength and the nuisance parameter. The `MultiDimFit` method has an algorithm for calculating the impact for a given systematic: `--algo impact -P [parameter name]`, but it is typical to use a higher-level script, `combineTool.py` (part of the CombineHarvester package you checked out at the beginning) to automatically run the impacts for all parameters. Full documentation on this is given [here](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#nuisance-parameter-impacts). There is a three step process for running this. First we perform an initial fit for the signal strength and its uncertainty:

```shell
combineTool.py -M Impacts -d workspace_part2b.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --doInitialFit
```
Then we run the impacts for all the nuisance parameters:
```shell
combineTool.py -M Impacts -d workspace_part2b.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --doFits
```
This will take a little bit of time. When finished we collect all the output and convert it to a json file:
```shell
combineTool.py -M Impacts -d workspace_part2b.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --output impacts.json
```
We can then make a plot showing the pulls and parameter impacts, sorted by the largest impact:
```shell
plotImpacts.py -i impacts.json -o impacts
```

**Tasks and questions:**

  - Identify the most important uncertainties using the impacts tool.


