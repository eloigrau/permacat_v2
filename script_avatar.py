import os
root_path = '/home/udjango/permacat/bourseLibre/media/avatars'
#root_path = '/home/tchenrezi/PycharmProjects/permacat_ok/bourseLibre/media/avatars'

import os, sys, re, subprocess

import glob

def Browse_file():
    #Browse along file tree
    print(str(root_path))
    for f in glob.glob(root_path+"/**/*.jpeg",   recursive=True):
        print(" ".join(["mogrify", "-format", "png", f]))
        subprocess.run(["mogrify", "-format", "png", f])

    for f in glob.glob(root_path+"/**/*.jpg",   recursive=True):
        print(" ".join(["mogrify", "-format", "png", f]))
        subprocess.run(["mogrify", "-format", "png", f])
#test
if __name__ =="__main__":
    Browse_file()
    import shutil