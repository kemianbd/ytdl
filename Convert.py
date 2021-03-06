import os
from pytube import YouTube
import moviepy.editor as mp
from tkinter import *
from tkinter import ttk, messagebox, Tk, scrolledtext
from tkinter.filedialog import askdirectory


def exit_program():
    sys.exit(0)


def get_path():
    file = askdirectory(title='Choose Path')
    path_var.set(file)


def show_progress(stream=None, chunk=None, file_handle=None, bytes_remaining=None):
    barLength = 10  # Modify this to change the length of the progress bar
    percent = (yfilesize - bytes_remaining) / yfilesize
    block = int(round(barLength * percent))
    text = "\rVideo Progress: [{0}] {1}% {2}".format("#" * block + "-" * (barLength - block), round(percent*100,1), 'downloaded')
    sys.stdout.write(text)
    sys.stdout.flush()


def dl_convert(yturl, dlpath, vid, bit):
    # Save dlpath for future
    configtxt = open("config.txt", "w")
    configtxt.write(dlpath)
    configtxt.close()

    # Split entries
    ytget = yturl.splitlines()

    # Loop through all URLs
    err_cnt = 0
    for i in range(0, len(ytget)):

        # Skip blank line
        if ytget[i] == "":
            continue

        # Grab video from youtube
        try:
            ytdl = YouTube(ytget[i])
        except:
            err_cnt += 1
            print('File', i+1, 'could not be downloaded, make sure the YouTube link is correct')
            continue

        # Get attributes of video
        global yfilesize
        try:
            yfilesize = ytdl.streams.filter(file_extension='mp4').first().filesize
            ytdl.register_on_progress_callback(show_progress)
        except:
            print("Progress bar can't be shown. Working on it, sorry!")
        ytitle = ytdl.title
        print('NOW DOWNLOADING: ' + ytitle + '\n')
        ytdl.streams.filter(file_extension='mp4').first().download(dlpath)

        # Clean title
        for badchar in ['\"', '#', '$', '%', '\'', '*', ',', '.', '/', ':',
                        ';', '<', '>', '?', '\\', '^', '|', '~', '\\\\']:
            if badchar in ytitle:
                ytitle = ytitle.replace(badchar, "")

        # Convert video to mp3
        print('\n')
        clip = mp.VideoFileClip(dlpath + '\\' + ytitle + '.mp4')
        clip.audio.write_audiofile(dlpath + '\\' + ytitle + '.mp3', bitrate=bit)
        clip.reader.close()

        # Delete video if not requested
        if vid == 0:
            os.remove(dlpath + '\\' + ytitle + '.mp4')

    if err_cnt == 0:
        messagebox.showinfo('Status', 'All downloads complete')
    else:
        messagebox.showinfo('Status', 'At least one file did not download successfully')


if __name__ == "__main__":
    root = Tk()
    root.title("Download From YouTube")

    mainframe = ttk.Frame(root, padding="2 6 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    # Enter YouTube url
    ttk.Label(mainframe, text="Enter YouTube URL(s) - One per line").grid(column=1, row=2, sticky=W)
    yt_url = scrolledtext.ScrolledText(mainframe, width=67, height=5)
    yt_url.grid(column=1, row=3, sticky=(W, E))

    # Download path
    # Initialize
    ttk.Label(mainframe, text="Download Location").grid(column=1, row=5, sticky=W)
    path_var = StringVar()

    # Default path
    configtxt = open("config.txt", "r")
    dlpdefault = configtxt.read()
    configtxt.close()
    path_var.set(dlpdefault)

    # UI button
    dlpath = ttk.Entry(mainframe, width=67, textvariable=path_var)
    dlpath.grid(column=1, row=6, sticky=(W, E))

    # Button to choose path
    get_address = ttk.Button(mainframe, width=3, text="...", command=lambda:get_path())
    get_address.grid(column=2, row=6, sticky=W)

    # What to download
    vid = IntVar()
    vidb = ttk.Checkbutton(mainframe, text='Keep Video?', variable=vid)
    vidb.grid(column=1, row=8)

    bit = StringVar()
    bit_rate = ttk.OptionMenu(mainframe,bit,'256k','192k','256k','320k')
    bit_rate.grid(column=1, row=9)

    # Actions
    convert = ttk.Button(mainframe, text="Go!",
        command=lambda: dl_convert(yt_url.get(1.0,END), dlpath.get(), vid.get(), bit.get()))
    convert.grid(column=1, row=10, sticky=E)

    leave = ttk.Button(mainframe, text="Exit", command=exit_program)
    leave.grid(column=1, row=10, sticky=W)

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.mainloop()
