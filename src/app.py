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
                    value = r.json.get(self.field)
                if self.source == "form":
                    value = r.form.get(self.field)
                if self.source == "args":
                    value = r.args.get(self.field)
                if self.source == "head":
                    value = r.headers.get(self.field)
                if self.source == "const":
                    value = self.field

                return value


        def __init__(self, config, logger) -> None:
            self.endpoint = config["endpoint"]
            self.method = config["method"]
            self.headers = config["headers"]
            self.arguments = [
                (key, self.Selector(value))
                for key, value in config["arguments"].items()
            ]
            self.logger = logger
            # self.payload = [
                # (key, self.Selector(value))
                # for key, value in config["arguments"].items()
            # ]

        def __call__(self, r: wrappers.Request):
            self.logger.info("Incoming request:\n"\
                +"=== METHOD ===\n%s\n"\
                +"=== HEADERS ===\n%s\n"\
                +"=== ARGS ===\n%s\n"\
                +"=== PAYLOAD ===\n%s\n",
                r.method, r.headers, r.args, r.get_json(silent=True))

            arguments = {key: selector(r) for key, selector in self.arguments}
            # payload = {argument(r) for argument in self.payload}
            full_url = self.endpoint + "?" + "&".join(
                [f"{key}={value}" for key, value in arguments.items()]
            )
            self.logger.info("Outgoing request:\n"\
                +"=== ENDPOINT ===\n%s\n"\
                +"=== METHOD ===\n%s\n"\
                +"=== HEADERS ===\n%s\n",
                full_url, self.method, self.headers)


            response = requests.request(
                self.method, self.endpoint,
                headers=self.headers,
                params=arguments,
                # data=payload,
                timeout=60
            )
            self.logger.info("Response:\n"\
                +"=== STATUS ===\n%s\n"\
                +"=== HEADERS ===\n%s\n"\
                +"=== BODY ===\n%s\n",
                response.status_code, dict(response.headers), response.text)

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

    @application.route('/', methods=['GET', 'POST'])
    def index():
        """
        The main endpoint for the application.
        """
        response = Config.forwarder(request)

        return jsonify(response)

    with application.app_context():
        with open("config.yaml", "r", encoding="utf-8") as f:
            Config.forwarder = Config.Forwarder(yaml.safe_load(f), application.logger)


    return application

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
