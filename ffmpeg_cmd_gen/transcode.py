import subprocess,shlex
import re

def get_media_info(f):
    cmd = "mediainfo %s" % f
    cmd_args = shlex.split(cmd)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
    o,e = p.communicate()

    media_info = dict()
    for l in o.split('\n'):
        if len(l) > 0 and ':' in l:
            s = l.split(':')
            kv = (s[0].strip(), s[1].strip())
            media_info[cur_k + '.' + kv[0]] = kv[1]
        elif len(l) > 0:
            cur_k = l.strip()

    return media_info


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print "Usage: ./transcode.py <input_file_path> <output_file_path>"

    m_info = get_media_info(sys.argv[1])
    scan_type_key = filter(lambda s: re.match('Video[ #0-9]*.Scan type', s), m_info.keys())
    na = len(filter(lambda s: re.match('Audio[ #0-9]*.ID', s), m_info.keys()))
    expected_scan_type = "{scan_type}"
    if m_info[scan_type_key[0]].lower() != expected_scan_type:
        print "Input scan type " +  m_info[scan_type_key[0]] + " not correct for ffmpeg command"
        sys.exit(1)

    expected_num_aud = {num_aud}
    if na != expected_num_aud:
        print "Input file num audio tracks " + str(na) + " does not match expected num aud tracks " + str(expected_num_aud)
        sys.exit(1)

    ffmpeg_cmd = '{ffmpeg_cmd}' % (sys.argv[1], sys.argv[2])
    cmd_args = shlex.split(ffmpeg_cmd)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
    o,e = p.communicate()
