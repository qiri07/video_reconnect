# video_reconnect 视频流 断链重连处理
use python opencv lib to process video streaming while the network is down and reconnect.

1 stream_url 传入本地视频流地址 或者网络视频流地址 ，比如 rtsp,rtmp都可以

2 通过 ThreadPoolExecutor 启动2个线程处理 视频 线程1 负责将视频流 存储 队列，线程2 负责将队列缓存视频 保存成文件.mp4

3 不论是启动程序后，视频流是中断的，还是 运行中 视频流中断，都可断联重连处理。

场景：传入视频流地址，进行视频 算法处理，确保视频流的网络波动不稳定，进行的 视频流断线重连处理
the tools to push streaming can use OBS,ffmpeg etc. the MediaCenter can use ZLMediaServer
