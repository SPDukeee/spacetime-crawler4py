import re, hashlib
from urllib.parse import urlparse
from html.parser import HTMLParser


visited_urls = set()
visited_content_hashes = set()
content_length_threshold = 1048576*1024 # 1GB

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

#help class for extract_next_links()
class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])

                    
def extract_next_links(url, resp):
    parser = LinkExtractor()
    parser.feed(resp.content.decode())
    return parser.links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        # Check if URL has already been visited
        if url in visited_urls:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        # Check if page has already been visited (using fingerprinting)
        if parsed.netloc in visited_content_hashes:
            return False
        # Check if URL is dead (status code is 200 and content length is 0)
        if resp.status == 200 and len(resp.raw_response.content) == 0:
            return False
        # Check if page has no content or too much content
        if len(resp.content) == 0 or len(resp.content) > content_length_threshold:
            return False
        # Add visited urls
        visited_urls.add(parsed.netloc)
        # Create and add visited content hash
        content_hash = hashlib.sha1(url.encode())
        visited_content_hashes.add(content_hash)
        return True
        
        

    except TypeError:
        print ("TypeError for ", parsed)
        raise
