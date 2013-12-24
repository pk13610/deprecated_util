#!/usr/bin/env python
# coding=utf-8

import os
from sys import argv
import zipfile
from time import localtime, strftime

def zip_file(src, dest):
    if src == dest:
        raise ValueError(r"error! src == dest")
    zf = zipfile.ZipFile(dest, "w", zipfile.zlib.DEFLATED)
    zf.write(src, os.path.basename(src))
    zf.close()

def zip_dir(dirname, zipfilename, ignore={}, linkfile=True):
    tmp = zipfilename + '!'
    try:
        filelist = []
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else:
            for root, dirs, files in os.walk(dirname):
                for fname in files:
                    filelist.append(os.path.join(root, fname))
        zf = zipfile.ZipFile(tmp, "w", zipfile.zlib.DEFLATED)

        link_files = []
        for tar in filelist:
            try:
                if os.path.islink(tar):
                    # print 'ignore link file: ', tar
                    link_files.append(
                        "ln -s %s %s\n"%(
                            os.readlink(tar).replace(" ", r"\ "), 
                            tar.replace(" ", r"\ ")
                        )
                    )
                    continue
                arcname = tar[len(dirname):]
                ignored = False
                for tt in ignore:
                    if tt in arcname.split('/'):
                        # print 'ignore dir/file file: ', tar
                        ignored = True
                        break
                if not ignored:
                    zf.write(tar, arcname)
            except Exception as e:
                print e
        if len(link_files) > 0:
            link_files_sh = os.path.join(dirname, "!recover_link_files.sh")
            open(link_files_sh, "w").writelines(link_files)
            zf.write(link_files_sh, "_link_files.sh")
            os.remove(link_files_sh)
        zf.close()
        os.rename(tmp, zipfilename)
    except Exception as e:
        print e
        os.remove(tmp)

def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir): os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

home = os.environ['HOME']
curr_time = lambda: strftime("%Y%m%d%H%M%S", localtime())

if __name__ == "__main__":
    import getopt
    import json

    cfg_file = __file__[0: __file__.rfind('.')] + r'.json'
    opts, args = getopt.getopt(argv[1:], "c:")
    for k, v in opts:
        if k in ("-c"):
            cfg_file = os.path.abspath(cfg_file)
    config = json.load(open(cfg_file))
    outpath = config["outpath"].replace("%(home)", home)
    outpath = os.path.join(outpath, curr_time())
    for setting in config['settings']:
        name = setting['name']
        path = setting['path'].replace("%(home)", home)
        ignore = setting['ignore']
        linkfile = setting['linkfile']
        print name, path, ignore
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        if os.path.isdir(path):
            out = os.path.join(outpath, "d[" + name + "].zip")
            zip_dir(path, out, ignore, linkfile)
        if os.path.isfile(path):
            out = os.path.join(outpath, "f[" + name + "].zip")
            zip_file(path, out)
