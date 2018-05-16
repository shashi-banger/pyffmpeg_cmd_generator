What we want to achieve?
=========================

- Give a mechanism to fetch a reliable previously tested ffmpeg command given
  an input media file, output specification from a collection of commands
- A workflow between Ops, DevOps and Dev to evolve a collection of ffmpeg commands
- Track ffmpeg docker version which has been used to verify the commands


Output specification Description
================================

   ::

    OutProfile
            format: {"mxf","mov","mp4","mpg","ts"}
            vcodec: {"h264","mpeg2", "copy"}
            acodec: {"mp2", "aac", "pcm16", "pcm24" ,"copy"}
            n_aud_tracks: 1..16
            aud_ch: {1,2}
            vid_scan_type: {"interlaced", "progressive"}
            vid_resolution: {"640x480", "720x576", "1280x720", "1920x1080"}
            vid_fps: {29.97, 30.0, 25}
            aud_map: {f: (int,int) -> (int)  \/  f: (int) -> (int)}

    OutParams
            vid_bitrate: 400000..25000000
            aud_bitrate: 64000..512000


Workflow
=========

- Run the following command:

   ::

    > get_ffmpeg_command input_media.mp4 out_spec.txt

  If previously tested combination
       Returns an ffmpeg command that can be used -> (A)
  else
       Returns a candidate ffmpeg command that needs to be validated,
       (sha1, ffmpeg_command) -> (B)


- If A just go ahead and use the command

- If B try the candidate ffmpeg, test it -> (C)

- If C passes then, checkin sha1 in "golden verified" folder git

- If C fails that would need some update in "get_ffmpeg_command" -> D


Users
=====

3 levels of users

- Ops: Will only do A, if B raise request to DevOps
- DevOps: C to be done
- Dev: D
