"""App entry point."""
from MTMS import create_app
from ssl import SSLContext, PROTOCOL_TLSv1_2

app = create_app()

context = SSLContext(PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)