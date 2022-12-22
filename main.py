
# AutoCode v0.1 By R.Hasaranga

from tkinter import *
from tkinter.messagebox import *
import multiprocessing
import requests
from functools import partial
from threading import Thread
from tkinter.filedialog import *
from tkinter import simpledialog
import queue

# packages which are ChatGPT forget to import sometimes.
from urllib.request import urlopen
import base64
import math
import time

apiKey = ""

class CodeWindowState:
    process = 0
    codeTextArea = 0

def runTheCode(txtCode):
    try:
        exec(txtCode, globals()) 
    except Exception as e:
        showinfo("Error",str(e))
    return

def onRunCodePress(state):
    try:
        state.process.terminate()
    except Exception as e:
        pass

    state.process = multiprocessing.Process(target=runTheCode, args=(state.codeTextArea.get(1.0,END),))
    state.process.start()
    return

def onSaveCodePress(state):
    file = asksaveasfilename(initialfile='code.py', defaultextension=".py", filetypes=[("Python Files","*.py")])
    if file != "":
        file = open(file,"w")
        file.write(state.codeTextArea.get(1.0,END))
        file.close()
    return

def onWindowClose(window, state):
    try:
        state.process.terminate()
    except Exception as e:
        pass
    window.destroy()    
    return

def setAPIKey():
    global apiKey
    txt = simpledialog.askstring(title="Set API Key",prompt="Your API Key:",show='*',initialvalue=apiKey)
    if txt != None:
        apiKey = txt.strip()
        file = open("config.dat","w")
        file.write(apiKey)
        file.close()
    return

def generateCode(prompt, taskMsgQueue):
    generatedCode = ""
    global apiKey
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ apiKey}
        body = '{"model": "text-davinci-003", "prompt": "python code to do ' + prompt + '", "temperature": 0.5, "max_tokens": 4000}'
        response = requests.post('https://api.openai.com/v1/completions', data=body, headers=headers)
        generatedCode = response.json()['choices'][0]['text']
    except Exception as e:
        pass

    codeWindow = Tk()
    codeWindow.title('Generated Code')
    codeWindowWidth = 800
    codeWindowHeight = 500
    screenWidth = codeWindow.winfo_screenwidth()
    screenHeight = codeWindow.winfo_screenheight()
    left = (screenWidth - codeWindowWidth) / 2
    top = (screenHeight - codeWindowHeight) /2
    codeWindow.geometry('%dx%d+%d+%d' % (codeWindowWidth, codeWindowHeight, left, top))
    codeWindow.grid_rowconfigure(0, weight=1)
    codeWindow.grid_columnconfigure(0, weight=1)
    codeTextArea = Text(codeWindow)
    codeTextArea.grid(sticky = N + E + S + W)
    codeTextArea.insert(1.0, generatedCode)

    state = CodeWindowState()
    state.codeTextArea = codeTextArea

    codeMenuBar = Menu(codeWindow)
    codeFileMenu = Menu(codeMenuBar, tearoff=0)

    codeFileMenu.add_command(label="Run Code", command=partial(onRunCodePress, state))
    codeFileMenu.add_separator()
    codeFileMenu.add_command(label="Save Code...", command=partial(onSaveCodePress, state))   
    codeMenuBar.add_cascade(label="File", menu=codeFileMenu)

    codeWindow.config(menu=codeMenuBar)
    codeWindow.protocol("WM_DELETE_WINDOW", partial(onWindowClose, codeWindow, state))    

    taskMsgQueue.put("generated")
    codeWindow.mainloop()
    return

def onGenerateCodePress(textArea, fileMenu, taskQueue):

    prompt = textArea.get(1.0,END).strip()
    if prompt == "":
        return

    global apiKey
    if apiKey == "":
        showinfo("Error", "Please set your API Key")
        return

    fileMenu.entryconfig("Generate Code",state="disabled")

    t = Thread(target=generateCode, args=(prompt,taskMsgQueue,))
    t.start()
    return

def onSaveTextPress(textArea):
    prompt = textArea.get(1.0,END).strip()
    if prompt == "":
        return      
    file = asksaveasfilename(initialfile='prompt.txt', defaultextension=".txt", filetypes=[("Text Files","*.txt")])
    if file != "":
        file = open(file,"w")
        file.write(prompt)
        file.close()
    return

def onAboutPress():
    showinfo("About","AutoCode v0.1\nBy Ruchira Hasaranga.\nhttps://www.hasaranga.com")
    return

def process_queue(window, fileMenu, taskQueue):
    try:
        msg = taskQueue.get_nowait()
        if msg == "generated":
            fileMenu.entryconfig("Generate Code",state="normal")
    except queue.Empty:
        pass
    window.after(1000, process_queue, window, fileMenu, taskQueue)
    return

if __name__ == "__main__":

    try:
        file = open("config.dat","r")
        apiKey = file.read()
        file.close()
    except Exception as e:
        pass

    window = Tk()
    window.title('AutoCode v0.1')

    thisWidth = 600
    thisHeight = 400
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()
    left = (screenWidth - thisWidth) / 2
    top = (screenHeight - thisHeight) /2
    window.geometry('%dx%d+%d+%d' % (thisWidth, thisHeight, left, top))

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    textArea = Text(window)
    textArea.grid(sticky = N + E + S + W)

    menuBar = Menu(window)

    taskMsgQueue = queue.Queue()

    fileMenu = Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="Generate Code", command=partial(onGenerateCodePress, textArea, fileMenu, taskMsgQueue))
    fileMenu.add_separator()
    fileMenu.add_command(label="Save Text...", command=partial(onSaveTextPress, textArea))    
    menuBar.add_cascade(label="File", menu=fileMenu)

    settingsMenu = Menu(menuBar, tearoff=0)
    settingsMenu.add_command(label="Set API Key...", command=setAPIKey)
    menuBar.add_cascade(label="Settings", menu=settingsMenu)

    helpMenu = Menu(menuBar, tearoff=0)
    helpMenu.add_command(label="About", command=onAboutPress)
    menuBar.add_cascade(label="Help", menu=helpMenu)    

    window.config(menu=menuBar)
    window.after(1000, process_queue, window, fileMenu, taskMsgQueue)

    window.mainloop()
