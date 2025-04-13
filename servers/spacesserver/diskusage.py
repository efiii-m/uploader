import subprocess

def get_spaces():
    command = ['bash', '-c', 'du -s -B 1 /tmp ~/.[!.]* ~/* | awk \'{s+=$1}END{print s}\'']
    res = subprocess.run(command, capture_output=True, text=True)
    total = 512000000
    data = {
        "totalspace": total / 1000000,
        "freespace": (total - int(res.stdout)) / 1000000,
        "usedspace": int(res.stdout) / 1000000
    }

    return data