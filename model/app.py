from flask import stream_with_context, request, Flask, Response
from rag import RAG

app = Flask(__name__)

model = RAG()


@app.route('/stream', methods=["POST"])
def streamed_response():
    message = request.json.get("message")
    stream = model(message)
    def generator(stream):
        for i in stream:
            #print(i.content, end="")
            try:
                yield i.content
            except AttributeError:
                yield i
    return Response(generator(stream), content_type='text/plain', headers={'Transfer-Encoding': 'chunked'})


@app.route('/more', methods=["POST"])
def streamed_more_response():
    message = request.json.get("message")
    stream = model.get_more(message)
    def generator(stream):
        for i in stream:
            #print(i.content, end="")
            try:
                yield i.content
            except AttributeError:
                yield i
    return Response(generator(stream), content_type='text/plain', headers={'Transfer-Encoding': 'chunked'})


# get_result_csv

if __name__ == "__main__":
    app.run(host="0.0.0.0")
