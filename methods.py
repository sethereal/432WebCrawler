import glob
import math
import os
import requests
import hashlib
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from boilerpy3 import extractors as ext
from tabulate import tabulate
from scipy.stats import kendalltau




class WebpageCrawler:
    """Class for crawling webpages and extracting unique URIs."""

    def __init__(self, seed_webpage, max_uris=500):
        """Initialize the WebpageCrawler.

        Parameters:
        - seed_webpage (str): The starting webpage for crawling.
        - max_uris (int): Maximum number of unique URIs to extract.
        """
        self.seed_webpage = seed_webpage
        self.max_uris = max_uris


    def crawl(self):
        """Crawl webpages and extract unique URIs."""
        unique_uris = set()
        to_visit = [self.seed_webpage]

        link_extractor = LinkExtractor(self.seed_webpage, unique_uris)
        while len(unique_uris) < self.max_uris and to_visit:
            current_url = to_visit.pop(0)

            try:
                response = requests.get(current_url, timeout=10)  # 
                response.raise_for_status()  
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                
                link_extractor.extract_links(soup, to_visit)


            except requests.Timeout:
                print(f"Timeout occurred while processing {current_url}")
            except requests.RequestException as e:
                print(f"An error has occurred while processing {current_url}: {e}")
                continue  


        print("\n")
        print(f"Generated {len(unique_uris)} unique URIs")

        file_writer = FileWriter()
        file_writer.write_to_file("./data/unique_uris.txt", unique_uris)
        file_writer.write_to_file("./data/seed_uri.txt", to_visit)


    
class LinkExtractor:
    """Class for extracting links from HTML."""

    def __init__(self, base_url, unique_uris):
        """Initialize the LinkExtractor.

        Parameters:
        - base_url (str): The base URL for resolving relative links.
        - unique_uris (set): A set to store unique URIs.
        """
        self.base_url = base_url
        self.unique_uris = unique_uris
        self.urlCounter = 0


    def extract_links(self, soup, to_visit):
        """Extract links from HTML and add them to the to_visit list.

        Parameters:
        - soup (BeautifulSoup): The BeautifulSoup object representing the HTML.
        - to_visit (list): The list of URIs to visit.
        """
        
        for link in soup.find_all("a"):
            uri = link.get("href")
            uri = urljoin(self.base_url, uri)

            if uri.startswith("https://"):
                print(f"Processing...  {uri}")
                
                self.process_uri(uri, to_visit)

            

    def process_uri(self, uri, to_visit):
        """Process a URI and add it to the unique_uris set if it meets criteria.

        Parameters:
        - uri (str): The URI to process.
        - to_visit (list): The list of URIs to visit.
        """
        try:
            response = requests.get(uri, timeout=10, allow_redirects=True)
            response.raise_for_status()  

            if response.headers.get("Content-Type", "").startswith("text/html"):
                content_length = int(response.headers.get("Content-Length", "0"))
                if content_length > 1000:
                    f_uri = response.url
                    self.unique_uris.add(f_uri)
                    to_visit.append(f_uri)
                    self.urlCounter += 1
                    if self.urlCounter % 50 == 0:
                        print(f"Total number of unique URIs processed: {self.urlCounter}")

        except requests.Timeout:
            print(f"Timeout occurred while processing {uri}")
        except requests.RequestException as e:
            print(f"An error has occurred while processing {uri}: {e}")
            return



class WebContentProcessor:
    """Class for processing web content."""

    def __init__(self, raw_dir = './', processed_dir = './'):
        """Initialize the WebContentProcessor.

        Parameters:
        - raw_dir (str): The directory to store raw HTML content.
        - processed_dir (str): The directory to store processed HTML content.
        """
        self.file_writer = FileWriter(raw_dir, processed_dir)
        self.extractor = ext.ArticleExtractor()
        self.uri_hash = {} 


    def get_html_hash(self, uri):
        """Get the hash of the HTML content from a URI.

        Parameters:
        - uri (str): The URI to fetch HTML content from.

        Returns:
        - tuple: A tuple containing the HTML content and its MD5 hash.
        """
        try:
            response = requests.get(uri, timeout=5)
            html_content = response.text if response.status_code == 200 else ""

            hash_object = hashlib.md5(html_content.encode())
            md5_hash = hash_object.hexdigest()

            return html_content, md5_hash

        except Exception as e:
            print(f"Error occurred while processing {uri}: {e}")
            raise


    def hash_uris(self, output_file):
        """Hash URIs from a file and write URI hash information to a file.

        Parameters:
        - filename (str): The name of the file containing URIs to hash.
        """
        self.uri_hash = {uri: hash(uri) for uri in self.unique_uris}

        with open(output_file, 'w') as f:
            json.dump(self.uri_hash, f)


    def hash_to_uri(self, hash_file, uri_hash_file):
        """Convert hashed URIs back to original URIs.

        Parameters:
        - hash_file (str): The file containing hashed URIs.
        - uri_hash_file (str): The file containing URI hash information.

        Returns:
        - list: List of original URIs.
        """
        with open(uri_hash_file, 'r') as f:
            self.uri_hash = json.load(f)

        with open(hash_file, 'r', encoding='utf-8') as f:
            hashes = f.read().splitlines()

        hashes = [h.replace('.txt', '') for h in hashes]
    
        uris = []
        for h in hashes:
            for uri, hash in self.uri_hash.items():
                if h == hash:
                    uris.append(uri)
                    break
            else:
                uris.append('Unknown URI')
      
        if self.file_writer:
            self.file_writer.write_to_file('./data/uris_to_hash.txt', uris)

        return uris


    def process_webpages(self, input_file, output_file):
        """Process webpages, calculate TF-IDF, and write results to a file.

        Parameters:
        - input_file (str): The file containing URIs to process.
        - output_file (str): The file to write the TF-IDF results to.
        """
        with open(input_file, 'r') as f:
            files_to_process = [line.strip() for line in f]

        results = []
        tf_ranks = []
        tf_idf_ranks = []

        query_word = input("Please enter a query word: ")
        self.query_files(query_word)

     
        df_tb = input("Please enter the df_t value: ")
        df_t = int(df_tb.replace(",", ""))

        for uri in files_to_process:
            content = self.fetch_content(uri)  
            calculate_val = Calculate(self.uri_hash, [content], df_t) 

            tfidf_result = calculate_val.compute_tf_idf(query_word)
    
            if tfidf_result is not None:
                tf_values, idf_value, tfidf_values = tfidf_result
                tf_ranks.append(tf_values[0])
                tf_idf_ranks.append(tfidf_values[0])
                results.append((uri, tf_values[0], idf_value, tfidf_values[0]))

        #Extra Credit
        tau, p_value = kendalltau(tf_ranks, tf_idf_ranks)
        print(f"Kendall's Tau: {tau}")
        print(f"P-value: {p_value}")
   
                        

        with open(output_file, 'w') as f:
         f.write(tabulate(results, headers=["URI", "TF", "IDF", "TF-IDF"], tablefmt='plain'))


    def query_files(self, query_word):
        """Query files for a specific word and store matching filenames.

        Parameters:
        - query_word (str): The word to search for in the files.
        - input_directory (str): The directory containing the processed files.
        - output_file (str): The file to store matching filenames.
        """

        files = glob.glob('./processed/*.txt')

        matching_files = []

        for filename in files:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if query_word in content:
                    clean_filename = os.path.basename(filename).replace('.txt', '')
                    matching_files.append(clean_filename)

       
        with open('./data/hash_dir.txt', 'w') as f:
            for filename in matching_files:
                f.write(filename + '\n')
                

    def fetch_content(self, uri):
        """Fetch content from a processed file based on URI.

        Parameters:
        - uri (str): The URI to fetch content for.

        Returns:
        - str: Content of the processed file.
        """

        hash = self.uri_hash[uri]

        with open(f'./processed/{hash}.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    

    def strip_boilerplate(self, uri, raw_html_content, md5_hash):
        """Strip boilerplate from raw HTML content and write raw and processed content to files.

        Parameters:
        - uri (str): The URI being processed.
        - raw_html_content (str): The raw HTML content to strip boilerplate from.
        - md5_hash (str): The MD5 hash of the raw HTML content.
        """
        try:
            print(f"Processing URI: {uri}")

            print(f"Writing Raw HTML to file for {md5_hash}")
            self.file_writer.write_raw_html_to_file(md5_hash, raw_html_content)

            try:
                content = self.extractor.get_content(raw_html_content)
            except ext.HTMLExtractionError:
                print(f"Failed to extract content from {uri}")
                content = ""

            if not content.strip():
                print(f"No useful content found in {uri}")
                return

            print(f"Writing Processed HTML to file for {md5_hash}")
            self.file_writer.write_processed_html_to_file(md5_hash, content)

        except Exception as e:
            print(f"An error occurred while processing {uri}: {e}")



class Calculate:
    def __init__(self, uri_hash, contents, df_t):
        self.uri_hash = uri_hash
        self.contents = contents
        self.df_t = df_t

    def compute_tf(self, content, term):
        """Compute the TF value for a term in a given content.

        Parameters:
        - content (str): The content to calculate TF for.
        - term (str): The term for which TF is calculated.

        Returns:
        - float: TF value.
        """
        return content.count(term) / len(content.split())


    def compute_idf(self, term):
        """Compute the IDF value for a term.

        Parameters:
        - term (str): The term for which IDF is calculated.

        Returns:
        - float: IDF value.
        """
        N = 40000000000
        df_t = self.df_t
        return math.log(N / (df_t + 1)) + 1


    def compute_tf_idf(self, term):
        """Compute TF-IDF values for a term in the given content.

        Parameters:
        - term (str): The term for which TF-IDF is calculated.

        Returns:
        - tuple: A tuple containing TF values, IDF value, and TF-IDF values.
        """
        tf_values = [self.compute_tf(content, term) for content in self.contents]
        idf_t = self.compute_idf(term)
        tfidf_values = [tf * idf_t for tf in tf_values]


        #Debug
        #print(f"TF values for {term}: {tf_values}")
        #print(f"IDF value for {term}: {idf_t}")
        #print(f"TF-IDF values for {term}: {tfidf_values}")

        return tf_values, idf_t, tfidf_values

        


class FileWriter:
    """Class for writing files."""

    def __init__(self, raw_dir="raw", processed_dir="processed"):
        """Initialize the FileWriter.

        Parameters:
        - raw_dir (str): The directory to store raw HTML content.
        - processed_dir (str): The directory to store processed HTML content.
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir


    def write_to_file(self, filename, data, output_dir="."):
        """Write data to a file.

        Parameters:
        - filename (str): The name of the file to write data to.
        - data (iterable): The data to write to the file.
        - output_dir (str): The directory where the file should be stored.
        """
        with open(f"{output_dir}/{filename}", "w",  encoding="utf-8") as f:
            for item in data:
                f.write(item + "\n")

    def write_raw_html_to_file(self, hash, content):
        """Write raw HTML content to a file.

        Parameters:
        - hash (str): The MD5 hash of the raw HTML content.
        - content (str): The raw HTML content to write to the file.
        """
        with open(f"{self.raw_dir}/{hash}.txt", "w", encoding="utf-8") as f:
            f.write(content)


    def write_processed_html_to_file(self, hash, content):
        """Write processed HTML content to a file.

        Parameters:
        - hash (str): The MD5 hash of the processed HTML content.
        - content (str): The processed HTML content to write to the file.
        """
        with open(f"{self.processed_dir}/{hash}.txt", "w", encoding="utf-8") as f:
            f.write(content)



