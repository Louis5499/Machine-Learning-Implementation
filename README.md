# Introduction to Machine Learning
NTHU CS 460200

During the course, we implement three kinds of ML techniques and separately apply to medical data.

### HW1 Regression Problem
Predict the dead rates for each contry according to past 30 dead rates dataset

- Techniques: Linear Regression / Auto Regression

### HW2 Classification Problem
Predict the dead possibility of each patient by their medical examination report

Techniques: Random Forest / Xgboost / **Neural Network**

### HW3 Image Classification Problem
Predict the dead possibility of each patient by chest X-Ray Images

Techniques: **CNN**


### Final Project
Predict the identity of anonymous users on social application(Dcard)

In this project, I mainly in charge of data preprocessing (Web crawling \ Word breaking \ TF-IDF-PF Calculation \ Bi-words analysis)


#### How to install & run final project code?
**CkipTagger is a project from ckip lab, so please be aware of license restriction, which are elaborated in their github repo README.md.**

Your Python should >=3.6


1. Go to [CkipTagger Github web](https://github.com/ckiplab/ckiptagger), download `iis-ckip` dataset, and put the `./data` directory at the root of the `final` folder.

2. Install CKIP-Tagger
If you are python 3 user, Please enter:
```shell
pip3 install -U ckiptagger[tf,gdown]
```
If you are python 2 user, Please enter:
```shell
pip3 install -U ckiptagger[tf,gdown]
```

3. Run `python3 tfidf.py` or `python tfidf.py`