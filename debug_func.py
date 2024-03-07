# test_functions.py

from webCrawler.methods import WebpageCrawler, WebContentProcessor, Calculate

def test_crawl():
    # Create an instance of the WebpageCrawler class
    crawler = WebpageCrawler("seed_webpage")
    # Call the crawl method and check the results
    crawler.crawl()
    

def test_processor():
    # Create an instance of the WebContentProcessor class
    processor = WebContentProcessor("./raw", "./processed")

    # Call the hash_uris method and check the results
    processor.hash_uris("unique_uris.txt")

 

def test_h2u():
    processor = WebContentProcessor()
    # Call the hash_to_uri method and check the results
    processor.hash_to_uri("output.txt", "uri_hash.txt")
   

def test_cal():
    # Create an instance of the Calculate class
    calculate_val = Calculate("output.txt", "word")
   
