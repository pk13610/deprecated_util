#!/usr/bin/env python
# coding=utf-8

import os
import sys
import gzip
import zipfile
import time

def zip_file(src, dest):
    if src == dest:
        raise "src == dest"
    zf = zipfile.ZipFile(dest, "w", zipfile.zlib.DEFLATED)
    zf.write(src, os.path.basename(dest))
    zf.close()
 
def zip_dir(dirname, zipfilename, ignore={}, linkfile=True):
    tmp = zipfilename + '!'
    try:
        filelist = []
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else :
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root, name))
        zf = zipfile.ZipFile(tmp, "w", zipfile.zlib.DEFLATED)

        for tar in filelist:
            try:
                if os.path.islink(tar):
                    print 'ignore link file: ', tar
                    continue
                arcname = tar[len(dirname):]
                ignored = False
                for tt in ignore:
                    if tt in arcname.split('/'):
                        print 'ignore dir/file file: ', tar
                        ignored = True
                        break
                if not ignored:
                    zf.write(tar,arcname)
            except Exception as e:
                print e
        zf.close()
        os.rename(tmp, zipfilename)
    except Exception as e:
        print e
        os.remove(tmp)
 
def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\','/')
        
        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:           
            ext_filename = os.path.join(unziptodir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir) : os.mkdir(ext_dir,0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

"""
backup local settings to some place,say dropbox
"""

home = os.environ['HOME']
curr_time = lambda : time.strftime("%Y%m%d%H%M%S", time.localtime())
dropbox = os.path.join(home, "app/dropbox/Dropbox/SysBackup/autobackup")

settings = [
                {
                    "name": "user.bash_profile",
                    "path": os.path.join(home, ".bash_profile"),
                    "ignore": ['.git'],
                    "linkfile": False
                },
                {
                    "name": "user.ssh",
                    "path": os.path.join(home, ".ssh"),
                    "ignore": ['.git'],
                    "linkfile": False
                },
                {
                    "name": "user.bin",
                    "path": os.path.join(home, "bin"),
                    "ignore": ['.git', '.log'],
                    "linkfile": False
                },
                {
                    "name": "user.etc",
                    "path": os.path.join(home, "etc"),
                    "ignore": ['.git', '.log', 'log'],
                    "linkfile": False
                },
                {
                    "name": "xampp.etc",
                    "path": "/Applications/XAMPP/etc",
                    "ignore": ['.git', '.log', 'log'],
                    "linkfile": False
                },
]

if __name__ == "__main__":

    for setting in settings:
        name = setting['name']
        path = setting['path']
        ignore = setting['ignore']
        linkfile = setting['linkfile']
        print name, path, ignore
        outpath = os.path.join(dropbox, curr_time())
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        if os.path.isdir(path):
            out = os.path.join(outpath, "d["+name+"].zip")
            zip_dir(path, out, ignore, linkfile)
        if os.path.isfile(path):
            out = os.path.join(outpath, "f["+name+"].zip")
            zip_file(path, out)

