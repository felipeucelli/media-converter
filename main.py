import tkinter
from tkinter import filedialog, messagebox
from _thread import start_new_thread

from moviepy.audio.io.AudioFileClip import AudioFileClip


class Convert:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry('450x400')
        self.root.resizable(False, False)

        self.file_path = ''
        self.file_name = ''

        self._interface()

    def _interface(self):
        self.canvas_file = tkinter.Canvas(self.root, width=440, height=390)
        self.message_name_file = tkinter.Message(self.canvas_file, font='Arial 10', width=350)
        self.canvas_file.create_window(220, 50, window=self.message_name_file)
        self.btn_open_file = tkinter.Button(self.canvas_file, font='Arial 15', text='OPEN FILE',
                                            command=self.open_file)
        self.canvas_file.create_window(220, 150, window=self.btn_open_file)
        self.btn_convert = tkinter.Button(self.canvas_file, font='Arial 15', text=' CONVERT ', command=self._convert)
        self.canvas_file.create_window(220, 220, window=self.btn_convert)
        self.btn_convert['state'] = 'disable'
        self.label_convert_status = tkinter.Label(self.canvas_file, font='Arial 15', fg='green')
        self.canvas_file.create_window(220, 300, window=self.label_convert_status)
        self.canvas_file.pack()

    def _block_interface(self):
        self.btn_open_file['state'] = 'disable'
        self.btn_convert['state'] = 'disable'

    def _unblock_interface(self):
        self.btn_open_file['state'] = 'normal'
        self.btn_convert['state'] = 'normal'

    def _start_download(self):
        self._block_interface()
        self.label_convert_status['text'] = 'Converting file, Please wait.'

    def _download_finished(self):
        messagebox.showinfo('Info', 'Download Finished')
        self._unblock_interface()
        self.label_convert_status['text'] = ''

    def mp4_to_mp3(self, mp4, mp3):
        self._start_download()
        try:
            mp4_without_frames = AudioFileClip(mp4)
            mp4_without_frames.write_audiofile(mp3)
            mp4_without_frames.close()
            self._download_finished()
        except Exception as error:
            messagebox.showerror('Error', error)
            self._unblock_interface()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=(('Mp4 files', '*.mp4'),
                                                     ('All files', '*.*')))
        if path != '' and path != ():
            self.file_path = path
            self.file_name = f'{path.split("/")[len(path.split("/")) - 1]}'
            self.message_name_file['text'] = f'FILE: {self.file_name}'
            self.btn_convert['state'] = 'normal'

    def _convert(self):
        save_file = filedialog.asksaveasfilename(defaultextension="mp3",
                                                 initialfile=self.file_name.replace('.mp4', '.mp3'))
        if save_file != '' and save_file != ():
            start_new_thread(self.mp4_to_mp3, (self.file_path, save_file))

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Convert()
    main.start()
