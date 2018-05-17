What we want to achieve?
=========================

- Give a mechanism to generate ffmpeg command based on the specifications given in
  next section
- The generated ffmpeg command is wrapped in another script so that when exercised
  on a new input file it will validate the input spec used during command generation.
  Failure will result in abort.


Output specification Description
================================

   ::

    Output File Spec
            format: {"mxf","mov","mp4","mpg","ts"}
            vcodec: {"h264","mpeg2", "copy"}
            acodec: {"mp2", "aac", "pcm16", "pcm24" ,"copy"}
            n_out_aud_tracks: 1..16
            aud_ch: {1,2}
            vid_out_resolution: {"640x480", "720x576", "1280x720", "1920x1080"}
            vid_out_fps: {29.97, 30.0, 25}
            vid_out_bitrate: "40000..25000000"[kKM]
            aud_map_[N]: {f: (int,int) -> (int)  \/  f: (int) -> (int)}

    Input File Spec
            vid_inp_scan_type={"interlaced","progressive"}
            n_inp_aud_tracks:1..16


Workflow
=========

- Run the following command:

   ::

    > python ffmpeg_cmd_gen.py <inpute_spec.txt> <output_transcode.py>

   This command will generate an output_transcode.py file which can be used to transcode
   a media file.

- To transcode an input media file to output media file the following command can be used.
  output_transcode.py is generated from the previous command.

   ./output_transcode.py <input_media> <output_media>
