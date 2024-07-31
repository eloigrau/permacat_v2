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
        subprocess.run(["rm", f])

    for f in glob.glob(root_path+"/**/*.jpg",   recursive=True):
        print(" ".join(["mogrify", "-format", "png", f]))
        subprocess.run(["mogrify", "-format", "png", f])
        subprocess.run(["rm", f])

    for f in glob.glob(root_path+"/**/*.JPG",   recursive=True):
        print(" ".join(["mogrify", "-format", "png", f]))
        subprocess.run(["mogrify", "-format", "png", f])
        subprocess.run(["rm", f])


def avatar():
    #Browse along file tree
    print(str(root_path))
    print(glob.glob(root_path+"**/40/*.png",   recursive=True))
    for f in glob.glob(root_path+"**/40/*.png",   recursive=True):
        f_new = f.split("40/")[0] + "/40/40/" + f.split("40/")[1]
        cmd_data = ["mv", f, "png", f]
        cmd = " ".join(cmd_data)
        print(cmd)
        #subprocess.run(cmd)
        #subprocess.run(["rm", f])
#test
if __name__ =="__main__":
    avatar()
    import shutil