from schema import Schema, And, Use, Optional, Or, Regex
import re


inp_spec_schema = Schema({'format': And(str, Use(str.lower), lambda s: s in ('mxf', 'ts', 'mov', 'mp4', 'mpg')),
                           'vcodec': And(str, Use(str.lower), lambda s: s in ('h264', 'm2v', 'copy')),
                           'acodec': And(str, Use(str.lower), lambda s: s in ('mp2', 'aac', 'copy')),
                           'n_out_aud_tracks': And(Use(int), lambda n: 1 <= n <= 16),
                           'aud_ch': And(Use(int), lambda n: 1 <= n <= 2),
                           'vid_out_resolution': And(str, Use(str.lower), lambda s: s in ('1920x1080', '1280x720', '720x576',\
                                                                                          '720x480', '640x480')),
                          'vid_out_bitrate': Or(And(Use(int)), And(Regex('[0-9\.]*[kK]'), Use(str)),\
                                                And(Regex('[0-9\.]*[M]'), Use(str))),
                           'vid_out_fps': And(str, Use(float), lambda f: f in [25.0, 29.97, 30.0]),
                          #Optional(Regex('aud_map')): Or(((Use(int),Use(int), Use(int))), Use(tuple(Use(int), Use(int)))),
                          Optional(Regex('aud_map')): Or(And(str, Use(eval), lambda (a,b): 1<=a<16 and 1<=b<=16),\
                                                         And(str, Use(eval), lambda ((a,b), c): 1<=a<16 and 1<=b<=16 and 1<=c<=16)),
                          'vid_inp_scan_type': And(str, Use(str.lower), lambda s: s in ('progressive', 'interlaced')),
                          'n_inp_aud_tracks': And(Use(int), lambda n: 1 <= n <=16)
                          })




def read_inp_spec(fname):
    o_dict = {}
    with open(fname) as fd:
        for l in fd:
            l = l.strip()
            if len(l) > 0 and l[0] != '#' and '=' in l:
                print l
                k,v = l.split('=')
                o_dict[k.strip()] = v.strip()
    return o_dict

def header():
    return 'ffmpeg -y -i "%s" '

def video(spec):
    video = "-pix_fmt yuv420p "
    video += "-vcodec %s " % (spec['vcodec'])
    if spec['vcodec'] == 'h264':
        video += "-x264opts nal-hrd=cbr "
        video += "-profile:v high "
        if spec['vid_inp_scan_type'] == 'interlaced':
            video += "-flags +ilme+ildct -top 1 "

    if d['vid_out_bitrate'][-1] in 'kK':
        o_bitrate = int(d['vid_out_bitrate'][:-1]) * 1000
    elif d['vid_out_bitrate'][-1] in 'M':
        o_bitrate = int(d['vid_out_bitrate'][:-1]) * 1000000
    else:
        o_bitrate = int(d['vid_out_bitrate'][:-1])

    video += "-vb %d -minrate:v %d -maxrate:v %d -bufsize:v %d " % (o_bitrate, o_bitrate, o_bitrate, (2*o_bitrate))
    return video

def audio(spec):
    audio = ""
    if spec['acodec'] == 'aac':
        audio += '-acodec %s ' %"libfdk_aac"
    else:
        audio += '-acodec %s ' % spec['acodec']

    if spec['acodec'] != 'copy':
        audio += '-ab 192k '
    return audio

def video_filter(spec):
    vf = '-vf \"fps=%f,scale=%s\" ' % (spec['vid_out_fps'],spec['vid_out_resolution'])
    return vf

def audio_filter_complex(spec):
    amapping = ""
    afilter = ""
    amap_spec = {}
    for k in spec.keys():
        if re.match('aud_map_', k):
            amap_spec[k] = spec[k]

    afilter_val = ""
    if len(amap_spec.keys()) > 0:
        type_amap = type(amap_spec[amap_spec.keys()[0]][0])
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

if __name__ == "__main__":
    import sys
    d = read_inp_spec(sys.argv[1])
    d = inp_spec_schema.validate(d)

    afilt, amap = audio_filter_complex(d)

    ffmpeg_cmd = header() + video_filter(d) + afilt + video(d) + audio(d) + "-map 0:v " + amap + '"%s"'

    with open("transcode.py") as fd:
        s = fd.read()
        print s
        s = s.format(scan_type=d['vid_inp_scan_type'], num_aud=d['n_inp_aud_tracks'], ffmpeg_cmd=ffmpeg_cmd)
        ofd = open(sys.argv[2], "w")
        ofd.write(s)
        ofd.close()
    print ffmpeg_cmd
