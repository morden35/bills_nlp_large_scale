Team members:
James Midkiff
Michelle Orden
Kelly Yang

Source for statistics: https://www.govtrack.us/congress/bills/statistics \
Our planned data source: https://openstates.org/us/bills/

The United States is becoming more politically divided over time, making it more difficult for legislation to gain enough votes to pass and eventually become law. 
A major factor of whether or not a given bill passes is based on many variables, such as which party holds majority power at the time of vote, which party holds 
the presidency, and the particular session of Congress, but the text of the bill itself also matters. Our group will explore if/how language impacts whether or not
bills related to topics such as climate change pass or fail, and if the language of such bills changes over time.

In the most recently completed session of the 116th Congress from 2019 to the start of 2021, 16,601 bills and resolutions were introduced and proposed to Congress.
Of those, 344 were enacted as laws, while another 714 were passed as resolutions and 746 had a major vote. Just in the past 11 months, there have been a total of 
10,488 bills and resolutions introduced to Congress. Our goal is to capture what language/words make a bill significant enough to warrant a vote and subsequent 
passing. To do so, we will look at final versions of bills that have been voted on from 2010-2020 (roughly 10,000 bills total). For these bills, we will analyze 
features such as the most used words, the most unique words, etc, to try and uncover any interesting language patterns over time.

Since we will be working with large volumes of data consisting of arcane text, we will use a number of large-scale computing methods to reduce computational time 
and complexity. For many of our analyses such as sentiment analysis, we can pre-compile our functions using numba to decrease run-times over significant amounts of
text. Additionally, we can set up multiple EC2 clusters to run in parallel over multiple machines, so the overall runtime will be cut by a significant factor. It 
might be possible to implement a pipeline using Spark and utilizing Spark’s NLP library to complete our analysis. Our rough timeline is as follows:

Week of 11/14/21 - 11/20/21:\
Sign up for API keys & familiarize selves with API (everyone)
Make a decision on how to filter data and figure out roughly what size our data will be (everyone)
Choose database type (Dynamo, Redshift, Kinesis stream, etc) (everyone)
Attend Professor’s office hours to check in / ask questions (everyone)\
Week of 11/21/21 - 11/27/21:\
Set up / define data science pipeline (Michelle)
Practice data pipeline with small subset of data (Kelly)\
Week of 11/28/21 - 12/04/21:\
Focus on the analysis / NLP component (James)
Try running pipeline with larger subset / entire data (Michelle)
Start working on the README and visualizations (everyone)\
Week of 12/05/21 - 12/10/21:\
Make video presentation (everyone)
Finish README (everyone)







Week Tasks\
11/14/21 - 11/20/21\
Sign up for API keys & familiarize selves with API (everyone)
Make a decision on how to filter data and figure out roughly what size our data will be (everyone)
Choose database type (Dynamo, Redshift, Kinesis stream, etc) (everyone)
Attend Professor’s office hours to check in / ask questions (everyone)\
11/21/21 - 11/27/21\
Set up / define data science pipeline (Michelle)
Practice data pipeline with small subset of data (Kelly)\
11/28/21 - 12/04/21\
Focus on the analysis / NLP component (James)
Try running pipeline with larger subset / entire data (Michelle)
Start working on the README and visualizations (everyone)\
12/05/21 - 2/10/21\
Make video presentation (everyone)
Finish README (everyone)


Topic Idea:\
Michelle: Natural Language processing of Bill text
Can specifically follow iterations/versions of the recently passed infrastructure bill (H.R. 3684) using Open States data
For a specific bill, compare the words used in each iteration/version of bill over time (bill that passed)

Can analyze words for all passed/failed bills for specific state over time (or all federal bills)
Using the final version of 10,000, compare the ones that passed vs ones that didnt, and look at the words used over time

For a single bill, what words are important (comparing bill versions) for that given bill to pass.
For all bills related to a given topic (say climate), how do important words change over time?
Pork?!!?



Large-Scale Computing methods we might want to consider:\
Pre-compiled functions (numba)
Set up an sns to alert new bills? (this probably isn’t super necessary)
Multiple clusters running in parallel

Logistic Ideas:\
Set up weekly group meeting day/time
Plan to meet with Prof to talk about ideas

Meeting 11/21\
Michelle working on API results - she’s currently limited to getting 10,000 bills, of which 150 are cl/imate related. 
She calls once for the bill id’s filtering on ‘climate’


James wants a few examples of bills to work with to start on the NLP side of things. 


