# between-the-lines
## Project in Programming and Data Sciences - 177-1218_FA21 TECH-UB 24 001-2 
## Professor Joao Sedoc

***Web application to render more transparent and approachable privacy policies. Functionalities include privacy policy summarization, similarity analysis, readability score, and topic modeling.***

In a nutshell, a user can type in the url/name of the website in order to analyse the privacy policies.

## Problem
**Privacy policies are filled with jargon and are not made for the average user.**
> 65% of personal data will be covered under a privacy regulation by 2023 (Gartner Inc.)

**Users have lost control over how their data is collected and where their data is stored.**
> 79% of respondents are concerned about how companies are using their personal data (Pew Research)


## Solution
1. Help the user understand how a privacy policy compares in terms of major companies privacy policies' using a sentence transformers ML model
2. Summarize privacy policies in a way that is user friendly and readable using ML summarization models
3. Identify common topics across data policies through LDA topic modeling

## Target Customer
**Internet Users**
Primary age group 15-40 due to frequency of internet usage that poses privacy vulnerabilities

## Features
### Summarization
> We used the t5 transfer learning model to generate summarizations for the policies.
### Similarity Analysis
> We used a sentence transformers model to generate text embedding to generate scores based on semantic similarity
### Readability
> Generate FleschKincaid score for the privacy policies to determine their grade level
### Topic Modeling
> The task of identifying topics that best describes our database of privacy policies

## How to run

To run this program, go to the designated directory and type in your terminal:

```
python ppds.py
```

The following images are a preview of the homepage:

<img width="1440" alt="Screen Shot 2021-12-25 at 9 59 24 AM" src="https://user-images.githubusercontent.com/24204239/147375275-c2c599bf-2203-4be1-8f90-55e1785900a6.png">

<img width="1433" alt="Screen Shot 2021-12-25 at 9 59 37 AM" src="https://user-images.githubusercontent.com/24204239/147375276-a9ec0275-bbdd-4726-9865-e39a8a647cd2.png">

<img width="1439" alt="Screen Shot 2021-12-25 at 9 59 50 AM" src="https://user-images.githubusercontent.com/24204239/147375278-7ada5178-6bd3-4391-b060-f1d63175581c.png">

