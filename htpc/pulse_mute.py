import re
from subprocess import run, PIPE


class Pulse(object):

    @staticmethod
    def get_hw_sink():
        sinks = Pulse.get_sinks()
        if sinks:
            for sink in sinks:
                if sink != "nullsink":
                    return sink

    @staticmethod
    def get_sinks():
        proc = run(["pacmd","list-sinks"], check=True, stdout=PIPE)
        out = proc.stdout.decode("utf-8")
        pattern = 'name: <(.*?)>'
        return re.findall(pattern, out, flags=re.DOTALL)

    @staticmethod
    def get_index(appname):
        streams = Pulse.get_stream_list()
        pattern = 'index: ([0-9]*)'
        if streams:
            for stream in streams:
                index = re.findall(pattern,stream, flags=re.DOTALL)[0]
                if re.findall(appname, stream, flags=re.DOTALL):
                    return index

    @staticmethod
    def mute_input(appname):
        index = Pulse.get_index(appname)
        if index:
            Pulse.move_sink(index,"nullsink")

    @staticmethod
    def unmute_input(appname):
        index = Pulse.get_index(appname)
        if index:
            hwsink = Pulse.get_hw_sink()
            Pulse.move_sink(index,hwsink)

    @staticmethod
    def move_sink(index,sinkname):
        if index and sinkname:
            print("moving sink input %s to sink output %s" % (index,sinkname))
            p = run(["pacmd","move-sink-input",index,sinkname], check=True, stdout=PIPE)
            print("Out: %s\n Returncode: %s" % (p.stdout,p.returncode))
            if p.returncode == 1 or "failed" in p.stdout.decode("utf-8"):
                run(["pacmd","kill-sink-input",index], check=True, stdout=PIPE)

    @staticmethod
    def get_info(appname):
        streams = Pulse.get_stream_list()
        if streams:
            for stream in streams:
                if re.findall(appname, stream, flags=re.DOTALL):
                    pattern = 'index: ([0-9]*).*?module-stream-restore.id = "(.*?)"'
                    return re.findall(pattern,stream, flags=re.DOTALL)[0]
        return ("","")

    @staticmethod
    def get_stream_list():
        proc = run(["pacmd", "list-sink-inputs"], check=True, stdout=PIPE)
        out = proc.stdout.decode("utf-8")

        pattern = 'index: [0-9]*?.*?module-stream-restore.id = ".*?"\n'
        return re.findall(pattern, out, flags=re.DOTALL)

    @staticmethod
    def mute(appname):
        index,restore_id = Pulse.get_info(appname)
        if index:
            proc = run(["pactl","set-sink-input-mute", index, "1"])
        return restore_id

    @staticmethod
    def unmute(appname, restore_id):
        tdb_file = "/home/zteifel/.config/pulse/63004b801bad430a96cbe372c12ce1f3-stream-volumes.tdb"
        index, tmp = Pulse.get_info(appname)
        if index:
            proc = run(["pactl","set-sink-input-mute", index, "0"])
        elif restore_id:
            proc = run(["tdbtool", tdb_file, "delete", restore_id])
            proc = run(["/usr/bin/pasuspender", "/bin/true"])

