# -*- coding: utf-8 -*-
import os
import threading
import time

import multi_thread


__author__ = 'haokai'

import setup
import download


def android_combine_url(root_url, branch_name, build_dir_name, android_build_suffix):
    results = []
    single_result_url = root_url + "/" + branch_name + "/tango-android/" + build_dir_name + "/"
    android_build_name = []
    for item in android_build_suffix:
        android_build_name.append("tango-android-" + build_dir_name + "-" + item)
    for item2 in android_build_name:
        results.append(single_result_url + item2)

    return results


def ios_combine_url(root_url, branch_name, build_dir_name, ios_build_suffix):
    results = []
    single_result_url = root_url + "/" + branch_name + "/tango-ios/" + build_dir_name + "/"
    ios_build_name = []
    for item in ios_build_suffix:
        ios_build_name.append("tango-ios-" + build_dir_name + "-" + item)
    for item2 in ios_build_name:
        results.append(single_result_url + item2)

    return results


def android_combine_dir(root_dir, branch_name):
    # D:\download\TangoBuilds\grenache\Android\android-3.14.129432-20150117223801-staging-armv7.apk
    dir = root_dir + os.sep + branch_name + os.sep + "tango-android"
    return dir


def ios_combine_dir(root_dir, branch_name):
    # D:\download\TangoBuilds\grenache\Android\android-3.14.129432-20150117223801-staging-armv7.apk
    dir = root_dir + os.sep + branch_name + os.sep + "tango-ios"
    return dir


if __name__ == "__main__":
    # the first branch in the list is in high priority when uploading to sharecn
    multi_branch_name = ["trunk", "muscadelle"]
    # assign min_version to empty string means no limit, the format is like: 3.14.126900-20141223221200
    # multi_min_version = ["3.14.132366", "3.15.132300"]
    multi_min_version = ["3.20.176900", "3.20.176900"]
    android_build_suffix = ["staging-ui-api14-release-armv7.apk", "t2dev-ui-api14-release-armv7.apk",
                            "production-ui-api14-release-armv7.apk"]
    ios_build_suffix = ["tango_t2dev_inhouse_tango3dev_release-fat.ipa", "tango_t2dev_inhouse_tango3dev_dsym_release-fat.zip",
                        "tango_staging_inhouse_tango3dev_release-fat.ipa", "tango_staging_inhouse_tango3dev_dsym_release-fat.zip",
                        "tango_production_inhouse_tango3dev_release-fat.ipa", "tango_production_inhouse_tango3dev_dsym_release-fat.zip"]
    root_dir = "/shared2T/TangoBuilds"
    root_url = "http://artifactory.tango.corp/tango"
    max_download_threads = 5

    mt = multi_thread.MultiThreadDownloading(max_download_threads)

    multi_undownloaded_android_list = []
    multi_undownloaded_ios_list = []
    for index in range(len(multi_branch_name)):
        branch_name = multi_branch_name[index]
        min_version = multi_min_version[index]
        print "begin to prepare_local_dir for %r" % branch_name
        setup.prepare_local_dir(root_dir, branch_name)

        # undownloaded_android_list and undownloaded_ios_list have been sorted from big to small
        undownloaded_android_list, undownloaded_ios_list = \
            setup.get_undownloaded_builds_list(root_dir, root_url, branch_name,
                                               android_build_suffix,
                                               ios_build_suffix, min_version)
        multi_undownloaded_android_list.append(undownloaded_android_list)
        multi_undownloaded_ios_list.append(undownloaded_ios_list)

    # store download urls for a specified version
    android_download_urls = []
    ios_download_urls = []

    while True:
        download.clean_local_builds(root_dir, multi_branch_name)

        for index in range(len(multi_branch_name)):
            branch_name = multi_branch_name[index]
            undownloaded_android_list = multi_undownloaded_android_list[index]
            undownloaded_ios_list = multi_undownloaded_ios_list[index]
            print "!!!android", branch_name, ": ", undownloaded_android_list
            print "!!!ios", branch_name, ": ", undownloaded_ios_list
            min_version = multi_min_version[index]

            print "\nround begin: %r\n" % branch_name
            print "undownloaded_android_list length is:", len(undownloaded_android_list)
            print "undownloaded_ios_list length is:", len(undownloaded_ios_list)

            for i in range(8):
                if len(undownloaded_android_list) != 0:
                    print "android round downloading"
                    android_download_urls = android_combine_url(root_url, branch_name,
                                                                undownloaded_android_list[0],
                                                                android_build_suffix)
                    print "delete the first item in undownloaded_android_list:", \
                        undownloaded_android_list[0]
                    del undownloaded_android_list[0]
                    # print "the urls are:", android_download_urls
                    for android_download_url in android_download_urls:
                        mt.add_job(download.download, android_download_url,
                                   android_combine_dir(root_dir, branch_name),
                                   undownloaded_android_list)

                if len(undownloaded_ios_list) != 0:
                    print "ios round downloading"
                    ios_download_urls = ios_combine_url(root_url, branch_name,
                                                        undownloaded_ios_list[0],
                                                        ios_build_suffix)
                    print "delete the first item in undownloaded_ios_list: ", \
                        undownloaded_ios_list[0]
                    del undownloaded_ios_list[0]
                    # print "the urls are:", ios_download_urls
                    for ios_download_url in ios_download_urls:
                        mt.add_job(download.download, ios_download_url,
                                   ios_combine_dir(root_dir, branch_name),
                                   undownloaded_ios_list)

            if True:
                time.sleep(5)
                print "\n####################begin to sleep: %r##########################" % time.ctime()
                print "%s: active downloading thread num is: %d" % (time.ctime(), threading.activeCount() - 1)
                if threading.activeCount() - 1 >= max_download_threads - 1:
                    time.sleep(30)
                time.sleep(45)

                undownloaded_android_list, undownloaded_ios_list = download.update_undownloaded_builds_list(
                    undownloaded_android_list, undownloaded_ios_list, root_dir, root_url,
                    branch_name, min_version)
                multi_undownloaded_android_list[index] = undownloaded_android_list
                multi_undownloaded_ios_list[index] = undownloaded_ios_list
                print "after refresh, the length of undownloaded_android_list is:", len(
                    undownloaded_android_list)
                print "after refresh, the length of undownloaded_ios_list is:", len(
                    undownloaded_ios_list)









