import sounddevice as sd
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
from threading import Lock
import datetime
import matplotlib.pyplot as plt
import threading
from scipy.io import wavfile
import os
import time
# Capture and publish audio data to csv_logger, sound

class AudioPublisher(Node):
    def __init__(self, device_ports,numberofmics, fig, ax, sample_rate = 44100, duration = .1):
        super().__init__('audio_publisher')
        
        self.device_ports = device_ports
        self.sample_rate = sample_rate
        self.numberofmics = numberofmics
        self.fig = fig
        self.ax = ax
        self.line = []
        for ax in self.ax:
            line, = ax.plot([], [], 'r-')
            ax.set_xlim(0, 100)
            ax.set_ylim(-1, 1)
            ax.grid(True)
            self.line.append(line)
        self.output_filename = "audiocaptures/audiocaptures_12/withthreads/output_audio_DELETE"
        self.reference_amplitude = 1 #change as per requirements
        self.buffertime = 15 #15 seconds buffer time

        # create publishers
        self.pub = self.create_publisher(Float32MultiArray, f'db_data',10)

        self.micthreads = []
        self.audiostreams = []
        self.audiodata_lock = []
        self.dbdata_lock = []
        self.audiodata = []
        self.dbdata = [[] for _ in self.device_ports]

        for i in range(len(self.device_ports)):
            self.audiodata_lock.append(Lock())
            self.dbdata_lock.append(Lock())
            self.audiodata.append(np.full((self.sample_rate * self.buffertime, 1), None))
            self.dbdata.append([])

        self.write_position = [0] * len(self.device_ports)
        self.buffer_num = [1]*len(self.device_ports)

        for i in range(len(self.device_ports)):
            threadt = threading.Thread(target=self.startrec, args=(self.device_ports[i],i))
            threadt.start()
            self.micthreads.append(threadt)

        self.timer = self.create_timer(duration, self.publish_db_data)
    
    def startrec(self, deviceport, deviceportindex):
        audio_stream = sd.InputStream(
            device=deviceport,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=105, #factor of 44100, keeping it fixed to not lose any samples
            callback=lambda indata, frames, time, status: self.audio_callback(deviceportindex, indata, frames, time, status)
        )
        audio_stream.start()
        self.audiostreams.append(audio_stream)

        # Wait for stream to get active
        while not audio_stream.active:
           self.get_logger().info(f"audio stream for device{deviceportindex} ntemp_files_wavot working")
           pass

    def audio_callback(self, deviceportindex,indata, frames, time, status):
        # update indata to db data list
        with self.dbdata_lock[deviceportindex]:
            self.dbdata[deviceportindex].append(indata)

        self.plotaudio(deviceportindex,indata[:,0])
        # update indata to audio data list
        with self.audiodata_lock[deviceportindex]:
            start_idx = self.write_position[deviceportindex]
            end_idx = start_idx + frames
            self.audiodata[deviceportindex][start_idx:end_idx] = indata
            self.write_position[deviceportindex] = end_idx

            if self.write_position[deviceportindex] >= self.audiodata[deviceportindex].shape[0]:
                self.save_reset_buffer(deviceportindex)
    
    def plotaudio(self, deviceportindex, inputaudio,duration = 1):
        x = np.linspace(0, duration, len(inputaudio))
        self.line[deviceportindex].set_data(x, inputaudio)
        self.ax[deviceportindex].relim()
        self.ax[deviceportindex].autoscale_view(False, True, True) 
        # time.sleep(0.1)

    def save_reset_buffer(self, deviceportindex):
        if self.audiodata[deviceportindex] is None:
                self.get_logger().info(f"No audio received from mic {deviceportindex+1}")
                return
        try:
            # output_file = f"{self.output_filename}_{deviceportindex+1}_{self.buffer_num[deviceportindex]}_TEMP.wav"
            # wavfile.write(output_file, self.sample_rate, self.audiodata[deviceportindex].astype(np.float32))
            output_file = f"{self.output_filename}_{deviceportindex+1}_{self.buffer_num[deviceportindex]}_TEMP.bin"
            with open(output_file, 'ab') as f:
                f.write(self.audiodata[deviceportindex].astype(np.float32).tobytes())
                f.flush()
            # self.get_logger().info(f"Saved TEMP audio to {output_file}")
            self.buffer_num[deviceportindex] += 1
        except Exception as e:
            self.get_logger().error(f"Failed to save audio for mic {deviceportindex+1}: {e}")

        self.audiodata[deviceportindex] = np.full((self.sample_rate * self.buffertime, 1), None)
        self.write_position[deviceportindex] = 0
        # self.get_logger().info(f"reset buffer")

    def publish_db_data(self):
        #make db data  list and empty db_data_list
        msg = Float32MultiArray()
        msg.data = []
        for i in range(len(self.dbdata_lock)):
            with self.dbdata_lock[i]:
                if len(self.dbdata[i]) > 0:
                    data_array = np.vstack(self.dbdata[i])
                    self.dbdata[i] = []
                    rms_amplitude = np.sqrt(np.mean(np.square(data_array)))
                    db = -np.inf if rms_amplitude == 0 else 20 * np.log10(rms_amplitude / self.reference_amplitude)
                    msg.data.append(float(db))
                else:
                    msg.data.append(-9999999.9999) #placeholder for invalid data
                    self.get_logger().info(f"db data for mic{i+1} not obtained, {datetime.datetime.now()}")
        #publish message
        self.pub.publish(msg)   
        # self.get_logger().info(f"Data: {msg.data}")   
        
    def savewav(self):
        # with self.audio_data_lock:
        for i in range(len(self.audiodata_lock)):
            with self.audiodata_lock[i]:
                self.save_reset_buffer(i)
                try:
                    currentdateandtime = datetime.datetime.now()
                    output_file = f"{self.output_filename}_{currentdateandtime}_{i+1}.wav"

                    temp_files = [f"{self.output_filename}_{i + 1}_{buffer_idx}_TEMP.bin" for buffer_idx in range(1, self.buffer_num[i])]
                    
                    for buffer_idx in range(1, self.buffer_num[i]):
                        self.binary_to_wav(i, buffer_idx)

                    temp_files_wav = [f"{self.output_filename}_{i + 1}_{buffer_idx}_TEMP.wav" for buffer_idx in range(1, self.buffer_num[i])]
                    self.concatenate_and_save_wav(temp_files_wav, output_file)
                    # self.get_logger().info(f"Saved audio to {output_file}")
                    sd.wait()
                    self.delete_temp_files((temp_files + temp_files_wav))
                    # write(output_file, self.sample_rate, self.audiodata[i].astype(np.float32))
                except Exception as e:
                    self.get_logger().error(f"Failed to save final audio for mic {i+1}: {e}")

    def concatenate_and_save_wav(self, temp_files, output_file):
        all_audio_data = []
        for temp_file in temp_files:
            _, audio_data = wavfile.read(temp_file)
            all_audio_data.append(audio_data)
        concatenated_audio_data = np.concatenate(all_audio_data, axis=0)
        wavfile.write(output_file, self.sample_rate, concatenated_audio_data)
        # self.get_logger().info(f"Saved concatenated audio to {output_file}")

    def delete_temp_files(self, temp_files):
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                # self.get_logger().info(f"Deleted temporary file: {file}")

    def binary_to_wav(self, deviceportindex, buffer_num):
        try:
            input_file = f"{self.output_filename}_{deviceportindex+1}_{buffer_num}_TEMP.bin"
            output_file = f"{self.output_filename}_{deviceportindex+1}_{buffer_num}_TEMP.wav"
            with open(input_file, 'rb') as f:
                audio_data = np.frombuffer(f.read(), dtype=np.float32)
            wavfile.write(output_file, self.sample_rate, audio_data)
            # self.get_logger().info(f"Converted binary audio to WAV: {output_file}")
        except Exception as e:
            self.get_logger().error(f"Failed to convert binary to WAV for mic {deviceportindex+1}: {e}")

    def delete(self):
        # self.get_logger().info("I AM CALLED")
        for i in range(len(self.audiodata_lock)):
            self.audiostreams[i].stop()

        #join threads here before saving any wavs
        for threadt in self.micthreads:
            threadt.join()

        self.savewav()

        for i in range(len(self.audiodata_lock)):
            self.audiostreams[i].close()
        self.get_logger().info(f"Audio stream stopped")


def main():
    rclpy.init(args=None)
    deviceports = []
    deviceslist = sd.query_devices()
    nummics = 2
    for index,device in enumerate(deviceslist):
        if 'Lavalier' in device['name']:
            deviceports.append(index)

    plt.ion()
    fig, ax = plt.subplots(1,nummics)
    audio_publisher = AudioPublisher(deviceports[:2],nummics, fig,ax)

    try:
        rclpy.spin(audio_publisher)
    except KeyboardInterrupt:
        audio_publisher.get_logger().info("Shutting down publisher.")
    finally:
        audio_publisher.delete()
        audio_publisher.destroy_node()
        rclpy.shutdown()
        plt.close(fig)

if __name__ == "__main__":
    main()