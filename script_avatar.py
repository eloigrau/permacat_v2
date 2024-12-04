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


def avatar(taille="40"):
    #Browse along file tree
    print(str(root_path))
    for f in glob.glob(root_path+"/**/"+taille+"/*.png",   recursive=True):
        split = f.split("40/")
        print("plis" + str(split))
        if len(split) == 2:
            f_new = split[0] + ""+taille+"/"+taille+"/" + split[1]
            cmd_data = ["mkdir", split[0] + ""+taille+"/"+taille]
            cmd = " ".join(cmd_data)
            print(cmd)
            subprocess.run(cmd_data)
            cmd_data = ["mv", f, f_new]
            cmd = " ".join(cmd_data)
            print(cmd)
            subprocess.run(cmd_data)
        #subprocess.run(["rm", f])
#test
if __name__ =="__main__":
    pass
    #avatar("40")
    #avatar("80")