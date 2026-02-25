# test_cache_performance.py
import requests
import time

url = "http://127.0.0.1:8000/api/products/products/"

print("Testing cache performance...\n")

# First request (database)
start = time.time()
response1 = requests.get(url)
time1 = (time.time() - start) * 1000

print(f"1st Request (Database): {time1:.2f}ms")

# Second request (cache)
start = time.time()
response2 = requests.get(url)
time2 = (time.time() - start) * 1000

print(f"2nd Request (Cache):    {time2:.2f}ms")

# Results
speedup = time1 / time2 if time2 > 0 else 0
print(f"\n⚡ Speed improvement: {speedup:.1f}x faster!")
print(f"⏱️  Time saved: {time1 - time2:.2f}ms")