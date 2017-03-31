import subprocess, os

cwd = os.getcwd() + '/app/docker/'  # unsure if this is ./ or ./docker/


def create(instance):
    ORG_NAME = instance.sanitized_name()
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT
    SECRET = instance.secret

    subprocess.Popen(['sh', 'scripts/new_instance.sh', APP_NAME, ORG_NAME,
                      PORT, SECRET], cwd=cwd)

    return True


def stop(instance):
    ORG_NAME = instance.sanitized_name()
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT

    subprocess.Popen(['sh', 'scripts/stop_instance.sh', APP_NAME], cwd=cwd)

    return True
