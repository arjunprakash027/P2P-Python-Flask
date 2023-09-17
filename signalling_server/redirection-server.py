from flask import Flask, request
from flask_socketio import SocketIO,emit
from peer_management import peer_pool
import logging
from logging.handlers import RotatingFileHandler
import time
import pickle

app = Flask(__name__)

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
    name = system_info['name']
    print("name",name)
    pool.add_peer(request.sid,name)
    print(pool.show_all_peers())
    #emit('update_peers',pool.show_all_peers(),broadcast=True)

@socketio.on('show_all_peers')
def show_peers():
    avilable_peers = pool.show_all_peers()
    total_peers = {}
    number = 0
    for i in avilable_peers:
        total_peers[number] = {"sid":i,"peer_details":avilable_peers[i]}
        number += 1
    print("total peers:",total_peers)
    emit('get_all_peers',total_peers,room=request.sid)

@socketio.on('select_available_peers')
def check_available_peers():
    req_peer = request.sid

    avilable_peers = pool.show_all_peers()
    total_peers = {}
    number = 0
    for i in avilable_peers:
        if req_peer != i:
            if avilable_peers[i]['availiblity']:
                total_peers[number] = {"sid":i,"peer_details":avilable_peers[i]}
                number += 1
    
    emit('get_all_peers',total_peers,room=request.sid)

    @socketio.on('get_particular_peer')
    def get_particular_peer(data):
        print("data:",data)
        print(total_peers)
        p_number = data['p_number']
        print(selected_peer := total_peers[int(p_number)]['sid'])
        sender_name = total_peers[int(p_number)]['peer_details']['name']
        pool.mark_peer_busy(selected_peer)
        pool.mark_peer_busy(request.sid)
        emit('let_me_know',{'peer':req_peer},room=selected_peer)
        emit('get_connected_sid',{'peer':selected_peer},room=req_peer)

        @socketio.on('send_message')
        def send_message(data):
            message = data['message']
            receiver = data['receiver']
            s_name = avilable_peers[request.sid]['name']
            print("sent by {} to {}".format(request.sid,receiver))
            print("message is {}".format(message))

            emit('recv_message',{'message':message,'sender':s_name},room=receiver)
        # selected_sid = pool.select_peer_for_service(req_peer,min_specs)
        # print("assigned sid:",selected_sid)
        # print(pool.show_all_peers())
    

if __name__ == "__main__":
    socketio.run(app,debug=True)