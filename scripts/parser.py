from lxml import html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup
from pathlib import Path
import requests, os, re, json

class Parser():
    def __init__(self, links, template_dir, template_name, output_path):
        self.content_dict = {}
        self.links = links
        self.template_dir = template_dir
        self.template_name = template_name
        self.output_path = output_path

    def normalize_img_href(self, href, size):
        pattern = r"zXlarge"
        return re.sub(pattern, size, href)

    def parse_headline(self, headline):
        # request website
        headers = {"zawya-newsletter-app": "RbCsjxCcXtPOsJdm"}
        page = requests.get(headline, headers=headers)
        soup = BeautifulSoup(page.text, "lxml")
        href = headline

        # Initialize variables
        img_href = title = subtitle = ""

        # Try different methods for each element
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


    def generate_elements_dict(self):
        elements = ["href", "img_href", "title", "subtitle"]

        for key, link in enumerate(self.links):
            # print(f"----Processing link {key + 1}----")
            parsed = self.parse_headline(link)

            for elm_key, elm in enumerate(elements):
                self.content_dict[f"_{key+1}_headline_{elm}"] = parsed[elm_key]

    def load_jinja_template(self):
        env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))
        template = env.get_template(self.template_name)
        return template

    def output_html_file(self):
        filename = self.output_path
        template = self.load_jinja_template()
        output = template.render(self.content_dict)

        with open(filename, 'w', encoding="utf-8") as fh:
            fh.write(output)

        # print(f"HTML file is ready!")