# Predicting Congressional Bill Outcomes using Machine Learning and Large-Scale Computing Methods

## Team members:
James Midkiff<br/>
Michelle Orden<br/>
Kelly Yang<br/>

## Introduction

The United States is becoming more politically divided over time, making it more difficult for legislation to gain enough votes to pass and eventually become law. A major factor of whether or not a given bill passes can be attributed to a number of variables outside of the bills itself, such as which party holds majority power at the time of vote, which party holds the presidency, which session of Congress is active at the time the bill is introduced, etc. The passage of a congressional bill is also influenced by characteristics of the text of the bill itself, such as how many words are contained in the bill, the number of sections in the bill, and the number of sponsors the bill has. In this project, our group explores how features related to a given bill determine whether or not a bill passes or fails. We do so using a Logistic Regression model, as well as Large-Scale Computing tools such as Dask, PySPark, AWS EMR clusters, and AWS S3 buckets.


## Domain Knowledge

To give some context to the U.S. legislative process, a bill goes through a long process between being introduced in Congress to becoming law. A very small subset of bills introduced in Congress receive a vote, and fewer bills become law. In the most recent Congress (116th) which ranged from January 3rd, 2019 to January 3rd, 2021, 16,601 bills and resolutions were introduced and proposed to Congress. Of those, only 746 (4%) were voted on, and 344 (2%) were enacted as laws. Our goal is to capture what language/features predict whether or not a bill warrants being passed into law. With such a small percentage of introduced bills ever becoming law, this information could potentially inform members of the House and Senate on how to make their bill of interest more likely to receive a vote and eventually pass.

## Data

All data for this project was stored in an AWS S3 bucket. The code to set up the bucket can be found in the following notebook: <insert link to s3_set_up.ipynb>.

Our datasource for this project is https://www.govinfo.gov/. Our initial approach was to collect all bills from this source using their API (https://api.govinfo.gov/docs/). In order to do so, we needed to make 2 separate API calls for each bill. First, in order to identify a bill, we needed to collect the each bill's 'packageId'. Once we had the 'packageId' for a given bill, we could then make a second API call to collect the bill summary and text. We then collected all 'packageId's and their associated bill texts and stored them in a dictionary, which was then stored in an AWS S3 bucket. The code for this process can be found in the following notebook: <insert link to get_bills.ipynb>. We were able to successfully run this notebook on an EMR cluster using 3 m5.xlarge EC2 instances. This allowed us to speed up a very slow data gathering process. Although this notebook worked as expected, we ran into issues with the API due to throttling. The API allows a maximum of 1000 requests per hour for a given API key. With the amount of API requests necessary to gather the data of interest, we had to think of an alternative way to collect the bill texts.

Fortunately, our datasource has a Bulk Data Repository (https://www.govinfo.gov/bulkdata). We were able to download zip files containing all bill texts for the 113th-116th Congress in xml format. We then directly uploaded these xml files to the S3 bucket. In order to make this data easier to pull into Dask, we converted the xml files to a dictionary/json representation. To do so, we connected to the S3 bucket via boto3 in a notebook that ran on an EMR cluster. This EMR cluster only required 1 m4.xlarge EC2 instance. We then iterated through each xml file and decoded the file into a utf8 string. All bill text strings were then added to a dictionary, and pushed back to the S3 bucket for storage. The code for this process can be found in the following notebook: <insert link to convert_xml.ipynb>.

Additionally, we decided to keep only House and Senate bills, and filter our resolutions. Ultimately, we were able to collect all House and Senate bill texts from the 113th (11,479 bills), 114th (13,541 bills), 115th (15,527 bills), and 116th (17,452 bills) congress, which spans from January 3rd, 2013 to January 3, 2021. This accumulated to a total of 57,999 bill texts. In future iterations of this project, we would like to complete the analysis using all available bill texts (available bill texts date back to the 103rd Congress, which began on January 5th, 1993).

## Natural Language Processing on Midway using Dask

## Machine Learning on EMR using PySpark

## Conclusion
  
## Project Breakdown:
Kelly: Conducted sentiment analysis on bill text for feature creation. Once the bills were loaded in together, prepped the datasets, consolidated the frames, and vector assembled the features. Then read it into a PySpark DataFrame via AWS on an EMR Cluster. Created and ran the Logistic Regression Machine Learning Model with our dataset and tested the predictive model. Reported various metrics, created a confusion matrix, and computed accuracy scores.

## Citations
  

Source for statistics: https://www.govtrack.us/congress/bills/statistics
