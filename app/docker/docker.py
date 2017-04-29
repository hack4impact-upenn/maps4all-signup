import subprocess
import os

cwd = os.getcwd() + '/app/docker/'  # unsure if this is ./ or ./docker/


def create(instance):
    ORG_NAME = instance.sanitized_name()
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT
    SECRET = instance.secret

    ADMIN_USER = instance.email
    ADMIN_PASSWORD = instance.default_password  # password can only be got once

    subprocess.Popen(['sh', 'scripts/new_instance.sh', APP_NAME, ORG_NAME,
                      PORT, SECRET, ADMIN_USER, ADMIN_PASSWORD], cwd=cwd)

    return True


def stop(instance):
    ORG_NAME = instance.sanitized_name()
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT

    subprocess.Popen(['sh', 'scripts/stop_instance.sh', APP_NAME], cwd=cwd)

    return True


def start(instance):
    ORG_NAME = instance.sanitized_name()
    PORT = str(instance.port)
    APP_NAME = ORG_NAME.replace(' ', '-') + '_p' + PORT

    subprocess.Popen(['sh', 'scripts/start_instance.sh', APP_NAME], cwd=cwd)

    return True
