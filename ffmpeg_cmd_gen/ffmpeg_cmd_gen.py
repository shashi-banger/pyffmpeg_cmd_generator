from schema import Schema, And, Use, Optional, Or, Regex
import re
import sys


inp_spec_schema = Schema({'format': And(str, Use(str.lower), lambda s: s in ('mxf', 'ts', 'mov', 'mp4', 'mpg')),
                           'vcodec': And(str, Use(str.lower), lambda s: s in ('h264', 'mpeg2video', 'copy')),
                           'acodec': And(str, Use(str.lower), lambda s: s in ('mp2', 'aac', 'pcm_s24le', 'ac3', 'copy')),
                           'n_out_aud_tracks': And(Use(int), lambda n: 1 <= n <= 16),
                           'aud_ch': And(Use(int), lambda n: 1 <= n <= 2),
                           'gop_length': And(Use(int)),
                           'vid_out_resolution': And(str, Use(str.lower), lambda s: s in ('1920x1080', '1280x720', '720x576',\
                                                                                          '720x480', '640x480')),
                          'vid_out_bitrate': Or(And(Use(str)), And(Regex('[0-9\.]*[kK]'), Use(str)),\
                                                And(Regex('[0-9\.]*[M]'), Use(str))),
                           'vid_out_fps': And(str, Use(float), lambda f: f in [25.0, 29.97, 30.0]),
                          #Optional(Regex('aud_map')): Or(((Use(int),Use(int), Use(int))), Use(tuple(Use(int), Use(int)))),
                          Optional(Regex('aud_map')): Or(And(str, Use(eval), lambda a: 1<=a[0]<16 and 1<=a[1]<=16),\
                                                         And(str, Use(eval), lambda a: 1<=a[0][0]<16 and 1<=a[0][1]<=16 and 1<=a[1]<=16)),
                          'vid_inp_scan_type': And(str, Use(str.lower), lambda s: s in ('progressive', 'interlaced')),
                          'n_inp_aud_tracks': And(Use(int), lambda n: 1 <= n <=16),
                           'streamid_vid': And(Use(int)),
                           'streamid_aud_start': And(Use(int))
                          })



def _get_vid_bitrate_(s, d):
    if s[-1] in 'kK':
        o_bitrate = int(s[:-1]) * 1000
    elif d['vid_out_bitrate'][-1] in 'M':
        o_bitrate = int(s[:-1]) * 1000000
    else:
        o_bitrate = int(s[:-1])
    return o_bitrate


def read_inp_spec(fname):
    o_dict = {}
    with open(fname) as fd:
        for l in fd:
            l = l.strip()
            if len(l) > 0 and l[0] != '#' and '=' in l:
                #print l
                k,v = l.split('=')
                o_dict[k.strip()] = v.strip()
    return o_dict

def header():
    return 'ffmpeg -y -i "%s" '

def video(spec):
    if spec['vcodec'] == 'copy':
        return "-vcodec copy "

    video = "-pix_fmt yuv420p  "
    video += "-vcodec %s -g %d -bf 2 " % (spec['vcodec'], spec['gop_length'])
    if spec['vcodec'] == 'h264':
        video += "-x264opts nal-hrd=cbr "
        video += "-profile:v high "
        if spec['vid_inp_scan_type'] == 'interlaced':
            video += "-flags +ilme+ildct -top 1 "
    elif spec['vcodec'] == 'mpeg2video':
        video += "-profile:v 4 -level:v 4 " #mp@hl: https://forum.videohelp.com/threads/345143-mpeg2-MP-ML-with-ffmpeg
        if spec['vid_inp_scan_type'] == 'interlaced':
            video += "-flags +ilme+ildct -top 1 "

    if spec['vid_out_bitrate'][-1] in 'kK':
        o_bitrate = int(spec['vid_out_bitrate'][:-1]) * 1000
    elif spec['vid_out_bitrate'][-1] in 'M':
        o_bitrate = int(spec['vid_out_bitrate'][:-1]) * 1000000
    else:
        o_bitrate = int(spec['vid_out_bitrate'][:-1])

    video += "-vb %d -minrate:v %d -maxrate:v %d -bufsize:v %d " % (o_bitrate, o_bitrate, o_bitrate, int(0.5*o_bitrate))
    return video

def audio(spec):
    audio = " -ar 48000 "
    if spec['acodec'] == 'aac':
        audio += '-acodec %s -profile:a aac_low ' %"libfdk_aac"
    else:
        audio += '-acodec %s ' % spec['acodec']

    if spec['acodec'] != 'copy' or re.match('pcm', spec['acodec']):
        audio += '-ab 192k '
    return audio

def video_filter(spec):
    if spec['vcodec'] != 'copy':
        vf = '-vf \"fps=%f,scale=%s\" ' % (spec['vid_out_fps'],spec['vid_out_resolution'])
    else:
        vf = ""

    return vf

def audio_filter_complex(spec):
    amapping = ""
    afilter = ""
    amap_spec = {}
    for k in spec.keys():
        if re.match('aud_map_', k):
            amap_spec[k] = spec[k]

    afilter_val = ""

    amap_keys = list(amap_spec.keys())
    if len(amap_spec.keys()) > 0:
        type_amap = type(amap_spec[amap_keys[0]][0])
        if type_amap == tuple:
            afilter = "-filter_complex "
            aindex = 0
            for k in amap_spec.keys():
                afilter_val += "[0:a:%d][0:a:%d]amerge=inputs=2[aout%d]," % (amap_spec[k][0][0] - 1, amap_spec[k][0][1] - 1,aindex)
                amapping += '-map ["aout%d"] ' % aindex
                aindex += 1
            afilter_val = afilter_val[:-1] # Removing trailing ,
            afilter += '"%s" ' % afilter_val
        elif type_amap == int:
            amap_list = [(amap_spec[k]) for k in amap_spec.keys()]
            sorted(amap_list, key=lambda a: (a[1] - 1))
            for a in amap_list:
                amapping += "-map 0:a:%d " % (a[0] - 1)

    return (afilter, amapping)

def muxer_params(spec):
    mux_params = ""
    if spec['format'] == 'ts':
        vb = _get_vid_bitrate_(spec['vid_out_bitrate'], spec)
        mux_rate = vb + 192000*spec['n_out_aud_tracks']
        mux_rate = 1.1 * mux_rate
        mux_params = " -muxrate %d " % int(mux_rate)
        mux_params += " -streamid 0:%d " % spec['streamid_vid']
        for i in range(spec['n_out_aud_tracks']):
            mux_params += " -streamid %d:%d " % (i+1, spec['streamid_aud_start'] + i)
    return mux_params



import inspect
import transcode
def main():
    if len(sys.argv) < 3:
        print("Usage: ffmpeg_cmd_gen <input_spec> <output_transcode_file.py>")
        sys.exit(1)
    d = read_inp_spec(sys.argv[1])
    d = inp_spec_schema.validate(d)

    afilt, amap = audio_filter_complex(d)

    ffmpeg_cmd = header() + video_filter(d) + afilt + video(d) + audio(d) + "-map 0:v " + amap + muxer_params(d) + \
                                          " -vsync 1 -async 1 " '"%s"'

    # Create the wrapper output puthon file which will transcode using above generated command
    # and will ensure that the input media has the same input spec as to this command
    #with open("transcode.py") as fd:
    if(True):
        s = inspect.getsource(transcode)
        #s = fd.read()
        #print s
        s = s.format(scan_type=d['vid_inp_scan_type'], num_aud=d['n_inp_aud_tracks'], ffmpeg_cmd=ffmpeg_cmd)
        ofd = open(sys.argv[2], "w")
        ofd.write(s)
        ofd.close()
    print(ffmpeg_cmd)


if __name__ == "__main__":
    main()
