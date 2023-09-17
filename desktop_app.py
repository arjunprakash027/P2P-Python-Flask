import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QWidget, QVBoxLayout, QLabel,QTextEdit
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import socketio

sio = socketio.Client()

class SignalHandler(QObject):
    update_peers_signal = pyqtSignal(dict)
    let_me_know_signal = pyqtSignal(dict)
    get_connected_sid_signal = pyqtSignal(dict)
    recv_message_signal = pyqtSignal(dict)

class EnterTextEdit(QTextEdit):
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers():
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)

signal_handler = SignalHandler()


class ChatWindow(QMainWindow):
    def __init__(self, parent=None, data={}):
        super(ChatWindow, self).__init__(parent)
        self.data = data
        self.setMinimumSize(1000, 790)
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle("Chat")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.chat_window = QTextEdit(central_widget)
        font = QFont()  # Create a QFont instance
        font.setPointSize(18)  # Set the font size to 12
        self.chat_window.setFont(font)  # Apply the font to the chat window
        self.chat_window.setReadOnly(True)

        self.input_box = EnterTextEdit(central_widget)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_box.setFont(input_font)
        self.input_box.setPlaceholderText("Type your message here")
        self.input_box.enter_pressed.connect(self.send_message)

        self.send_button = QPushButton("Send", central_widget)
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_window)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

        central_widget.setLayout(layout)

        self.developed_by_label = QLabel(self.mainWidget)
        self.developed_by_label.setText('<a href="https://github.com/arjunprakash027">Developed with love by Arjun</a>')
        self.developed_by_label.setOpenExternalLinks(True)
        self.developed_by_label.setFont(QFont("Arial", 10))
        self.developed_by_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.developed_by_label.setGeometry(550, 670, 400, 20)

        sio.on('recv_message', self.handle_recv_message)
        signal_handler.recv_message_signal.connect(self.recv_message)

    def send_message(self):
        message = self.input_box.toPlainText()
        if message:
            self.chat_window.append(f"you:{message}")
            sio.emit('send_message',{"message":message,"receiver":self.data['peer']})
            self.input_box.clear()

    def handle_recv_message(self, data):
        signal_handler.recv_message_signal.emit(data)
    
    def recv_message(self,data):
        message = data['message']
        sender = data['sender']
        self.chat_window.append(f"{sender}: {message}")


class SelectPeerWindow(QMainWindow):
    def __init__(self, parent=None, name=""):
        super(SelectPeerWindow, self).__init__(parent)
        self.peer_windows = []
        self.setMinimumSize(1000, 790)
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle("Select Peer")
        self.name = name

        font = QFont()
        font.setBold(True)
        font.setPointSize(16)  

        self.label = QLabel(parent=self.mainWidget)
        self.label.setText(f"Hello, {name}!")
        self.label.setGeometry(350, 50, 350, 30)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignCenter)


        self.label_inform = QLabel(parent=self.mainWidget)
        self.label_inform.setText(f"select your peer from the list please!")
        self.label_inform.setGeometry(350, 350, 350, 30)
        self.label_inform.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.peer_layout = QVBoxLayout()
        self.mainWidget.setLayout(self.peer_layout)

        self.developed_by_label = QLabel(self.mainWidget)
        self.developed_by_label.setText('<a href="https://github.com/arjunprakash027">Developed with love by Arjun</a>')
        self.developed_by_label.setOpenExternalLinks(True)
        self.developed_by_label.setFont(QFont("Arial", 10))
        self.developed_by_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.developed_by_label.setGeometry(550, 670, 400, 20)


        sio.emit("select_available_peers")
        sio.on('get_all_peers', self.handle_update_peers)
        sio.on('let_me_know', self.handle_let_me_know)
        sio.on('get_connected_sid', self.handle_get_connected_sid)

        # Connect the signal to the slot
        signal_handler.update_peers_signal.connect(self.update_peers)
        signal_handler.let_me_know_signal.connect(self.let_me_know)
        signal_handler.get_connected_sid_signal.connect(self.get_connected_sid)

    def handle_update_peers(self, peers):
        # Emit the signal to update the peers
        signal_handler.update_peers_signal.emit(peers)
        print(peers)
    
    def handle_let_me_know(self, data):
        # Emit the signal to let the user know
        signal_handler.let_me_know_signal.emit(data)
    
    def handle_get_connected_sid(self, data):
        signal_handler.get_connected_sid_signal.emit(data)

    def let_me_know(self, data):
        select_chat_window = ChatWindow(self, data = data)
        self.peer_windows.append(select_chat_window)  # Store the reference to the new window
        select_chat_window.show()  # Show the new window
        self.label.hide()
        
        print("inside let me know:",data)

    def get_connected_sid(self, data):
        select_chat_window = ChatWindow(self, data = data)
        self.peer_windows.append(select_chat_window)  # Store the reference to the new window
        select_chat_window.show()  # Show the new window
        self.label.hide()
        
        print("inside get connected sid:",data)

    def update_peers(self, peers):
        # Remove any existing buttons
        for i in reversed(range(self.peer_layout.count())):
            widget = self.peer_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create buttons based on the keys of the peers dictionary
        for key,value in peers.items():
            button = QPushButton(value['peer_details']['name'], parent=self.mainWidget)
            button.setFont(QFont())
            button.clicked.connect(lambda _, key=key: self.handle_button_click(key))
            self.peer_layout.addWidget(button)

    def handle_button_click(self, key):
        print(f"Button clicked for peer: {key}")
        sio.emit('get_particular_peer', {'p_number': key})

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Peer to Peer chatting application')
        self.setMinimumSize(1000, 790)

        self.name_enter = QLineEdit(self)
        self.name_enter.setPlaceholderText('Enter your name')
        self.name_enter.setGeometry(350, 50, 350, 30)
        self.name_enter.returnPressed.connect(self.onTextChanged)

        sio.connect('http://127.0.0.1:5000')
        
        self.peer_windows = []  # Store references to peer windows

        self.developed_by_label = QLabel(self)
        self.developed_by_label.setText('<a href="https://github.com/arjunprakash027">Developed with love by Arjun</a>')
        self.developed_by_label.setOpenExternalLinks(True)
        self.developed_by_label.setFont(QFont("Arial", 10))
        self.developed_by_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.developed_by_label.setGeometry(550, 670, 400, 20)


    def onTextChanged(self):
        self.text = self.name_enter.text()
        system_info = {"name": self.text}
        sio.emit('peer_info', system_info)

        select_peer_window = SelectPeerWindow(self, self.text)
        self.peer_windows.append(select_peer_window)  # Store the reference to the new window
        select_peer_window.show()  # Show the new window
        self.name_enter.hide()

    def closeEvent(self, close):
        sio.disconnect() 
        print("app closed succussfully, thank you for using!")
        close.accept()
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
