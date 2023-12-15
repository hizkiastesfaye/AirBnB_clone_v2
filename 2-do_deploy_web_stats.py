#!/usr/bin/env python3
"""
Fabric script that distributes an archive to your web servers
"""

from datetime import datetime
from fabric import Connection, task
from invoke import run as local_run
import os

env = {
    "hosts": ["54.227.128.156", "35.174.213.137"],
    "user": "ubuntu"
}

@task
def dopack(c):
    """
    Return the archive path if the archive has been generated correctly.
    """

    c.run("mkdir -p versions")
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    archived_f_path = f"versions/web_static_{date}.tgz"
    t_gzip_archive = local_run("tar -cvzf {} web_static".format(archived_f_path))

    if t_gzip_archive.ok:
        return archived_f_path
    else:
        return None

@task
def deploy(c, archivepath):
    """
    Distribute archive.
    """
    if os.path.exists(archivepath):
        archived_file = archivepath[9:]
        newest_version = "/data/web_static/releases/" + archived_file[:-4]
        archived_file = "/tmp/" + archived_file
        c.put(archivepath, "/tmp/")
        c.run("sudo mkdir -p {}".format(newest_version))
        c.run("sudo tar -xzf {} -C {}/".format(archived_file, newest_version))
        c.run("sudo rm {}".format(archived_file))
        c.run("sudo mv {}/web_static/* {}".format(newest_version, newest_version))
        c.run("sudo rm -rf {}/web_static".format(newest_version))
        c.run("sudo rm -rf /data/web_static/current")
        c.run("sudo ln -s {} /data/web_static/current".format(newest_version))

        print("New version deployed!")
        return True

    return False
