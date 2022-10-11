from math import fabs
import time
import os
import queue
import sys
import logging
import concurrent.futures

try:
    import cv2 as cv
except ImportError:
    sys.stderr.write("This example requires opencv-python is installed")
    raise

output_path = "Output"
log = logging.getLogger(__name__)
video_buffer = queue.Queue()

def save_video_to_buffer(stream_url, cap, num_second_per_clips=None, frame_height=None, frame_width=None):
    global video_buffer
    print('##########cap is init with url : {}'.format(stream_url))
    log.info("{} - Loading stream {}".format(time.strftime("%Y-%m-%d %H:%M:%S"),stream_url))
    isReConnected=False
    is_run, frame_s = cap.read()
    while not is_run:
        # reconnect
        time.sleep(0.1)
        print('{} - cap before reconnect with url : {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"),stream_url))
        cap = cv.VideoCapture(stream_url)
        is_run, frame_s = cap.read()

    fps = cap.get(cv.CAP_PROP_FPS)
    # step get video info
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    num_frame_per_clip = int(num_second_per_clips * fps)

    if frame_height is None:
        dst_height = height
    else:
        dst_height = frame_height
    if frame_width is None:
        dst_width = width
    else:
        dst_width = frame_width
    isSave=True
    print('{} - in the buffer put loop '.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    frames = []
    try:
        tmp_stamp = time.strftime("%Y%m%d%H%M%S")
        for _ in range(num_frame_per_clip):
            is_opened, frame = cap.read()
            while not is_opened:
                # reconnect
                time.sleep(0.1)
                print('{} - cap inner reconnect with url : {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"),stream_url))
                cap = cv.VideoCapture(stream_url)
                is_opened, frame = cap.read()
                isReConnected=is_opened
            if isReConnected:
                isReConnected=False
                isSave=False
                break
            frame = cv.resize(frame, (dst_width, dst_height))
            frames.append(frame)
            
            print('working .... frames put frame...')
        if isSave:
            video_buffer.put((tmp_stamp, frames))
            print('$$$$$$$$$$ video_buffer put frame...')
        else:
            video_buffer.queue.clear()
            print('---------- video_buffer clear frame...')
    except Exception as ex:
        # reconnect
        print('except out {}'.format(ex))
    except KeyboardInterrupt:
        print('KeyboardInterrupt Exit')
    print('{} - Finish the loop put frame...'.format(time.strftime("%Y-%m-%d %H:%M:%S")))

def save_video(fps, save_path, video_name, video, dst_height, dst_width):
    fourcc = cv.VideoWriter_fourcc(*'MP4V')  # MPEG-4 codec

    video_path = os.path.join(save_path, str(video_name) + '.mp4')
    out = cv.VideoWriter(filename=video_path, fourcc=fourcc, fps=fps, frameSize=(dst_width, dst_height),
                         isColor=True)
    try:
        for i in range(len(video)):
            out.write(video[i])
        out.release()
        # cap.release()
    except cv.error as e:
        print(f"Failed to save video, due to {e}")
        raise e
    print('{} Finish write file {}.mp4 to DISK...'.format(time.strftime("%Y-%m-%d %H:%M:%S"),video_name))

def save_buffer_to_device(fps, save_path):
    global video_buffer

    if video_buffer.empty() is False:
        video_name, video = video_buffer.get()
        dst_height = video[0].shape[0]
        dst_width = video[0].shape[1]
        save_video(fps, save_path, video_name, video, dst_height, dst_width)

def save_video_stream(stream_url, output_path, num_second_per_clips=5):
    try:
        cap = cv.VideoCapture(stream_url)
        while True:
            is_true, frame_i = cap.read()
            while not is_true:
             # reconnect
                time.sleep(0.1)
                print('cap first reconnect with url : {}'.format(stream_url))
                cap = cv.VideoCapture(stream_url)
                is_true, frame_i = cap.read()
            
            fps = cap.get(cv.CAP_PROP_FPS)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(save_video_to_buffer, stream_url,
                                cap, num_second_per_clips)
                executor.submit(save_buffer_to_device, fps, output_path)
    except Exception as ex:
        print("except of {}".format(ex))

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(filename='D:/example.log', level=logging.INFO)
    #stream_url = 'rtsp://127.0.0.1/live/test'
    stream_url = 'rtmp://172.16.99.27/live/test'

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    save_video_stream(stream_url, output_path, num_second_per_clips=5)