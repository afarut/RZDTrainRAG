from flask import stream_with_context, request, Flask, Response
from rag import RAG
from upload import get_result_csv

app = Flask(__name__)

model = RAG()


@app.route('/upload', methods=["POST"])
def streamed_response():
    url = request.json.get("url")
    stream = get_result_csv(url)
    def generator(stream):
        for i in stream:
            #print(i.content, end="")
            yield i
    return Response(generator(stream), content_type='text/plain', headers={'Transfer-Encoding': 'chunked'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
