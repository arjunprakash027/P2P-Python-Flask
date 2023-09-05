from flask import Flask, request
from flask_socketio import SocketIO,emit
from peer_management import peer_pool
import logging
from logging.handlers import RotatingFileHandler
import time

app = Flask(__name__)
file_handler = RotatingFileHandler('flask_app.log', maxBytes=1024 * 1024, backupCount=3)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

socketio = SocketIO(app)
pool = peer_pool()

@socketio.on('connect')
def handle_connect():
    print(f"{request.sid} hopped in") 

@socketio.on('disconnect')
def handle_disconnect():
    print(f"{request.sid} hopped out")
    pool.remove_peer(request.sid)
    print(pool.show_all_peers())
    #emit('update_peers',pool.show_all_peers(),broadcast=True)

@socketio.on('peer_info')
def peer_info(system_info):
    sys_info = system_info[0]
    pool.add_peer(request.sid,sys_info)
    print(pool.show_all_peers())
    #emit('update_peers',pool.show_all_peers(),broadcast=True)

@socketio.on('show_all_peers')
def show_peers():
    emit('get_all_peers',pool.show_all_peers(),room=request.sid)

@socketio.on('select_available_peers')
def check_available_peers(data_sent):
    req_peer = request.sid
    min_specs = data_sent['min_specs']
    print(min_specs)
    selected_sid = pool.select_peer_for_service(req_peer,min_specs)
    print("assigned sid:",selected_sid)
    print(pool.show_all_peers())


    if selected_sid == None:
         emit('assigned_compute',"None",room=req_peer)
    else:
        emit('assigned_compute',selected_sid,room=req_peer)
    

@socketio.on('perform_computation')
def perform_computation(data):
    req_peer = request.sid
    query = data['query']
    provider = data['provider']
    emit('job',query,room = provider)

    @socketio.on('answer_received')
    def answer_received(answer):
        print(f"server got the answer from {request.sid} and the anser is {answer}")
        emit('job_done',answer,room=req_peer)
        pool.mark_peer_available(provider)

if __name__ == "__main__":
    socketio.run(app,debug=True)