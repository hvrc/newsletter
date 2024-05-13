from scripts.parser import *
from config import Config
from flask import Flask, render_template, request

app = Flask(__name__)
app.config.from_object(Config)
app.config["TEMPLATES_AUTO_RELOAD"] = True

root_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = root_dir + "/templates/"
template_name = "template.html"
template_path = template_dir + template_name
output_path = "templates/output.html"

@app.route("/newsletter-app/", methods=["POST", "GET"])
def home(): 
    if request.method == "POST":
        if os.path.exists(template_path):
            os.remove(template_path)
            print(template_path + " deleted")

        if os.path.exists(output_path):
            os.remove(output_path)
            print(output_path + " deleted")

        posts = [post[1] for post in request.form.items()]
        links = list(filter(None, [x.strip() for x in posts[0].splitlines()]))

        template = request.files["template"]
        template.save(template_path)

        parser = Parser(links, template_dir, template_name, output_path)
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

@app.route("/newsletter-app/output/", methods=["POST", "GET"])
def output():
    return render_template(
        "output.html",
    )

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