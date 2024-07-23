# SNDrome
Stockholm Syndrome SN Project to test Light Curve Fitters in a Model Independent Framework

# Problem
How can SN Ia fitters be compared against each other fairly?
A large quantity of data is required to evaluate the performance of a fitter over the diversity of SNe Ia.
It's difficult to get a representative sample of SNe Ia without simulations, but simulations must assume a specific model to generate data.
Evaluating a model using simulations based on that model will be naturally biased.

# Proposal
## Generating simulation-like quantities of almost real data.
Gaussian Processes provide a model-agnostic way of augmenting a sample of light curves by providing a reasonable estimate of their functional forms.
Alternatives include sub-sampling the light curves, a more naive interpolation method (e.g. splines + random error), or machine learning solutions.
## Augmenting light curves
The spoofed light curves can be augmented in a number of ways, such as by varying temporal or wavelength coverage, adding known instrumental or calibration systematics, or by applying reasonably well-understood transformations like altering the redshift.
These spoofed light curves cannot be directly augmented in model-specific ways, such as by varying $x_1$ $c$, $s_{BV}$, or $\theta$.
## Evaluating fitter performance
Any SN Ia fitter can be deployed on the sample of light curves and its performance can be quantified as a function of any of the augmented parameters.
The quantification could be something naive like a reduced $\chi^2$, but should probably be a more sophisticated Figure of Merit (FoM) that will need to be defined.
This FoM may not be a single metric, but rather take different forms based on the desired science (e.g. dust analyses, Hubble diagrams, early-time modeling, etc.).

# Ideal Outcome
## Identifying the right tool for the job
The idiosyncrasies of the currently available SNe Ia fitters will likely not yield an objectively optimal fitter unless the FoM is singular and narrowly defined.
However, it would be useful to determine which fitters are most/least sensitive to specific variations and excel/struggle in different contexts.
As an example, fitter A may produce the lowest scatter in Hubble residuals with densely-sampled light curves while fitter B may suffer fewer catastrophic errors when fitting sparsely-sampled light curves.
## Identifying areas for development
A model-independent set of light curves should deviate from the models assumed in any fitting program with sufficiently extreme augmentation, but the specific modes of failure could be used to identify areas in need of improvement.
As an example, fitter C may underestimate its errors as color is varied, which could indicate a limitation to the validity of mangling or an issue in how reddening is calculated.
