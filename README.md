HOW TO RUN
==========
go the the app.py file location and run python app.py to start the code once the docker compose is up for the feddit api's


PROBLEM_STATEMENT
=================
You are asked to design and develop a small microservice application offering a RESTful API that identifies if comments on a given subfeddit or category are positive or negative.

Given the name of a subfeddit the application should return:
-A list of the most recent comments. Suppose a limit of 25 comments.
-For each comment:
oThe unique identifier of the comment
oThe text of the comment
oThe polarity score and the classification of the comment (positive, or negative) based on that score.

Optionally, you should allow the user to modify the query as follows:
-Filter comments by a specific time range 
-Sort the results by the comments polarity score.
-Define a GitHub workflow to run linting checks and tests for the built RESTful API
