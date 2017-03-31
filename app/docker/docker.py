import subprocess

cwd = './'  # unsure if this is ./ or ./docker/


def filter(source):
    return ''.join(c for c in source if c.isalnum() or c == ' ')


def create(instance):
    ORG_NAME = filter(instance.name)
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT
    SECRET = 'supersecretkeyshhhh'

    subprocess.Popen(['sh', 'scripts/new_instance.sh', APP_NAME, ORG_NAME,
                      PORT, SECRET], cwd='./')

    return True


def delete(instance):
    ORG_NAME = filter(instance.name)
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT

    subprocess.Popen(['sh', 'scripts/stop_instance.sh', APP_NAME], cwd='./')

    return True
