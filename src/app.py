"""
The main entrypoint for the application.
"""
from flask import Flask, request, jsonify, wrappers
import yaml
import requests

class Config:
    """
    Configuration settings for the application.
    """

    class Forwarder:
        """
        A template class for the configuration settings.
        """
        class Selector:
            """
            A class for selecting the arguments from the request.
            """
            def __init__(self, properties) -> None:
                self.source = properties["source"]
                self.field = properties["field"]

            def __call__(self, r: wrappers.Request) -> str:
                if self.source == "json":
                    value = r.json[self.field]
                if self.source == "form":
                    value = r.form[self.field]
                if self.source == "args":
                    value = r.args[self.field]
                if self.source == "head":
                    value = r.headers[self.field]
                if self.source == "const":
                    value = self.field

                return value


        def __init__(self, config) -> None:
            self.endpoint = config["endpoint"]
            self.method = config["method"]
            self.headers = config["headers"]
            self.arguments = [
                (key, self.Selector(value))
                for key, value in config["arguments"].items()
            ]
            # self.payload = [
                # (key, self.Selector(value))
                # for key, value in config["arguments"].items()
            # ]

        def __call__(self, r: wrappers.Request):
            arguments = {key: selector(r) for key, selector in self.arguments}
            # payload = {argument(r) for argument in self.payload}

            response = requests.request(
                self.method, self.endpoint,
                headers=self.headers,
                params=arguments,
                # data=payload,
                timeout=60
            )

            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }


    forwarder:Forwarder


def create_app():
    """
    Creates the Flask app and registers the blueprints.
    """
    application = Flask(__name__)

    with application.app_context():
        with open("config.yaml", "r", encoding="utf-8") as f:
            Config.forwarder = Config.Forwarder(yaml.safe_load(f))

    return application

if __name__ == '__main__':
    app = create_app()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """
        The main endpoint for the application.
        """
        response = Config.forwarder(request)

        return 200, jsonify(response)

    app.run(debug=True, port=5000)
