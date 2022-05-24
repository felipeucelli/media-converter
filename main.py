# -*- coding: utf-8 -*-

# @autor: Felipe Ucelli
# @github: github.com/felipeucelli

# Built-in
import os
import tkinter
from _thread import start_new_thread
from tkinter import filedialog, messagebox, ttk

from imageio_ffmpeg import get_ffmpeg_exe
from ffmpeg_progress_yield import FfmpegProgress


class Gui:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Media Converter')
        self.root.geometry('750x425')
        self.root.resizable(False, False)

        self.file_path = []
        self.file_extension = ''
        self.status_convert = True

        self.variable_out_file = tkinter.IntVar()

        self.style_root = ttk.Style(self.root)
        self.style_root.configure('TButton', font=('Arial', 15))
        self.style_root.configure('btn.TButton', font=('Arial', 10))
        self.style_root.configure('TRadiobutton', font=('Arial', 15))
        self.style_root.map('btn_stop_convert.TButton', foreground=[('!disabled', 'red'), ('disabled', 'grey')])
        self.style_root.map('btn_start_convert.TButton', foreground=[('!disabled', 'green'), ('disabled', 'grey')])

        self._interface()

    def _interface(self):
        """
        Configuring the interface widgets
        :return:
        """
        self.frame_main = tkinter.Frame(self.root, width=540, height=520)
        self.frame_main.pack(padx=5, pady=5, )

        self.frame_convert = tkinter.LabelFrame(self.frame_main, width=540, height=520)
        self.frame_convert.pack()

        # File selection frame
        self.frame_add = tkinter.Frame(self.frame_convert, width=540, height=100)
        self.frame_add.pack(fill='both', padx=5, pady=5)

        self.btn_add = ttk.Button(self.frame_add, text='ADD FILE', command=self.open_file)
        self.btn_add.pack(pady=15, padx=15, side='left')

        self.radio_bnt_mp3 = ttk.Radiobutton(self.frame_add, text='MP3', variable=self.variable_out_file, value=1)
        self.radio_bnt_mp3.pack(side='right', padx=15)

        self.radio_bnt_mp4 = ttk.Radiobutton(self.frame_add, text='MP4', variable=self.variable_out_file, value=2)
        self.radio_bnt_mp4.pack(side='right', padx=15)

        self.label_out_file = tkinter.Label(self.frame_add, font='arial 12', text='OUTPUT: ')
        self.label_out_file.pack(side='right', padx=15)

        # Frame listbox
        self.frame_list_box = tkinter.Frame(self.frame_convert, width=540, height=200)
        self.frame_list_box.pack(fill='both', pady=5, padx=5)

        list_playlist_scrollbar_y = tkinter.Scrollbar(self.frame_list_box, orient='vertical')
        list_playlist_scrollbar_y.pack(side="right", fill="y")

        list_playlist_scrollbar_x = tkinter.Scrollbar(self.frame_list_box, orient='horizontal')
        list_playlist_scrollbar_x.pack(side="bottom", fill="x")

        self.list_box_files = tkinter.Listbox(self.frame_list_box, width=540, height=8, font='arial 15',
                                              yscrollcommand=list_playlist_scrollbar_y.set,
                                              xscrollcommand=list_playlist_scrollbar_x.set, activestyle='none')
        self.list_box_files.pack()
        list_playlist_scrollbar_y.config(command=self.list_box_files.yview)
        list_playlist_scrollbar_x.config(command=self.list_box_files.xview)

        # Progress bar frame
        self.frame_progress_bar = tkinter.Frame(self.frame_convert, width=540, height=50)
        self.frame_progress_bar.pack(fill='both', pady=5, padx=5)

        self.progress_bar = ttk.Progressbar(self.frame_progress_bar, orient=tkinter.HORIZONTAL,
                                            mode='determinate', length=280)
        self.progress_bar.pack()

        # Conversion buttons and listbox frame
        self.frame_convert = tkinter.Frame(self.frame_convert, width=540, height=120)
        self.frame_convert.pack(fill='both', pady=5, padx=5)

        self.btn_clear = ttk.Button(self.frame_convert, text='CLEAR', command=self.clear_list_box)
        self.btn_clear.pack(anchor='nw', side='left', pady=20, padx=5)
        self.btn_clear.config(state=tkinter.DISABLED)

        self.btn_remove = ttk.Button(self.frame_convert, text='REMOVE', command=self.remove_item_list_box)
        self.btn_remove.pack(anchor='nw', side='left', pady=20, padx=5)
        self.btn_remove.config(state=tkinter.DISABLED)

        self.btn_start_convert = ttk.Button(self.frame_convert, text='CONVERT', command=self.convert,
                                            style='btn_start_convert.TButton')
        self.btn_start_convert.pack(anchor='ne', side='right', pady=20, padx=5)
        self.btn_start_convert.config(state=tkinter.DISABLED)

        self.btn_stop_convert = ttk.Button(self.frame_convert, text='STOP', command=self.cancel_convert,
                                           style='btn_stop_convert.TButton')
        self.btn_stop_convert.pack(anchor='ne', side='right', pady=20, padx=5)
        self.btn_stop_convert.config(state=tkinter.DISABLED)

    def change_interface_status(self, status: str):
        """
        Change the status of interface buttons
        :return:
        """
        self.btn_add['state'] = status
        self.radio_bnt_mp4['state'] = status
        self.radio_bnt_mp3['state'] = status
        self.btn_start_convert['state'] = status
        self.btn_remove['state'] = status
        self.btn_clear['state'] = status
        self.btn_stop_convert['state'] = 'enable' if status == 'disable' else 'disable'

    def _start_conversion(self):
        """
        Configures the interface to start the conversion
        :return:
        """
        self.status_convert = True
        for pos, value in enumerate(self.file_path):
            self.list_box_files.itemconfig(pos, fg='black')
        self.change_interface_status('disable')

    def _conversion_finished(self):
        """
        Reset the interface
        :return:
        """
        messagebox.showinfo('Info', 'Conversion Finished')
        self.change_interface_status('normal')
        self.set_progress_callback(percent='0')

        self.btn_stop_convert['state'] = 'disable'
        self.btn_stop_convert['text'] = 'STOP'
        self.status_convert = True

    def run_ffmpeg(self, command: list):
        """
        Run the ffmpeg binary and get stdout to generate a progress bar using the ffmpeg_progress_yield library
        :param command: List containing the parameters to be passed to ffmpeg
        :return:
        """
        ffmpeg = FfmpegProgress(command)
        for progress in ffmpeg.run_command_with_progress():
            self.set_progress_callback(str(progress))

    @property
    def ffmpeg_path(self) -> str:
        """
        Get the ffmpeg binary and adapt it to linux and Windows systems
        :return: Returns the full path of the binary
        """
        path = f'{get_ffmpeg_exe()}'
        if os.name != 'nt':
            ffmpeg = path.split('/')[-1]
            path = path.replace(ffmpeg, f'./{ffmpeg}')

        return path

    def to_mp4(self, file_in: str, file_out: str):
        """
        Convert video files using moviepy library
        :param file_in: Full path of the file to be converted
        :param file_out: Output file full path
        :return:
        """
        command = [self.ffmpeg_path, '-y', '-i', file_in, '-c:v', 'copy', file_out]

        self.run_ffmpeg(command=command)

    def to_mp3(self, file_in: str, file_out: str):
        """
        Convert audio files using moviepy library
        :param file_in: Full path of the file to be converted
        :param file_out: Output file full path
        :return:
        """
        command = [self.ffmpeg_path, '-y', '-i', file_in,  '-vn', file_out]

        self.run_ffmpeg(command=command)

    def remove_item_list_box(self):
        """
        Removes selected items in the listbox
        :return:
        """
        pos = self.list_box_files.curselection()
        if pos != ():
            self.list_box_files.delete(pos)
            self.file_path.pop(pos[0])
        if self.list_box_files.size() == 0:
            self.btn_start_convert['state'] = 'disable'
            self.btn_remove['state'] = 'disable'
            self.btn_clear['state'] = 'disable'

    def clear_list_box(self):
        """
        Clear all items from the listbox
        :return:
        """
        self.list_box_files.delete(0, 'end')
        self.file_path.clear()
        self.btn_start_convert['state'] = 'disable'
        self.btn_remove['state'] = 'disable'
        self.btn_clear['state'] = 'disable'

    def cancel_convert(self):
        """
        Cancel the conversation
        :return:
        """
        stop_convert = messagebox.askokcancel('Cancel Convert', 'Do you really want to stop the conversation?')
        if stop_convert:
            self.btn_stop_convert['state'] = 'disable'
            self.btn_stop_convert['text'] = 'STOPPING'
            self.status_convert = False

    def open_file(self):
        """
       Opens a box to select files, and inserts the files into a listbox
        :return:
        """
        path = filedialog.askopenfilenames(filetypes=(('all files', '*.*'),))
        if path != '' and path != ():
            path = list(path)
            self.btn_start_convert.config(state=tkinter.NORMAL)
            self.btn_remove.config(state=tkinter.NORMAL)
            self.btn_clear.config(state=tkinter.NORMAL)

            # Insert the files in the listbox and in the self.file_path variable
            for file in path:
                self.file_path.append(file)
                self.list_box_files.insert('end', file)

        else:
            self.btn_start_convert.config(state=tkinter.DISABLED)
            self.btn_remove.config(state=tkinter.DISABLED)
            self.btn_clear.config(state=tkinter.DISABLED)

    def _convert(self, *args):
        """
        Call the conversation function
        :param args: None
        :return: converted file
        """
        _none = args
        if self.variable_out_file.get() == 0:
            messagebox.showerror('Error', 'Please, Select a Output File')
        else:
            save_file = filedialog.askdirectory()
            if save_file != '' and save_file != ():
                self._start_conversion()

                for pos, file_in in enumerate(self.file_path):
                    name = self.get_file_name(file_in)  # Get the file name
                    extension = self.get_extension(name)  # Get the file extension
                    mp3_file_out = f'{save_file}/{name.replace(f".{extension}", ".mp3")}'
                    mp4_file_out = f'{save_file}/{name.replace(f".{extension}", ".mp4")}'

                    self.list_box_files.itemconfig(pos, fg='gray')  # Change the foreground of the file being converted

                    try:
                        if self.variable_out_file.get() == 1:
                            self.to_mp3(file_in, mp3_file_out)
                        elif self.variable_out_file.get() == 2:
                            self.to_mp4(file_in, mp4_file_out)
                    except (KeyError, IOError, RuntimeError):
                        self.list_box_files.itemconfig(pos, fg='red')
                    else:
                        self.list_box_files.itemconfig(pos, fg='green')

                    if not self.status_convert:
                        break
                self._conversion_finished()

    def convert(self):
        """
        Start a new thread for the conversion
        :return:
        """
        start_new_thread(self._convert, (None, None))

    @staticmethod
    def get_extension(file_name: str) -> str:
        """
        Get the file extension
        :param file_name: file_name
        :return: file extension
        """
        return file_name.split('.')[-1]

    @staticmethod
    def get_file_name(file_path: str) -> str:
        """
        Get the filename in the selected path
        :param file_path: file_path
        :return: File name
        """
        return f'{file_path.split("/")[-1]}'

    def set_progress_callback(self, percent: str):
        """
        Set the download progress bar
        :param percent: Progress bar percentage
        :return:
        """
        self.progress_bar['value'] = percent

    def start_mainloop(self):
        """
        Start tkinter mainloop
        :return:
        """
        self.root.mainloop()


class Main(Gui):
    def start_gui(self):
        """
        Start the graphical interface
        :return:
        """
        self.start_mainloop()


class Convert(Main):
    pass


if __name__ == '__main__':
    main = Convert()
    main.start_gui()
