# Cognitive Modeling Environment

This package contains the code framework for the environment used for the
Cognitive Modeling seminar in WS 2018/2019 
(https://ekvv.uni-bielefeld.de/kvv_publ/publ/vd?id=135109752).

It is strongly recommended to use a Python environment (virtualenv, conda env, 
etc)!

## Requirements

The environment does not have any third party requirements. But the simplest
visualization requires matplotlib (will be automatically installed by the
```setup.py```). A more advanced visualization can be used, when ```pygame```
is available on the system, which can be installed using:

```
pip install pygame
```

## Installation

```
python setup.py install
```

## Documentation

You can find API documentation in the ```doc``` folder.
Just run the ```index.html``` and you should find the generated documentation
for the module.

## Data

This repository contains human navigation behavior data data collected in a 
study by Jan Pöppel, originally published as supplementary material to the paper
"Satisficing Models of Bayesian Theory of Mind for Explaining Behavior of
Differnetly Uncertain Agents" by Pöppel and Kopp 
(https://pub.uni-bielefeld.de/record/2917285).

## Usage

You can furthermore find a couple of example of how you can use the package
in the ```example.py```.