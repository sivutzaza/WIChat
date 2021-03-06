import kivy
import socket
import threading
import time

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.carousel import Carousel
from kivy.uix.popup import Popup
from kivy.uix.label import Label

#from kivy.core.window import Window
#Window.size = (350, 600)

Builder.load_string('''
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
<WIChat>:
    transition: SlideTransition(direction="up")
    startupScreen: StartupScreen
    mainUIScreen: MainUIScreen
    chatroomScreen: ChatroomScreen

    StartupScreen:
        id: StartupScreen
    MainUIScreen:
        id: MainUIScreen
    ChatroomScreen:
        id: ChatroomScreen

<StartupScreen>:
    name: "StartupScreen"

    nameInput: nameInput
    ipInput: ipInput
    portInput: portInput

    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        Button:
            id: StartupLabel
            text: "Start Up"
            size_hint: 1, .2

        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: "NAME"
                size_hint_x: .3
            TextInput:
                id: nameInput
                multiline: False
                size_hint_x: .7

        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: "HOST IP"
                size_hint_x: .3
            TextInput:
                id: ipInput
                multiline: False
                size_hint_x: .7

        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: "PORT"
                size_hint_x: .3
            TextInput:
                id: portInput
                multiline: False
                size_hint_x: .7


        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, .3
            Button:
                id: loginButton
                text: "LOG IN AS CLIENT"
                on_release: app.root.login()

            Button:
                id: loginButton
                text: "BECOME A HOST"
                on_release: root.openHostPopup()

<ProfileArea>:
    orientation: 'horizontal'
    profileButton: profileButton
    nameButton: nameButton
    statusButton: statusButton

    size_hint: (1, .2)
    Button:
        id: profileButton
        text: "Profile"
        size_hint_x: .3

    BoxLayout:
        orientation: 'vertical'
        Button:
            id: nameButton
            text: "Name"
            size_hint_y: .2
        Button:
            id: statusButton
            text: "Status"
            size_hint_y: .2

<MenuBar>:
    orientation: 'horizontal'
    contactButton: contactButton
    historyButton: historyButton
    settingButton: settingButton
    size_hint: (1, .1)

    Button:
        text: 'Contact'
        id: contactButton
        on_release: app.root.mainUIScreen.changeScreen('contact')

    Button:
        text: 'History'
        id: historyButton
        on_release: app.root.mainUIScreen.changeScreen('history')

    Button:
        text: 'Setting'
        id: settingButton


<ContactComponent@BoxLayout>:
    orientation: 'horizontal'
    size_hint: 1, None
    Button:
        size_hint: .3, 1
        text: 'Pic'
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Name'
        Button:
            text: 'Status'

<ContactScreen>:
    orientation: 'vertical'
    ScrollView:
        size: self.parent.width, self.parent.height
        GridLayout:
            cols: 1
            padding: 10
            spacing: 10
            size_hint: 1,None
            height: self.minimum_height

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, None
                Button:
                    size_hint: .3, 1
                    text: 'Pic'
                BoxLayout:
                    orientation: 'vertical'

                    Button:
                        text: 'Sivut'
                        on_release: app.root.current = "ChatroomScreen"

                    Button:
                        text: 'Status'



<HistoryScreen>:
    Label:
        text: 'HistoryScreen'
        font_size: 50

<ScreenSlider>:
    anim_move_duration: .3
    anim_cancel_duration: .5
    ContactScreen:
    HistoryScreen:

<MainUIScreen>:
    name: "MainUIScreen"
    profileArea: profileArea
    menuBar: menuBar
    screenSlider: screenSlider

    BoxLayout:
        orientation: 'vertical'
        ProfileArea:
            id: profileArea
        MenuBar:
            id: menuBar
        ScreenSlider:
            id: screenSlider

<ChatroomScreen>:
    name: "ChatroomScreen"

    BoxLayout:
        orientation: 'vertical'
        messageInput: messageInput

        Button:
            text: "Sivut Chatroom"
            size_hint: 1, .1

        ScrollView:
            size: self.parent.width, self.parent.height
            GridLayout:
                cols: 1
                padding: 10
                spacing: 10
                size_hint: 1,None
                height: self.minimum_height

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    Button:
                        size_hint: .2, 1
                        text: 'Sivut'
                    Label:
                        size_hint: .8, 1
                        text: "Hello"

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, .1
            TextInput:
                id: messageInput
                size_hint: .7, 1
            Button:
                id: sendButton
                text: "SEND"
                size_hint: .3, 1
                on_release: app.root.mainUIScreen.clientSocket.setText(messageInput.text)

''')

class StartupScreen(Screen):
    def __init__(self, **kwargs):
        super(StartupScreen, self).__init__(**kwargs)

    def openHostPopup(self):
        notification = BoxLayout(orientation = "vertical")
        label = Label(text="Please turn on Hotspot before start hosting.")
        closeButton = Button(text="Close")
        startHostButton = Button(text="Start Hosting")

        closeButton.size_hint = 1, .3
        startHostButton.size_hint = 1, .3
        notification.add_widget(label)
        notification.add_widget(startHostButton)
        notification.add_widget(closeButton)

        popup = Popup(title='Caution', content=notification,
                      auto_dismiss=True)
        popup.open()

        closeButton.bind(on_press = popup.dismiss)
        startHostButton.bind(on_press = self.startHosting)

    def startHosting(self, instance):
        pass


class MainUIScreen(Screen):
    def __init__(self, **kwargs):
        super(MainUIScreen, self).__init__(**kwargs)

        self.listofScreen = ["contact", "history"]
        self.curIndxScreen = 0

    def startClient(self, ip, port, username):
        self.clientSocket = ClientSocket(ip, int(port), username)  ## Start client socket loop
        self.clientSocket.connect()
        self.clientSocket.start()

    def changeScreen(self, name):
        target_idx = self.listofScreen.index(name)
        self.screenSlider.load_slide(self.screenSlider.slides[target_idx])


class ChatroomScreen(Screen):
    def __init__(self, **kwargs):
        super(ChatroomScreen, self).__init__(**kwargs)

class ProfileArea(BoxLayout):
    pass

class MenuBar(BoxLayout):
    pass

class ContactScreen(BoxLayout):
    pass

class HistoryScreen(BoxLayout):
    pass

class ScreenSlider(Carousel):
    pass

#########################################################

class Contact:
    def __init__(self, name, status, id):
        self.__name = name
        self.__status = status
        self.__id = id

    def getName(self):
        return self.__name

    def getStatus(self):
        return self.__status

    def getID(self):
        return self.__id

class ClientSocket(threading.Thread):
    def __init__(self, ip, port, name="Name", **kwargs):
        threading.Thread.__init__(self)
        self.tLock = threading.Lock()
        self.shutdown = False

        self.clientName = name
        self.clientMessage = ""

        self.ip = ip
        self.port = port
        self.targetServer = (ip, port)

    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.connect(self.targetServer)
        self.soc.setblocking(0)

        ### Create a receiving thread
        self.recvThread = threading.Thread(target=self.receving, args=("RecvThread",self.soc))
        self.recvThread.start()

    def setText(self, message):
        self.clientMessage = message

    def receving(self, name, sock):
        while not self.shutdown:
            try:
                self.tLock.acquire()
                while True:
                    data, addr = sock.recvfrom(1024)
                    print(str(data))
            except:
                pass
            finally:
                self.tLock.release()

    def run(self):
        while self.clientMessage != "q":
            string = self.clientName + ": " + self.clientMessage
            if self.clientMessage != "":
                self.soc.sendto(string.encode("utf-8"), self.targetServer)
            self.tLock.acquire()
            self.tLock.release()
            self.clientMessage = ""
            time.sleep(0.1)


class WIChat(ScreenManager):
    def __init__(self, **kwargs):
        super(WIChat, self).__init__(**kwargs)
        self.startupScreen = self.startupScreen
        self.mainUIScreen = self.mainUIScreen
        self.chatroomScreen = self.chatroomScreen

    def login(self):
        self.username = self.startupScreen.nameInput.text
        self.ip = self.startupScreen.ipInput.text
        self.port = int(self.startupScreen.portInput.text)

        self.current = "MainUIScreen"
        self.mainUIScreen.startClient(self.ip, self.port, self.username)
        self.mainUIScreen.profileArea.nameButton.text = self.username

class WIChatApp(App):
    def build(self):
        return WIChat()

    def on_pause(self):
        return True

WIChatApp().run()
