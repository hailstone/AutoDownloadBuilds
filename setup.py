# -*- coding: utf-8 -*-
import os
import re
import time
import urllib
import download

__author__ = 'haokai'


def prepare_local_dir(root_dir, branch_name):
    if not os.path.exists(root_dir + os.sep + branch_name):
        print "%s: folder %r does not exist under %r" % (time.ctime(), branch_name, root_dir)
        os.mkdir(root_dir + os.sep + branch_name)
        print "%s: folder %r created under %r" % (time.ctime(), branch_name, root_dir)

    branch_dir = root_dir + os.sep + branch_name

    android_folder_name = "tango-android"
    android_dir = branch_dir + os.sep + android_folder_name
    if not os.path.exists(branch_dir + os.sep + android_folder_name):
        print "%s: folder %r does no exist under %r" % (time.ctime(), android_folder_name, branch_dir)
        os.mkdir(branch_dir + os.sep + android_folder_name)
        print "%s: folder %r created under %r" % (time.ctime(), android_folder_name, branch_dir)

    ios_folder_name = "tango-ios"
    ios_dir = branch_dir + os.sep + ios_folder_name
    if not os.path.exists(branch_dir + os.sep + ios_folder_name):
        print "%s: folder %r does no exist under %r" % (time.ctime(), ios_folder_name, branch_dir)
        os.mkdir(branch_dir + os.sep + ios_folder_name)
        print "%s: folder %r created under %r" % (time.ctime(), ios_folder_name, branch_dir)

    return android_dir, ios_dir


def get_server_builds_list(root_url, branch_name):
    url = root_url + "/" + branch_name
    print "begin to get server builds list from %r" % url

    server_android_list = []
    print "try to open " + url + "/" + "tango-android/"
    page = urllib.urlopen(url + "/" + "tango-android/")
    if page.getcode() != 200:
        print "server code is not 200, server error!"
        print "the url is:", url
        print "return empty list as default and will try again next round."
        time.sleep(10)
        return [], []

    content = page.read()
    result_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", content)
    server_android_list = list(set(result_list))
    server_android_list.sort()
    # print server_android_list
    print "The length of server_android_list is:", len(server_android_list)

    server_ios_list = []
    page = urllib.urlopen(url + "/" + "tango-ios/")
    if page.getcode() != 200:
        print "server code is not 200, server error!"
        print "the url is:", url
        print "return empty list as default and will try again next round."
        time.sleep(10)
        return 1

    content = page.read()
    result_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", content)
    server_ios_list = list(set(result_list))
    server_ios_list.sort()
    # print server_ios_list
    print "The length of server_ios_list is:", len(server_ios_list)

    return server_android_list, server_ios_list


def get_local_builds_list(root_dir, branch_name, android_build_suffix, ios_build_suffix):
    dir = root_dir + os.sep + branch_name

    android_dir = dir + os.sep + "tango-android"
    print "local android dir is:", android_dir
    local_android_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(os.listdir(android_dir)))
    local_android_list = list(set(local_android_list))
    for suffix in android_build_suffix:
        temp_list_with_suffix = re.findall("\d\.\d{2}\.\d{6}-\d{14}" + "-" + suffix, "".join(os.listdir(
            android_dir)))
        temp_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(temp_list_with_suffix))
        local_android_list = [i for i in local_android_list if i in temp_list]
    print "The length of local_android_list is:", len(local_android_list)

    ios_dir = dir + os.sep + "tango-ios"
    print "local ios dir is:", ios_dir
    local_ios_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(os.listdir(ios_dir)))
    local_ios_list = list(set(local_ios_list))
    for suffix in ios_build_suffix:
        temp_list_with_suffix = re.findall("\d\.\d{2}\.\d{6}-\d{14}" + "-" + suffix, "".join(os.listdir(
            ios_dir)))
        temp_list = re.findall("\d\.\d{2}\.\d{6}-\d{14}", "".join(temp_list_with_suffix))
        local_ios_list = [i for i in local_ios_list if i in temp_list]
    print "The length of local_ios_list is:", len(local_ios_list)

    return local_android_list, local_ios_list


def clean_local_broken_builds(root_dir, root_url, branch_name, android_build_suffix, ios_build_suffix):
    # the unit is Byte
    offset_to_normal_size = 40 * 1000 * 1000
    dir = root_dir + os.sep + branch_name

    print "begin to clean the dir, remove wrong size builds under %r" % dir

    android_dir = dir + os.sep + "tango-android"
    for suffix in android_build_suffix:
        # key: build name  value: build size
        build_dic = {}
        build_names = re.findall("tango-android-" + "\d\.\d{2}\.\d{6}-\d{14}" + "-" + suffix, "".join(os.listdir(
            android_dir)))
        for build_name in build_names:
            build_dic[build_name] = os.path.getsize(android_dir + os.sep + build_name)
        # print build_dic
        sum = 0
        for size in build_dic.values():
            sum += size
        if len(build_dic) != 0:
            avg = sum / len(build_dic)
        if 0 < len(build_dic) < 4:
            android_offset_to_normal_size = offset_to_normal_size / len(build_dic)
        elif len(build_dic) >= 4:
            android_offset_to_normal_size = offset_to_normal_size / 4
        for build_name in build_names:
            if avg - build_dic[build_name] > android_offset_to_normal_size:
                build_dir = re.findall("\d\.\d{2}\.\d{6}-\d{14}", build_name)[0]
                download_url = root_url + "/" + branch_name + "/" + "tango-android" + "/" + build_dir + "/" + build_name
                server_build_size = download.get_length_from_server(download_url)
                if server_build_size == 0:
                    continue
                local_build_sie = os.path.getsize(android_dir + os.sep + build_name)

                if server_build_size != local_build_sie:
                    os.remove(android_dir + os.sep + build_name)
                    print "%r is removed from %r cause the size is not correct" % (build_name, android_dir)
                    print "local size is %r, server size is %r" % (local_build_sie, server_build_size)

    ios_dir = dir + os.sep + "tango-ios"
    for suffix in ios_build_suffix:
        # key: build name  value: build size
        build_dic = {}
        build_names = re.findall("tango-ios-" + "\d\.\d{2}\.\d{6}-\d{14}" + "-" + suffix, "".join(os.listdir(
            ios_dir)))
        for build_name in build_names:
            build_dic[build_name] = os.path.getsize(ios_dir + os.sep + build_name)
        # print build_dic
        sum = 0
        for size in build_dic.values():
            sum += size
        if len(build_dic) != 0:
            avg = sum / len(build_dic)
        if 0 < len(build_dic) < 10:
            ios_offset_to_normal_size = offset_to_normal_size / len(build_dic)
        elif len(build_dic) >= 10:
            ios_offset_to_normal_size = offset_to_normal_size / 10
        for build_name in build_names:
            if avg - build_dic[build_name] > ios_offset_to_normal_size:
                build_dir = re.findall("\d\.\d{2}\.\d{6}-\d{14}", build_name)[0]
                download_url = root_url + "/" + branch_name + "/" + "tango-ios" + "/" + build_dir + "/" + build_name
                # get an error if try to connect server too frequent
                time.sleep(2)
                server_build_size = download.get_length_from_server(download_url)
                if server_build_size == 0:
                    continue
                local_build_sie = os.path.getsize(ios_dir + os.sep + build_name)

                if server_build_size != local_build_sie:
                    os.remove(ios_dir + os.sep + build_name)
                    print "%r is removed from %r cause the size is not correct" % (build_name, ios_dir)
                    print "local size is %r, server size is %r" % (local_build_sie, server_build_size)

    print "done clearing the dir"


def get_undownloaded_builds_list(root_dir, root_url, branch_name, android_build_suffix, ios_build_suffix,
                                 min_version):
    if len(min_version) == 0:
        min_version = "0"
    server_android_list = []
    server_ios_list = []
    server_android_list, server_ios_list = get_server_builds_list(root_url, branch_name)
    local_android_list = []
    local_ios_list = []
    # clean_local_broken_builds(root_dir, root_url, branch_name, android_build_suffix, ios_build_suffix)
    local_android_list, local_ios_list = get_local_builds_list(root_dir, branch_name,
                                                                  android_build_suffix,
                                                                  ios_build_suffix)

    undownloaded_android_list = [i for i in server_android_list if i not in local_android_list and i >= min_version]
    undownloaded_ios_list = [i for i in server_ios_list if i not in local_ios_list and i >= min_version]
    # sort from small to big
    # format: 3.14.129817-20150120171137
    undownloaded_android_list.sort(reverse=True)
    undownloaded_ios_list.sort(reverse=True)
    print "The length of undownloaded_android_list is:", len(undownloaded_android_list)
    print "The length of undownloaded_ios_list is:", len(undownloaded_ios_list)

    return undownloaded_android_list, undownloaded_ios_list


if __name__ == "__main__":
    get_local_builds_list("D:\download\TangoBuilds", "shoptab", ["staging-release.apk", ],
                          ["staging_inhouse_tango3dev-release.ipa",
                           "staging_inhouse_tango3dev_dsym-release.zip"])
    clean_local_broken_builds("D:\download\TangoBuilds", "shoptab", ["staging-release.apk", ],
                              ["staging_inhouse_tango3dev-release.ipa",
                               "staging_inhouse_tango3dev_dsym-release.zip"])


