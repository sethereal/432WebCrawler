import sys
import argparse
from methods import WebpageCrawler, WebContentProcessor

def main():
    parser = argparse.ArgumentParser(description="Webpage Crawler")
    parser.add_argument("action", choices=["crawl", "process"], help="Choose action: crawl or process")

    args = parser.parse_args()

    if args.action == "crawl":
      
        if len(sys.argv) != 3:
            print("Usage: python3 main.py crawl <seed_webpage_uri>")
            sys.exit(1)

        seed_webpage = sys.argv[2]

      
        crawler = WebpageCrawler(seed_webpage)
        crawler.crawl()
       
        processor = WebContentProcessor("./raw", "./processed")
        processor.hash_uris("./data/unique_uris.txt")

    elif args.action == "process":
        processor = WebContentProcessor()

        uris = processor.hash_to_uri('./data/hash_dir.txt', './data/uri_hash.json')
    
        processor.process_webpages(input_file='./data/uris_to_hash.txt', output_file='./data/TFIDF_values.txt')

if __name__ == "__main__":
    main()
