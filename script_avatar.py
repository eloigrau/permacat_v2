import os
root_path = '/home/tchenrezi/PycharmProjects/permacat_ok/bourseLibre/media/avatars/'
root_path = '/home/tchenrezi/PycharmProjects/permacat_ok/bourseLibre/media/avatars/'

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
    for f in glob.glob(root_path+"/**/40/*.png",   recursive=True):
        split = f.split("40/")
        #print("plis" + str(split))
        if len(split)==2:
            f_new = split[0] + "40/40/" + split[1]
            cmd_data = ["mkdir", split[0] + "40/40/"]
            cmd = " ".join(cmd_data)
            print(cmd)
            cmd_data = ["mv", f, f_new]
            cmd = " ".join(cmd_data)
            print(cmd)
        #subprocess.run(cmd)
        #subprocess.run(["rm", f])
#test
if __name__ =="__main__":
    avatar()
    import shutil