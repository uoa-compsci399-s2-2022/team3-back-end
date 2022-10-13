"""App entry point."""
from MTMS import create_app
import ssl

app = create_app()

context = ssl.SSLContext()
context.load_cert_chain('cert.pem', 'key.pem')

if __name__ == "__main__":
    app.run(host='localhost', port=5000, ssl_context=context)