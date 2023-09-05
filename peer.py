import socketio
import gpuinfo
import threading
import time

sio = socketio.Client()

#events code block ----------------
provider = None
@sio.on('connect')
def on_connect():
    system_info = gpuinfo.get_gpu_info()
    sio.emit('peer_info',system_info)
    print("conncted to the middleman server")

@sio.on('update_peers')
def update_peers(peers):
    print("connected peers:",peers)

@sio.on('assigned_compute')
def assigned_compute(selected_sid):
    global provider
    if selected_sid == "None":
        print("sorry all peers are busy")
    else:
        print("A compute has been assigned to you:",selected_sid)
        provider = selected_sid

@sio.on('job')
def perform_task(query):
    print("received a task",query)
    try:
        answer = eval(query)
        sio.emit('answer_received',answer)
    except:
        sio.emit('answer_recieved',"None")

@sio.on('get_all_peers')
def get_all_peers(all_peers):
    print(all_peers)
    for peer,specs in all_peers.items():
        if specs['availiblity']:
            print("peer:",peer)

@sio.on('job_done')
def jon_done(answer):
    if answer == "None":
        print("incorrect query")
    else:
        print("the answer is:",answer)

#events code block end -------------


def get_compute_peer():
    min_specs = {'memory_used':600.0}
    sio.emit('select_available_peers', {'min_specs': min_specs})

continue_peer  = True
def interface():
    global continue_peer

    while continue_peer:
        options = """
Select from the below options

1 -> give some task
2 -> show all peers
3 -> Stop the server


"""
        task_inp = """
enter a arthemetic query

"""

        option = int(input(options))

        if option == 1:
            get_compute_peer()
            query = str(input("enter query:"))
            data = {"query":query,"provider":provider}
            sio.emit('perform_computation',data)
        elif option == 3:
            continue_peer = False
        elif option == 2:
            sio.emit('show_all_peers')
        else:
            print("option not available")


if __name__ == "__main__":
    sio.connect('http://127.0.0.1:5000')
    time.sleep(3)
    
    sio_thread = threading.Thread(target = sio.wait)
    sio_thread.start()
    
    while continue_peer:
        interface()
    
    sio.disconnect()
    sio_thread.join()
    