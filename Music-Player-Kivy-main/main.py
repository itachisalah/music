
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import Screen
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

import os
import eyed3
import time

os.environ["KIVY_AUDIO"] = "ffpyplayer"

Window.size = (360,600)

music_dir = os.path.dirname(os.path.realpath(__file__))+ "\musics\\"
list_music = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]


print(os.path.dirname(os.path.realpath(__file__)))

class MusicScreen(Screen):
    pass

class SongCover(MDBoxLayout):
    angle = NumericProperty()
    anim = Animation(angle= 360, d=7, t='linear')
    anim += Animation(angle= 0, d=0, t='linear')
    anim.repeat = True
    isResume = False
    current_song = 0

    def rotate(self):
        self.anim.start(self)

    def stopRotate(self):
        self.anim.stop(self)

    def play(self):
        if self.btn_play.icon == "pause-circle-outline":
            self.pause()
        elif self.isResume:
            self.resume()
        else:
            self.playSong()   

    def playSong(self):
        self.sound = SoundLoader.load(music_dir + list_music[self.current_song])
        audiofile = eyed3.load(music_dir + list_music[self.current_song])

        image_file = open(f"{self.current_song}.jpg", "wb")
        image_file.write(audiofile.tag.images[0].image_data)
        image_file.close()

        self.rotate_image.source = f"{self.current_song}.jpg"
        self.background_image.source = f"{self.current_song}.jpg"
        self.artist_name.text = audiofile.tag.artist
        self.song_name.text = audiofile.tag.title

        self.rotate()
        self.process_bar.value = 0
        self.current_time.text = "00:00"
        self.process_bar.max = self.sound.length
        self.sound.play()
        self.updateProcessbarEvent = Clock.schedule_interval(self.updateProcessbar, 1)
        self.updateTimeEvent = Clock.schedule_interval(self.setTime, 1)
        self.btn_play.icon = "pause-circle-outline"
        self.isResume = False     

    def resume(self):
        self.isResume = False
        self.btn_play.icon = "pause-circle-outline"
        self.sound.play()
        self.sound.seek(self.currtentSeekTime)
        self.updateProcessbarEvent = Clock.schedule_interval(self.updateProcessbar, 1)
        self.updateTimeEvent = Clock.schedule_interval(self.setTime, 1)
        self.rotate()

    def pause(self):
        if self.sound:
            self.currtentSeekTime = self.sound.get_pos()
            self.sound.stop()
            self.btn_play.icon = "play-outline"
            self.updateProcessbarEvent.cancel()
            self.updateTimeEvent.cancel()
            self.stopRotate()
            self.isResume = True

    def next(self):
        os.remove(f"{self.current_song}.jpg")
        self.isResume = False
        self.updateProcessbarEvent.cancel()
        self.updateTimeEvent.cancel()
        self.sound.stop()
        self.btn_loop.text_color = [1, 1, 1, 1]

        if self.current_song < len(list_music) - 1:
            self.current_song += 1
        else:
            self.current_song = 0
        self.stopRotate()
        self.playSong()

    def previous(self):
        os.remove(f"{self.current_song}.jpg")
        self.isResume = False
        self.updateProcessbarEvent.cancel()
        self.updateTimeEvent.cancel()
        self.btn_loop.text_color = [1, 1, 1, 1]

        if self.current_song > 0:
            self.current_song -= 1
        else:
            self.current_song = len(list_music) - 1
        self.sound.stop()
        self.stopRotate()
        self.playSong()

    def updateProcessbar(self, value):
        if self.process_bar.value < self.sound.length:
            self.process_bar.value += 1
        else:
            if self.sound.loop:
                self.process_bar.value = 0
                self.current_time.text = "00:00"
            else:
                self.stopRotate()
                self.updateProcessbarEvent.cancel()
                self.updateTimeEvent.cancel()
    
    def setTime(self, t):
        currtentTime = time.strftime("%M:%S", time.gmtime(self.process_bar.value))
        totalTime = time.strftime("%M:%S", time.gmtime(self.sound.length))

        self.current_time.text = currtentTime
        self.total_time.text = totalTime

    def seek(self):
        if self.sound:
            self.sound.seek(self.process_bar.value)

    def loop(self):
        if not self.sound.loop:
            self.sound.loop = True
            self.btn_loop.text_color = [37/255, 150/255, 190/255, 1]
        else:
            self.sound.loop = False
            self.btn_loop.text_color = [1, 1, 1, 1]
    
    def skipForward(self):
        self.skipEvent =  Clock.schedule_interval(self.updateProcessbar, .1)
    
    def doSkipForward(self):
        self.skipEvent.cancel()
    
    def skipBackward(self):
        self.skipEventBackward =  Clock.schedule_interval(self.updateProcessbarBackward, .1)

    def doSkipBackward(self):
        self.skipEventBackward.cancel()

    def updateProcessbarBackward(self, value):
        if self.process_bar.value > 0:
            self.process_bar.value -= 1

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return MusicScreen()

MainApp().run()