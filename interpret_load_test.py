import csv
import os
import requests
import dotenv
import time
import sys
import requests
import csv
import boto3
import github_helper

from dotenv import load_dotenv
load_dotenv()

PASSING_MEDIAN_RESPONSE=200
PASSING_AVERAGE_RESPONSE=200
PASSING_FAILURE_COUNT=10
PASSING_NUMBER_REQUESTS=144             # Total number mins = 144 * 5 = 720 = 12 hours
PASSING_NUMBER_REQUESTS_DEV=5    


STABLE_RELEASES_FILE = "stable_releases.txt"
UNSTABLE_RELEASES_FILE = "unstable_releases.txt"


def interpret_results(csv_file, test_name=None):
    with open(csv_file, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        rows = list(csvreader)
        """
        in this csv reader
        - Create 1 new column "Status"
        - if a row has a median response time < 300 and an average response time < 300, Status = "Passed ✅"
        - if a row has a median response time >= 300 or an average response time >= 300, Status = "Failed ❌"
        - Order the table in this order Name, Status, Median Response Time, Average Response Time, Requests/s,Failures/s, Min Response Time, Max Response Time, all other columns
        """

        # Add a new column "Status"

        for row in rows:
            median_response_time = float(
                row["Median Response Time"].strip().rstrip("ms")
            )
            average_response_time = float(
                row["Average Response Time"].strip().rstrip("s")
            )

            row["Test-Name"] = test_name

            request_count = int(row["Request Count"])
            failure_count = int(row["Failure Count"])
            success_count = request_count - failure_count

            if (success_count == 50):
                row["Status"] = "Passed ✅"
            else:
                row["Status"] = "Failed ❌"

        results = "\n"
        # Construct Markdown table rows
        for row in rows:
            name = row["Name"]
            status = row["Status"]
            median_response_time = row["Median Response Time"]
            average_response_time = row["Average Response Time"]
            requests_per_second = row["Requests/s"]
            failures_per_second = row["Failures/s"]
            request_count = row["Request Count"]
            failure_count = row["Failure Count"]

            result = f"""
                Current Time: {time.strftime("%m-%d %H:%M:%S")}
                Name: {name}
                Status: {status}    
                Median Response Time: {median_response_time}
                Average Response Time: {average_response_time}
                Requests/s: {requests_per_second}
                Failures/s: {failures_per_second}
                Request Count: {request_count}
                Failure Count: {failure_count}
            \n\n    
            """

            results += result

        return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 interpret_load_test.py <test_name>")
        sys.exit(1)

    test_name = sys.argv[1]
    print("Interpreting results for test: " + test_name)
    csv_file = "load_test_stats.csv"  # Change this to the path of your CSV file
    markdown_table = interpret_results(
        csv_file, 
        test_name=test_name
    )
    print(markdown_table)
    markdown_table = "\nTest Name: " + f"`{test_name}`\n" + markdown_table


    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
    if slack_webhook_url is None:
        raise Exception("Missing SLACK_WEBHOOK_URL from environment")
    
    payload = {"text": markdown_table}
    headers = {"Content-type": "application/json"}


    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
    if slack_webhook_url is None:
        raise Exception("Missing SLACK_WEBHOOK_URL from environment")

    payload = {"text": markdown_table}
    headers = {"Content-type": "application/json"}

    response = requests.post(slack_webhook_url, json=payload, headers=headers)

    if response.status_code == 200:
        pass    