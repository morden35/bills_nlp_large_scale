# Predicting Congressional Bill Passage using Machine Learning and Large-Scale Computing Methods

## Team members:
James Midkiff<br/>
Michelle Orden<br/>
Kelly Yang<br/>

## Introduction

The United States is becoming more politically divided over time, making it more difficult for legislation to gain enough votes to pass and eventually become law. A major factor of whether or not a given bill passes can be attributed to a number of variables outside of the bills itself, such as which party holds majority power at the time of vote, which party holds the presidency, which session of Congress is active at the time the bill is introduced, etc. The passage of a congressional bill is also influenced by characteristics of the text of the bill itself, such as how many words are contained in the bill, <insert a few more characteristcs>. In this project, our group explores how features related to a given bill determine whether or not a bill passes or fails. We do so using a Logistic Regression model, as well as Large-Scale Computing tools such as Dask, PySPark, AWS EMR clusters, and AWS S3 buckets.


## Domain Knowledge

To give some context to the U.S. legislative process, a bill goes through a long process between being introduced in Congress to becoming law. A very small subset of bills introduced in Congress recieve a vote, and fewer bills become law. In the most recently Congress (116th) which ranged from January 3rd, 2019 to January 3rd, 2021, 16,601 bills and resolutions were introduced and proposed to Congress. Of those, only 746 (4%) were voted on, and 344 (2%) were enacted as laws. Our goal is to capture what language/features predict whether or not a bill warrants being passed into law. With such a small percentage of introduced bills ever becoming law, this information could potentially inform members of the House and Senate on how to make their bill of interest more likely to receive a vote and eventually pass.

## Data

Our datasource for this project is https://www.govinfo.gov/. Our initial approach was to collect all bills from this source using their API (https://api.govinfo.gov/docs/). In order to do so, we needed to make 2 separate API calls for each bill. First, in order to identify a bill, we needed to collect the each bill's 'packageId'. Once we had the 'packageId' for a given bill, we could then make a second API call to collect the bill summary and text. We then collected all 'packageId's and their associated bill texts and stored them in a dictionary, which was then stored in an AWS S3 bucket. The code for this process can be found in the following notebook: <insert link to get_bills.ipynb>. We were able to successfuly run this notebook on an EMR cluster using 3 m5xlarge EC2 instances. This allowed us to speed up a very slow data gathering process. Although this notebook worked as expected, we ran into issues with the API due to throttling. The API allows a maximum of 1000 requests per hour for a given API key. With the amount of API requests necessary to gather the data of interest, we had to think of an alternative way to collect the bill texts.

Talk about solution to use bulk data download.

In the end, we were able to collect all bill texts from the 113th (10,637 bills), 114th (12,063 bills), 115th (13,556 bills), and 116th (16,601 bills) congress, which spans from January 3rd, 2013 to January 3, 2021. This accumulated to a total of 52,857 <check that this is correct> bill texts. Future iterations of this project, we would like to complete the analysis using all available bill texts (available bill texts date back to the 103rd Congress, which began on January 5th, 1993).

## Natural Language Processing on Midway using Dask

## Machine Learning on EMR using PySpark

## Conclusion

## Citations

Source for statistics: https://www.govtrack.us/congress/bills/statistics
