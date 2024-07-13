from dataclasses import dataclass
from enum import Enum
import requests

class VscoMediaType(Enum):
    IMAGE = 0
    VIDEO_M3U8 = 1
    VIDEO_MP4 = 2

@dataclass
class VscoMedia:
    type: VscoMediaType
    download_url: str
    timestamp: int
    
headers = {
        'authority': 'vsco.co',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer 7356455548d0a1d886db010883388d08be84d0c9',
        'content-type': 'application/json',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'x-client-build': '1',
        'x-client-platform': 'web'}

bearer_token = 'Bearer 7356455548d0a1d886db010883388d08be84d0c9'

def set_bearer_token(value: str):
    '''
    By default, the guest bearer token is used, but you may use your own with this method.
    
    `value` should be the entire authorization header (ie. 'Bearer xxxxxxx...').
    '''
    global bearer_token
    bearer_token = value
    headers['authorization'] = bearer_token
    
def get_site_id(username: str, strict: bool = False) -> str | None:
    '''
    Returns the site_id for the first profile returned by searching for `username`.
    
    If `strict` is true, returns `None` if the returned profile's username does not equal `username`.
    
    Also returns `None` if no profiles are returned.
    
    Raises `HTTPError` on `response.raise_for_status()`.
    '''
    global headers
    response = requests.get(
        url='https://vsco.co/api/2.0/search/grids',
        headers=headers,
        params={
            'query': username,
            'page': 0,
            'size': 7
        })
    
    response.raise_for_status()
    profiles = response.json()['results']
    if len(profiles) == 0:
        return None
    
    return profiles[0]['siteId'] if not strict or profiles[0]['siteSubDomain'] == username else None

def get_media_page(site_id: str, cursor: str | None = None) -> tuple[list[VscoMedia], str]:
    '''
    Returns a tuple containing a list of posts in a page and a cursor string for the next page.
    
    Raises `HTTPError` on `response.raise_for_status()`.
    '''
    global headers
    params = {
        'site_id': site_id,
        'limit': 20
    }
    if cursor: params['cursor'] = cursor
    
    response = requests.get(
        url=f'https://vsco.co/api/3.0/medias/profile',
        headers=headers,
        params=params)
    
    response.raise_for_status()
    response = response.json()
    posts = [
        (
            VscoMedia(VscoMediaType.IMAGE, f'https://{media[media['type']]['responsive_url']}', media[media['type']]['upload_date'])
            if not media[media['type']]['is_video']
            else VscoMedia(VscoMediaType.VIDEO_MP4, f'https://{media[media['type']]['video_url']}', media[media['type']]['upload_date'])
        ) 
        if media['type'] == 'image' 
        else VscoMedia(VscoMediaType.VIDEO_M3U8, media[media['type']]['playback_url'], media[media['type']]['created_date'])
        for media in response['media']]
    return (posts, response.get('next_cursor'))

class ProfileIterator:
    def __init__(self, site_id: str) -> None:
        self.cursor = None
        self.medias = []
        self.site_id = site_id
        self.end_reached = False
        
    def __iter__(self):
        self.cursor = None
        self.medias = []
        self.end_reached = False
        return self
    
    def __next__(self):
        if self.end_reached:
            raise StopIteration
        
        old_cursor = self.cursor
        self.medias, self.cursor = get_media_page(self.site_id, self.cursor)
        
        if self.cursor == None:
            self.end_reached = True
        elif self.cursor == old_cursor: 
            raise StopIteration
        
        return self.medias
