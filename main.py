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
        self.canvas_main = tkinter.Canvas(self.root, width=440, height=390)
        self.message_name_file = tkinter.Message(self.canvas_main, font='Arial 10', width=350)
        self.canvas_main.create_window(220, 50, window=self.message_name_file)
        self.label_count_file = tkinter.Label(self.canvas_main, font='Arial 15')
        self.canvas_main.create_window(220, 130, window=self.label_count_file)
        self.btn_open_file = tkinter.Button(self.canvas_main, font='Arial 15', text='OPEN FILE',
                                            command=self.open_file)
        self.canvas_main.create_window(220, 220, window=self.btn_open_file)
        self.btn_convert = tkinter.Button(self.canvas_main, font='Arial 15', text=' CONVERT ', command=self._convert)
        self.canvas_main.create_window(220, 280, window=self.btn_convert)
        self.btn_convert['state'] = 'disable'
        self.label_convert_status = tkinter.Label(self.canvas_main, font='Arial 15', fg='green')
        self.canvas_main.create_window(220, 350, window=self.label_convert_status)
        self.canvas_main.pack()

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
        messagebox.showinfo('Info', 'Convert Finished')
        self._unblock_interface()
        self.label_convert_status['text'] = ''
        self.label_count_file['text'] = ''

    def mp4_to_mp3(self, mp4, mp3):
        self._start_download()
        try:
            if type(mp4) == str:
                mp4_without_frames = AudioFileClip(mp4)
                mp4_without_frames.write_audiofile(mp3)
                mp4_without_frames.close()
                self._download_finished()
            elif type(mp4) == tuple:
                count = 0
                for file in mp4:
                    self.label_count_file['text'] = f'{count}/{len(mp4)}'
                    file_name = self.get_name_file(file)
                    self.message_name_file['text'] = file_name
                    mp4_without_frames = AudioFileClip(file)
                    mp4_without_frames.write_audiofile(f'{mp3}/{file_name.replace(".mp4", ".mp3")}')
                    mp4_without_frames.close()
                    count += 1
                    self.label_count_file['text'] = f'{count}/{len(mp4)}'
                self._download_finished()
        except Exception as error:
            messagebox.showerror('Error', error)
            self._unblock_interface()

    def open_file(self):
        path = filedialog.askopenfilenames(filetypes=(('Mp4 files', '*.mp4'),
                                                      ('All files', '*.*')))
        if path != '' and path != ():
            self.file_path = path
            self.file_name = self.get_name_file(path)
            self.message_name_file['text'] = self.file_name
            self.btn_convert['state'] = 'normal'

    def _convert(self):
        if len(self.file_path) == 1:
            save_file = filedialog.asksaveasfilename(defaultextension="mp3",
                                                     initialfile=self.file_name.replace('.mp4', '.mp3'))
            if save_file != '' and save_file != ():
                start_new_thread(self.mp4_to_mp3, (self.file_path[0], save_file))
        else:
            save_file = filedialog.askdirectory()
            if save_file != '' and save_file != ():
                start_new_thread(self.mp4_to_mp3, (self.file_path, save_file))

    @staticmethod
    def get_name_file(path):
        if type(path) == tuple:
            return f'{path[0].split("/")[len(path[0].split("/")) - 1]}'
        else:
            return f'{path.split("/")[len(path.split("/")) - 1]}'

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Convert()
    main.start()
