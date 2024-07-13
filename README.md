# Vsco Api

A python package that provides convenient functions for grabbing user posts.

## Installation
```bash
pip install vsco-api
```

## Sample Usage
```python
import vsco_api
import time

# Use the authorization token of your own account
vsco_api.set_bearer_token('Bearer xxxxxxx...')

# Get site id by username
site_id = vsco_api.get_site_id('username here')

# Get the first page of posts
page, next_cursor = vsco_api.get_media_page(site_id)

# Iterate through all pages of posts
for page in vsco_api.ProfileIterator(site_id):
    for post in page:
        print(post.download_url, post.timestamp, post.type)
        is_image = post.type == vsco_api.VscoMediaType.IMAGE
        
    time.sleep(5)

```
