import socketio
import threading
import time
import PyQt5

sio = socketio.Client()

peer_avilable = False
#events code block ----------------
@sio.on('connect')
def on_connect():
    system_info = {"name":str(input("enter your name:"))}
    sio.emit('peer_info',system_info)
    print("conncted to the middleman server")

@sio.on('update_peers')
def update_peers(peers):
    print("connected peers:",peers)

@sio.on("let_me_know")
def let_me_know(data):
    print("A peer has been connected to you:",data['peer'])
    while True:
        message = str(input(""))
        sio.emit('send_message',{'message':message,'receiver':data['peer']})
    
    
#events code block end -------------

def start_receiving_messages():
    while True:
        @sio.on("recv_message")
        def recv_message(data):
            message = data['message']
            sender = data['sender']
            print("{} : {}".format(sender,message))

def get_message_peer():
    sio.emit('select_available_peers')
    

continue_peer  = True
def interface():
    global continue_peer
    global peer_avilable

    @sio.on('get_all_peers') #put inside the function to manipulated global value interface
    def get_all_peers(all_peers):
        global peer_avilable
        #print(all_peers)
        if all_peers == {}:
            peer_avilable = False
        else:
            for number,specs in all_peers.items():
                if specs['peer_details']['availiblity']:
                    print("peer_number:",number,"peer_name:",specs['peer_details']['name'])
            peer_avilable = True


   

    while continue_peer:
        options = """
Select from the below options

1 -> Stop the server
2 -> Connect to a peer
3 -> show all peers



"""
        task_inp = """
enter a arthemetic query

"""

        option = int(input(options))

        if option == 2:
            get_message_peer()
            time.sleep(2)
            if peer_avilable:
                peer_number = int(input("enter peer number:"))
                sio.emit('get_particular_peer', {'p_number': peer_number})
                print("peer connected")
                @sio.on('get_connected_sid')
                def get_connected_sid(data):
                    global friend
                    friend = data['peer']
                    print("friend:",friend)

                while True:
                    message = str(input(""))
                    sio.emit('send_message',{'message':message,'receiver':friend})
            else:
                print("sorry no peer avilable")




        elif option == 1:
            continue_peer = False
        elif option == 3:
            sio.emit('show_all_peers')
        elif option == 4:
            pass

        else:
            print("option not available")


if __name__ == "__main__":
    sio.connect('http://127.0.0.1:5000')
    time.sleep(3)
    
    sio_thread = threading.Thread(target = sio.wait)
    sio_thread.start()

    message_thread = threading.Thread(target = start_receiving_messages)
    message_thread.start()
    
    while continue_peer:
        interface()
    
    sio.emit('disconnect')
    sio.disconnect()
    sio_thread.join()
    message_thread.join()
    