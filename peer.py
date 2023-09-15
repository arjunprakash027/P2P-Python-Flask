import socketio
import gpuinfo
import threading
import time
from serialize_csv import csv_to_byte
import pickle
import pandas

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
        print("A compute has been assigned to you:{}\n".format(selected_sid))
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
    #print(all_peers)
    for peer,specs in all_peers.items():
        if specs['availiblity']:
            print("peer:",peer)

@sio.on('job_done')
def jon_done(answer):
    if answer == "None":
        print("incorrect query")
    else:
        print("the answer is:",answer)

@sio.on('ml_job')
def perform_ml_job(serialized_data):
    data = pickle.loads(serialized_data)
    df = pandas.DataFrame(data)
    print(df)
    df.to_csv('output.csv')
    
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

1 -> Stop the server
2 -> give some task
3 -> show all peers
4 -> Train a model



"""
        task_inp = """
enter a arthemetic query

"""

        option = int(input(options))

        if option == 2:
            get_compute_peer()
            query = str(input("enter query:"))
            data = {"query":query,"provider":provider}
            sio.emit('perform_computation',data)
        elif option == 1:
            continue_peer = False
        elif option == 3:
            sio.emit('show_all_peers')
        elif option == 4:
            get_compute_peer()
            path = str(input("enter path of the csv file:"))
            serialized_data = csv_to_byte(path)
            #print(serialized_data)
            data = {"serialized_data":serialized_data,"provider":provider}
            sio.emit("perform_ml",data)

        else:
            print("option not available")


if __name__ == "__main__":
    sio.connect('http://127.0.0.1:5000')
    time.sleep(3)
    
    sio_thread = threading.Thread(target = sio.wait)
    sio_thread.start()
    
    while continue_peer:
        interface()
    
    sio.emit('disconnect')
    sio.disconnect()
    sio_thread.join()
    