from scripts.parser import *
from google.cloud import storage
from config import Config
from flask import Flask, render_template, request

# flask
app = Flask(__name__)
app.config.from_object(Config)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# generated output files
template_name = "template.html"
output_name = "output.html"

@app.route("/newsletter-app/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        
        # 1 DELETING THE PREV TEMPLATE AND OUTPUT FILE
        template_blob = bucket.blob(template_name)
        output_blob = bucket.blob(output_name)
        if template_blob.exists(): template_blob.delete()
        if output_blob.exists(): output_blob.delete()

        # get links entered by user
        posts = [post[1] for post in request.form.items()]
        links = list(filter(None, [x.strip() for x in posts[0].splitlines()]))

        # get user uploaded template
        template = request.files["template"]

        # 2 SAVING THE USER UPLOADED TEMPLATE FILE
        template_blob = bucket.blob(template_name)
        template_blob.upload_from_string(template.read(), content_type="text/html")
            
        # creates a instance of a parser
        # generates a content dictionary based on the input links
        # writes to an output file and stores it in the bucket
        parser = Parser(links, template_name, output_name)
        parser.generate_elements_dict()
        parser.output_html_file()

        return render_template(
            "home.html",
            parsed=True
        )

    return render_template(
        "home.html",
        parsed=False
    )

@app.route("/newsletter-app/template/", methods=["POST", "GET"])
def template():
    return render_template(
        "template.html",
    )

# renders output file thats stored in the bucket
@app.route("/newsletter-app/output/", methods=["POST", "GET"])
def output():
    output_blob = bucket.blob(output_name)
    output_content = output_blob.download_as_string()
    return output_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route("/newsletter-app/test/", methods=["POST", "GET"])
def test():
    return "Hello World!"

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template(
        "index.html",
    )

if __name__ == "__main__":
    app.run(debug=True)