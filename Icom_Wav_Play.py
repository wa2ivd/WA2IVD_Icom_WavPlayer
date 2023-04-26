#
#
import os
import time
import threading
import pygame
import taglib
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

stopplaying = False
paused = False
skipfile = False


#
# Use taglib to get metadata from Icom Voice .wav files
#
def icom_wav_data(filepath):
    # This function expects a full filepath

    meta = taglib.File(filepath)
    full_title = meta.tags.get("TITLE")
    comments = meta.tags.get("COMMENT")

    #debugging
    #print(full_title)
    #print(comments)

    length= meta.length  # Length of sound file in seconds

    ofst= full_title[0].find("Recorder Data")
    
    if (ofst>0):

        radio = str.split(full_title[0])[0]

        
        ofst = ofst+15  #index to the text that we want to extract
        freq = full_title[0][0+ofst:10+ofst]
        mode = full_title[0][11+ofst:16+ofst]
        txrx = full_title[0][18+ofst:20+ofst]
        date = full_title[0][21+ofst:31+ofst]
        time = full_title[0][32+ofst:]

        mylatlon = comments[0][0:25]
        myalt = comments[0][26:34]
        mycall = comments[0][35:43]
        urcall = comments[0][44:52]
        mtr_pwr = comments[0][53:58]
        urlatlon = comments[0][59:83]
        uralt = comments[0][85:94]

        data_dict= {'radio':radio, 'freq':freq, 'mode':mode, 'txrx':txrx, 'date':date,
                    'time':time, 'mylatlon':mylatlon, 'myalt':myalt, 'mycall':mycall,
                    'urcall':urcall, 'mtr_pwr':mtr_pwr, 'urlatlon':urlatlon,
                    'uralt':uralt, 'length':length }
    else:
        data_dict= { }
    
    meta.close()
    
    #debugging
    #print('freq:',freq,' mode:', mode, ' txrx:',txrx, ' date:',date,' time:',time)
    #print('mylatlon:',mylatlon,' myalt:',myalt,' mycall:',mycall,' urcall:',urcall)
    #print('mtr_pwr:',mtr_pwr,' urlatlon:',urlatlon,' uralt:',uralt)
    
    return data_dict
      
    

# Increment clock time function for player time display
#
def inctime(hms, inc):
    hms[2]= hms[2] + inc
    if hms[2] >59:
        hms[2]= 60 - hms[2]
        hms[1]= hms[1] + 1

    if hms[1] >59:
        hms[1]= 60 - hms[1]
        hms[0]= hms[0] + 1

    if hms[0] >23:
        hms[0]= 24 - hms[0]

    return hms

    
# Player that plays a the list of files
#    Checks to see if a list item is selected and plays starting from the selected file.
#    Otherwise, plays from the beginning
#
def playfiles(pl, path, filelist):
    global stopplaying

    selected= pl.listbox.curselection()
    if len(selected)>0:
        firstfile= selected[0]
        pl.listbox.selection_clear(firstfile)
    else:
        firstfile= 0

    ##print("First=",firstfile)    
    for index, f in enumerate(filelist):
        # Break the loop if the user presses the stop button or if the loop flag is False
        if stopplaying:
            break
        if index<firstfile:
            continue

        file_path = os.path.join(path, f)

        ##print("index=",index,"Filepath=",file_path)

        # Load file into taglib and get title information
        IC_Data= icom_wav_data(file_path)

        clock = IC_Data['time'].split(':')
        timedata= [int(clock[0]), int(clock[1]), int(clock[2]) ]
        
        length = IC_Data['length']

        m_text = 'Radio: ' + IC_Data['radio'] + '      ' + IC_Data['freq'] + ' ' + IC_Data['mode'] + '\n'
        m_text2 = IC_Data['date'] + '    ' + IC_Data['time'] + "  " + format(length,'03') + ' Seconds'
        if (IC_Data['txrx'] == "RX"):
            m_text2 = m_text2 + '    RX Mtr:'
        else:
            m_text2 = m_text2 + '    TX Pwr:'

        m_text2 = m_text2 + IC_Data['mtr_pwr'] + '\n\n'
        
        m_text3 = 'My LATLON:' + IC_Data['mylatlon'] + '   My Alt:' + IC_Data['myalt'] + '\n\n'

        m_text4 = 'DV Data-   My Call:' + IC_Data['mycall'] + '   UR Call:' + IC_Data['urcall'] + '\n'
        m_text5 = ('UR LatLon:' + IC_Data['urlatlon'] + '\n' +
                      'UR Alt:' + IC_Data['uralt'])

        pl.textinfo.delete('1.0',tk.END)
        pl.textinfo.insert(tk.END,m_text + m_text2 + m_text3 + m_text4 + m_text5)
        pl.listbox.see(index)
        pl.listbox.itemconfig(index, bg='yellow')
        
  
        
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy() or paused:
            if stopplaying:
                pygame.mixer.music.stop()
                pl.textinfo.delete('1.0',tk.END)
                break

            time.sleep(1)
            if not paused:
                timedata = inctime(timedata, 1)
                length = length - 1
                clock_str= format(timedata[0],'02') + ':' + format(timedata[1],'02') + ':' + format(timedata[2],'02')
                pl.textinfo.replace("2.14","2.22",clock_str)
                len_str= format(length,'03')
                pl.textinfo.replace("2.24","2.27",len_str)
            
            
        pl.listbox.itemconfig(index, bg='white')
        ##print("Played: ",f)



#--------   Class Definition

class AudioPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Icom Voice File Player")
        self.create_widgets()
        self.current_file = None
        self.files = []
        self.folder_path = None
        self.loop_flag = False  # Add a flag to keep track of whether the loop is running

        # Initialize Pygame mixer
        pygame.mixer.init()

    def create_widgets(self):
        # Create a textbox to display current file information
        self.toplabel = tk.Label(self.root, text="Wave File Metadata", font=('Arial', 14, 'bold'))
        self.toplabel.pack(side="top")
        
        self.textinfo = tk.Text(self.root, height=8, width=50, fg="green", font=('Arial',14,'normal'))
        self.textinfo.pack(side="top")
        # Create the listbox to display the .wav files
        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=50, activestyle='none')
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # create a horizontal scrollbar and attach it to the listbox
        hscrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.listbox.config(xscrollcommand=hscrollbar.set)
        hscrollbar.config(command=self.listbox.xview)

        # create a vertical scrollbar and attach it to the listbox
        vscrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.listbox.yview)

        # Create the buttons
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.playall_button = tk.Button(self.root, text="Play All", command=self.play_loop)
        self.playall_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.skip_button = tk.Button(self.root, text="Skip", command=self.skip_file)
        self.skip_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Create the menu bar
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Folder", command=self.open_folder)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def open_folder(self):
        # Prompt the user to select a folder
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.files = [f for f in os.listdir(self.folder_path) if f.endswith('.wav')]
            self.listbox.delete(0, tk.END)
            for f in self.files:
                #
                #---- Checking meta function
                #
                metadata= icom_wav_data(os.path.join(self.folder_path, f))
                listitem= f+'    '+metadata['txrx']+'   '+metadata['freq']+' '+metadata['mode']
                listitem= listitem + 'Len:' + '{:03d}'.format(metadata['length'])
                self.listbox.insert(tk.END, listitem)

    def play(self, index):
        # Play the selected file
        self.current_file = self.files[index]
        self.listbox.itemconfig(index, bg='yellow')
        file_path = os.path.join(self.folder_path, self.current_file)
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()


    def play_loop(self):
        # Play the entire list

        global stopplaying

        # Stop the currently playing file if there is one
        if self.current_file:
            self.stop()
        # Set the loop flag to True
        stopplaying = False
        # Start the loop to play each file
        playthread = threading.Thread(target=playfiles, args=(self,self.folder_path,self.files))
        playthread.start()


    def pause(self):
        # Pause the currently playing file
        global paused
        ##print("paused is: ",paused)
        if not paused:
            pygame.mixer.music.pause()
            paused = True
            ##print("Setting paused: ",paused)
            time.sleep(1)
        else:
            pygame.mixer.music.unpause()
            paused = False
            ##print("Setting paused: ",paused)
            time.sleep(1)
            

    def stop(self):
        # Stop the currently playing file and reset the loop flag
        global stopplaying
        stopplaying = True

    def skip_file(self):
        # skip the current file
        pygame.mixer.music.stop()

    def run(self):
        self.root.mainloop()


#
# Main Code Here
#
        

if __name__ == '__main__':
    player = AudioPlayer()
    player.run()






