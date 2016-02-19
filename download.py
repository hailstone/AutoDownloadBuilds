# -*- coding: utf-8 -*-
import os
import re
import urllib
import time
import setup

__author__ = 'hailstone01'


def get_length_from_server(single_build_download_url):
    page = urllib.urlopen(single_build_download_url)
    # the Content-Length part is something like: 'Content-Length: 27107189'
    result_list = re.findall("Content-Length: \d+", str(page.headers))
    if len(result_list) != 1:
        print "get the length of %r failed, return 0 as the result" % single_build_download_url
        return 0
    else:
        length = "".join(result_list).split(":")[1].strip()
        return int(length)


def url_call_back(a, b, c):
    print "callback"
    prec = 100 * a * b / c
    if 100 < prec:
        prec = 100
        print "let prec = 100"
    print "%.2f%%" % prec


def is_already_downloaded(download_url, local_dir):
    print "enter is_already_downloaded function"
    filename = download_url.split("/")[-1]
    if filename not in os.listdir(local_dir):
        print "file not in the local dir, return False"
        return False
    return True

    # local_build_size = os.path.getsize(local_dir + os.sep + filename)
    # print "local build length:", local_build_size
    #
    # server_build_size = get_length_from_server(download_url)
    # print "server build length:", server_build_size
    #
    # if local_build_size == server_build_size:
    #     return True
    # else:
    #     return False


def download(download_url, local_dir, undownloaded_list):
    print "#############################################################"
    print "enter download function, begin to deal with %r" % download_url
    if is_already_downloaded(download_url, local_dir):
        print "this build already exists in local dir or is still downloading, pass: %r" % download_url
        return

    try:
        content = urllib.urlopen(download_url)
        if content.getcode() == 404:
            print "file does not exist under this web dir, jump and continue"
            return
    except:
        print "can't open %r, wait for 30s" % download_url
        time.sleep(30)

    filename = download_url.split("/")[-1]
    try:
        begin_time = time.ctime()
        print "%s: begin to download %r" % (begin_time, filename)
        # urllib.urlretrieve(download_url, local_dir + os.sep + filename, url_call_back)
        # no need to callback for now
        urllib.urlretrieve(download_url, local_dir + os.sep + filename)
        print "%s: finish downloading %r" % (time.ctime(), filename)
        print "and the start time is:", begin_time
    except:
        print "exception occured"
    finally:
        target_build_size = get_length_from_server(download_url)
        build_number = "".join(re.findall("\d\.\d{2}\.\d{6}-\d{14}", filename))
        if filename in os.listdir(local_dir):
            build_size = os.path.getsize(local_dir + os.sep + filename)
            print "the build_size is:", build_size
            if build_size < target_build_size:
                if build_size < 5 * 1000:
                    print "build doesn't exist"
                else:
                    print "download error, need to download again."
                    if build_number not in undownloaded_list:
                        print "#######error happened, insert %s to undownloaded_list if it's not in it" % build_number
                        undownloaded_list.insert(0, build_number)
                print "remove the file: %r cause the size is only %r " \
                      "and the real size should be %r" % (local_dir + os.sep + filename, build_size, target_build_size)
                os.remove(local_dir + os.sep + filename)


def update_undownloaded_builds_list(undownloaded_android_list, undownloaded_ios_list, root_dir, root_url, \
                                    branch_name, min_version):
    while True:
        try:
            new_server_android_list, new_server_ios_list = setup.get_server_builds_list(root_url, branch_name)
            break
        except:
            print "connection error, get new_server_list failed, try again later"
            time.sleep(10)

    local_android_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(os.listdir(root_dir + os.sep + branch_name +
                                                                                  os.sep + "tango-android")))
    local_ios_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(os.listdir(root_dir + os.sep + branch_name +
                                                                              os.sep + "tango-ios")))

    local_android_list.sort()
    local_ios_list.sort()


    android_temp = ""
    if len(local_android_list) > 0:
        android_temp = local_android_list[-1]

    for item in new_server_android_list:
        if item >= android_temp:
            undownloaded_android_list.append(item)
            print "server new android version coming:", item
            # append the second newest build version, cause sometimes an newer build comes when the second newest build
            # is still building
            undownloaded_android_list.append(item)
    if len(new_server_android_list) > 4:
        undownloaded_android_list.append(new_server_android_list[-1])
        undownloaded_android_list.append(new_server_android_list[-2])
        undownloaded_android_list.append(new_server_android_list[-3])
        undownloaded_android_list.append(new_server_android_list[-4])
        undownloaded_android_list.append(new_server_android_list[-5])
    else:
        undownloaded_android_list.extend(new_server_android_list)

    undownloaded_android_list = list(set(undownloaded_android_list))
    undownloaded_android_list.sort(reverse=True)

    ios_temp = ""
    if len(local_ios_list) > 0:
        ios_temp = local_ios_list[-1]

    for item in new_server_ios_list:
        if item >= ios_temp:
            undownloaded_ios_list.append(item)
            print "server new ios version coming:", item
            # append the second newest build version, cause sometimes an newer build comes when the second newest build
            # is still building
            undownloaded_ios_list.append(item)
    if len(new_server_ios_list) > 4:
        undownloaded_ios_list.append(new_server_ios_list[-1])
        undownloaded_ios_list.append(new_server_ios_list[-2])
        undownloaded_ios_list.append(new_server_ios_list[-3])
        undownloaded_ios_list.append(new_server_ios_list[-4])
        undownloaded_ios_list.append(new_server_ios_list[-5])
    else:
        undownloaded_ios_list.extend(new_server_ios_list)

    undownloaded_ios_list = list(set(undownloaded_ios_list))
    undownloaded_ios_list.sort(reverse=True)

    for temp in undownloaded_android_list:
        if temp < min_version:
            undownloaded_android_list.remove(temp)

    for temp in undownloaded_ios_list:
        if temp < min_version:
            undownloaded_ios_list.remove(temp)

    return undownloaded_android_list, undownloaded_ios_list


def clean_local_builds(root_dir, multi_branch_name):
    for branch_name in multi_branch_name:
        android_dir = root_dir + os.sep + branch_name + os.sep + "tango-android"
        ios_dir = root_dir + os.sep + branch_name + os.sep + "tango-ios"
        remove_small_builds(android_dir)
        remove_small_builds(ios_dir)


def remove_small_builds(dir):
    for single_build in os.listdir(dir):
        if os.path.getsize(dir + os.sep + single_build) < 1 * 1000:
            print "the build size of %s is %s, delete it" % (single_build, os.path.getsize(dir + os.sep + single_build))
            os.remove(dir + os.sep + single_build)


if __name__ == "__main__":
    # download_url = "http://artifactory.tango.corp/tango/trunk/android/3.14.127535-20150106185602/android-3.14.127535-20150106185602-staging-armv7.apk"
    # local_dir = "D:\download\TangoBuilds\trunk\Android\android-3.14.127535-20150106185602-staging-armv7.apk"
    # is_already_downloaded(download_url, local_dir)
    clean_local_builds("/Volumes/share/TangoBuilds", ["shopseller"])