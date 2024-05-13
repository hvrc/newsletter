from lxml import html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from google.cloud import storage
from bs4 import BeautifulSoup
from pathlib import Path
import requests, os, re, json

# google cloud credentials & details
root_dir = os.path.dirname(os.path.abspath(__file__)) 
key_path = "/../static/keys/newsletter-419717-1e2769b5c64d.json"
full_key_path = root_dir + key_path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = full_key_path
bucket = storage.Client().bucket("newsletter_bucket_0")

class Parser():
    def __init__(self, links, template_name, output_name):
        self.content_dict = {}
        self.links = links
        self.template_name = template_name
        self.output_name = output_name

    def normalize_img_href(self, href, size):
        pattern = r"zXlarge"
        return re.sub(pattern, size, href)

    # parse data from links
    def parse(self, headline):

        # request website
        headers = {"zawya-newsletter-app": "RbCsjxCcXtPOsJdm"}
        page = requests.get(headline, headers=headers)
        soup = BeautifulSoup(page.text, "lxml")
        href = headline

        # initialize variables
        img_href = title = subtitle = ""

        # try different methods for each element
        try:
            img_href = self.normalize_img_href(soup.find("meta", {"property": "og:image"})["content"], "zlarge")
        except (TypeError, KeyError, AttributeError):
            try:
                img_href = soup.find("meta", {"property": "og:image"})["content"]
            except (TypeError, KeyError, AttributeError):
                try:
                    img_href = soup.find('meta', {'itemprop': 'thumbnailUrl'})['content']
                except (TypeError, KeyError, AttributeError):
                    img_href = ""

        try:
            title = soup.find("meta", {"property": "og:title"})["content"]
        except (TypeError, KeyError, AttributeError):
            try:
                title = soup.find("meta", {"property": "og:title"}).get("content")
            except (TypeError, KeyError, AttributeError):
                try:
                    title = json.loads(soup.find("script", {"type": "application/ld+json"}).contents[0])["headline"]
                except (TypeError, KeyError, AttributeError):
                    title = ""

        try:
            subtitle = soup.find("meta", {"name": "description"})["content"]
        except (TypeError, KeyError, AttributeError):
            try:
                subtitle = soup.find('meta', {'itemprop': 'description'})['content']
            except (TypeError, KeyError, AttributeError):
                try:
                    subtitle = re.search('"dimension5":"(.*)","dimension3":"', soup.find("script", {"type": "text/javascript"}).contents[0]).group(1)
                except (TypeError, KeyError, AttributeError):
                    subtitle = ""

        return (href, img_href, title, subtitle)

    # create content dictionary
    def generate_elements_dict(self):
        elements = ["href", "img_href", "title", "subtitle"]

        for key, link in enumerate(self.links):
            # print(f"----Processing link {key + 1}----")
            parsed = self.parse(link)

            for elm_key, elm in enumerate(elements):
                self.content_dict[f"_{key+1}_headline_{elm}"] = parsed[elm_key]

    # get user uploaded template stored in the bucket
    def load_jinja_template(self):
        template_blob = bucket.blob(self.template_name)
        template_content = template_blob.download_as_string()
        return template_content.decode('utf-8')

    # output html file with content to bucket
    def output_html_file(self):
        env = Environment(loader=FileSystemLoader(searchpath='/'))
        template_content = self.load_jinja_template()
        template = env.from_string(template_content)
        output = template.render(self.content_dict)
        output_blob = bucket.blob(self.output_name)
        output_blob.upload_from_string(output, content_type="text/html")

        # print(f"HTML file is ready!")