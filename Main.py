# -*- coding: utf-8 -*-

__author__ = ' Harold (Finch) '

import numpy as np
import sklearn
import re
import math
import pickle
import os

import zhihu_login


# Hyperparameter

NUM_NEIGHBORS = 5 # How many neighbors you want to search ?
CENTER_ID = 'yue-yangming'
SELECTED_NEIGHBORS_NUM = 20
SELECTED_TOPICS_NUM = 20


# Initialize
PEOPLE_URL = 'https://www.zhihu.com/people/'
CENTER_URL = PEOPLE_URL + CENTER_ID
TOPIC_COUNTER = {}
NEIGHBOR_COUNTER = {}
TOPICS = []
NEIGHBORS = []

# Stimulated log in.
try:
    SESSION = zhihu_login.main()
except:
    'Log in failed, please try again.'

agent = zhihu_login.agent
headers = zhihu_login.headers

# Prepare data
def open_url(url):
    # input : url, output : content of url
    try:

        result = SESSION.get(url, headers=headers)
        return result.text

    except:

        print('Error in open_url part')

def Get_num(User_url,choice):

    # Get number of followers or following.
    # choice == 0, get followers num, else get following num

    if choice == 0:
        Follower_url = User_url + '/followers'
        Re_followers_num = re.compile(r'关注者</div><div class="NumberBoard-value">\d*')  # Regular experssion.
    elif choice == 1:
        Follower_url = User_url + '/following'
        Re_followers_num = re.compile(r'关注了</div><div class="NumberBoard-value">\d*')  # Regular experssion.
    elif choice == 2:
        Follower_url = User_url + '/following/topics'
        Re_followers_num = re.compile(r'关注的话题</span><span class="Profile-lightItemValue">\d*')
    temp_re = re.compile('\d{1,4}')

    main_data = open_url(Follower_url)
    # main_data = main_data.decode('utf-8')  # Decode for further process.

    temp = Re_followers_num.findall(main_data)
    result = temp_re.findall(temp[0])

    return int(result[0])

def Get_People_list(User_url,choice,report = 0):

    # Get follower or following list, choice == 0 : Follower
    # choice == 1 : following list

    # Use re to get a list of followers' personal page.

    num_follow = Get_num(User_url,choice)

    num_pages = math.floor(num_follow / 20) + 1
    results = []
    stop_flag = False
    target_string = '&quot;' + CENTER_ID + '&quot;,'
    target_string_2 = '&quot;' + CENTER_ID + '&quot;]'

    if choice == 0:
        page_string = '/followers?'
        output_string = 'Followers Got'
        RE_temp = re.compile(r'followersByUser.*totals&quot;:\d{1,6}}}')
    elif choice == 1:
        page_string = '/following?'
        output_string = 'Following list Got'
        RE_temp = re.compile(r'followingByUser.*totals&quot;:\d{1,6}}}')

    RE_new = re.compile(r'&quot;[a-zA-Z0-9-]*&quot;[,\]]')

    for i in range(num_pages):
        try:
            if choice == 1 and i > 0:
                if target_string in results_temp or target_string_2 in results_temp: # If target already in previous page
                    stop_flag = True

            page_index = i + 1
            page_url = User_url + page_string + 'page={}'.format(page_index)
            page_data = open_url(page_url)
            results_temp = RE_temp.findall(page_data)
            string_temp = results_temp[0]
            results_temp = RE_new.findall(string_temp)
            for each in results_temp:
                temp = each[6:-7]  # Get followers' url
                results.append(temp)
            if stop_flag:
                break
        except:
            print('Error in Get people list')
            print('User url : {}'.format(User_url))
            print('choice : {}'.format(choice))
            print('page_index : {}'.format(page_index))

    if report:
        print(output_string)

    return results


def Get_main_user_neighbor(User_url):
    # Analyse followers' following page to analyze which one is followed at nearly same time.

    Following_list = Get_People_list(User_url,1)
    target_index = Following_list.index(CENTER_ID)
    low_boundry = max(0, target_index - NUM_NEIGHBORS)
    high_boundry = min(len(Following_list), target_index + NUM_NEIGHBORS + 1)

    neighbors_list = Following_list[low_boundry: high_boundry]

    return neighbors_list

def Get_topic(User_url):

    # Input : User_url, output : topics list

    topics = set()
    num_topic = Get_num(User_url,2)
    num_pages = math.floor(num_topic / 20) + 1

    User_url = User_url + '/following/topics?'

    for i in range(num_pages):

        page_index = i + 1
        page_url = User_url + 'page={}'.format(page_index)
        page_data = open_url(page_url)
        # page_data = page_data.decode('utf-8')

        RE_topic = re.compile(r':&quot;[^&]*&quot;,&quot;introduction') # RE, contain string that don't have '&'
        results_temp = RE_topic.findall(page_data)
        for each in results_temp:
            temp = each[7:-25]  # Get followers' url
            topics.add(temp)

    # RE_topic = re.compile(r':&quot;[\u4e00-\u9fa5]*&quot;,&quot;introduction')
    topics_list = list(topics)

    return topics_list

# def Get_data(followers_list):
#
#     followers_neighbors = []
#     followers_topics = []
#
#     for follower in followers_list:
#
#         neighbor = Get_main_user_neighbor(PEOPLE_URL + follower)
#         followers_neighbors.append(neighbor)
#         for each in neighbor:
#             if each in NEIGHBORS:
#                 NEIGHBOR_COUNTER[each] += 1
#             else:
#                 if each != CENTER_ID:
#                     NEIGHBORS.append(each)
#                     NEIGHBOR_COUNTER[each] = 1
#
#         topic = Get_topic(PEOPLE_URL + follower)
#         followers_topics.append(topic)
#         for each in topic:
#             if each in TOPICS:
#                 TOPIC_COUNTER[each] += 1
#             else:
#                 TOPICS.append(each)
#                 TOPIC_COUNTER[each] = 1
#
#     # Save these variables into file.
#     # pickle.dump(followers_list, open('followers_list.txt', 'wb'))
#     pickle.dump(followers_neighbors, open('followers_neighbors.txt', 'wb'))
#     pickle.dump(followers_topics,open('followers_topics.txt', 'wb'))
#     pickle.dump(NEIGHBOR_COUNTER,open('NEIGHBOR_COUNTER.txt', 'wb'))
#     pickle.dump(NEIGHBORS,open('NEIGHBOR.txt', 'wb'))
#     pickle.dump(TOPICS,open('TOPICS.txt', 'wb'))
#     pickle.dump(TOPIC_COUNTER,open('TOPIC_COUNTER.txt', 'wb'))

def Sort_dict(Dict,k):
    #  Returns k largest numbers.
    items = Dict.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=True)
    temp = backitems[:k+1]
    temp = [v[1] for v in temp] # Only return a list of keys.
    return temp


if __name__ == '__main__':

    if os.path.isfile('followers_list.txt'):
        followers_list = pickle.load(open('followers_list.txt', 'rb'))
    else:
        followers_list = Get_People_list(CENTER_URL, 0, 1)
    if os.path.isfile('followers_topics.txt'):  # If file already exists, load else Get data.
        pickle.dump(followers_list, open('followers_list.txt', 'rb'))
        followers_neighbors = pickle.load(open('followers_neighbors.txt', 'rb'))
        followers_topics = pickle.load(open('followers_topics.txt', 'rb'))
        NEIGHBOR_COUNTER = pickle.load(open('NEIGHBOR_COUNTER.txt', 'rb'))
        NEIGHBORS = pickle.load(open('NEIGHBOR.txt', 'rb'))
        TOPICS = pickle.load(open('TOPICS.txt', 'rb'))
        TOPIC_COUNTER = pickle.load(open('TOPIC_COUNTER.txt', 'rb'))
    else:
        # Get_data(followers_list)
        followers_neighbors = []
        followers_topics = []
        reporter = 0
        for follower in followers_list:
            print(reporter)
            reporter += 1
            neighbor = Get_main_user_neighbor(PEOPLE_URL + follower)
            followers_neighbors.append(neighbor)
            for each in neighbor:
                if each in NEIGHBORS:
                    NEIGHBOR_COUNTER[each] += 1
                else:
                    if each != CENTER_ID:
                        NEIGHBORS.append(each)
                        NEIGHBOR_COUNTER[each] = 1

            topic = Get_topic(PEOPLE_URL + follower)
            followers_topics.append(topic)
            for each in topic:
                if each in TOPICS:
                    TOPIC_COUNTER[each] += 1
                else:
                    TOPICS.append(each)
                    TOPIC_COUNTER[each] = 1

        # Save these variables into file.
        pickle.dump(followers_list, open('followers_list.txt', 'wb'))
        pickle.dump(followers_neighbors, open('followers_neighbors.txt', 'wb'))
        pickle.dump(followers_topics, open('followers_topics.txt', 'wb'))
        pickle.dump(NEIGHBOR_COUNTER, open('NEIGHBOR_COUNTER.txt', 'wb'))
        pickle.dump(NEIGHBORS, open('NEIGHBOR.txt', 'wb'))
        pickle.dump(TOPICS, open('TOPICS.txt', 'wb'))
        pickle.dump(TOPIC_COUNTER, open('TOPIC_COUNTER.txt', 'wb'))

    # Data process and machine learning part.
    temp = Sort_dict(NEIGHBOR_COUNTER, SELECTED_NEIGHBORS_NUM + 1)
    sorted_NEIGHBOR_COUNTER = temp[1:]  # Because CENTER_ID is the first one in this dict.
    temp_2 = Sort_dict(TOPIC_COUNTER, SELECTED_TOPICS_NUM)
    sorted_TOPIC_COUNTER = temp_2[1:]

    followers_matrix = np.zeros(shape=[len(followers_list), SELECTED_NEIGHBORS_NUM + SELECTED_TOPICS_NUM])
    for idx, follower in enumerate(followers_list[0:100]):
        for idx_neighbor, neighbor in enumerate(sorted_NEIGHBOR_COUNTER):
            followers_matrix[idx, idx_neighbor] = int( neighbor in followers_neighbors[idx])
        for idx_topic, topic in enumerate(sorted_TOPIC_COUNTER):
            followers_matrix[idx, SELECTED_NEIGHBORS_NUM + idx_topic] = int(topic in followers_topics[idx])


    # idx, val in enumerate(ints):

    # Sort dict:






