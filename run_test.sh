#!/bin/bash

function run_no_cache_hits_locust_test() {
    locust -f no_cache_hits.py --headless -u 20 -r 20 -H http://34.106.146.156/ -t 300 --csv load_test
}

# Deploy your project (assuming deployment commands are here)
# Replace the following line with your deployment commands
echo "Deploying your project..."

# print content in current dir 
ls -lAh

# Run tests indefinitely
while true; do
    echo "Running tests..."

    # # Wait for 20 seconds
    # echo "Waiting for 20 seconds..."
    # sleep 20

    # # No cache hits test
    run_no_cache_hits_locust_test

    # Run the load test script again
    python3 interpret_load_test.py no_cache_hits

done
