import argparse

import json
import pickle
import random
import scipy.io
from math import ceil
from pathlib import Path
from collections import defaultdict


from tqdm import tqdm 

def read_ciao(args):
    rating_data = scipy.io.loadmat(args.rdir/'ciao_raw'/'rating.mat')['rating'][:, [0,1,3]]
    social_pairs = scipy.io.loadmat(args.rdir/'ciao_raw'/'trustnetwork.mat')['trustnetwork']

    social_list = defaultdict(list)
    rating_list = defaultdict(list)
    rated_list = defaultdict(list)

    for user_id, item_id, __ in rating_data:
        rating_list[user_id].append(item_id)

    qualify_users = []
    for user_id in tqdm(rating_list, desc='check min_item', ncols=80):
        if len(set(rating_list[user_id])) >= args.min_rating_degree:
            qualify_users.append(user_id)

    for user_a, user_b in tqdm(social_pairs, desc='init social pairs', ncols=80):
        if (user_a != user_b) and user_a in qualify_users and user_b in qualify_users:
            social_list[user_a].append(user_b)
            social_list[user_b].append(user_a)

    social_list = clean_up_social_list(social_list, args.min_user_degree)
    user_set = set(social_list.keys()) ### user_set fix ###
    user_id2uid = {user_id:i for i, user_id in enumerate(user_set)}
    item_id2iid = {}
    def item_get(item_id):
        if item_id not in item_id2iid:
            item_id2iid[item_id] = len(item_id2iid)
        return item_id2iid[item_id]

    social_adj_lists = defaultdict(list)
    for k,v in tqdm(social_list.items(), ncols=80, desc='load social_adj_lists'):
        for x in v:
            social_adj_lists[user_id2uid[k]].append(user_id2uid[x])
    for k in social_adj_lists:
        social_adj_lists[k] = list(set(social_adj_lists[k]))

    # count how many times item is rated
    for user_id, item_id, rating in tqdm(rating_data, ncols=80, desc='process rating.mat'):
        if user_id not in user_id2uid:
            continue
        rated_list[item_id].append(user_id2uid[user_id])

    qualify_items = []
    for item_id in tqdm(rated_list, desc='check min_rated', ncols=80):
        if len(set(rated_list[item_id])) >= args.min_item_degree and random.random()>0.44:
            qualify_items.append(item_id)

    all_ratings = {}
    for user_id, item_id, rating in tqdm(rating_data, ncols=80, desc='process rating.mat'):
        if user_id not in user_id2uid or item_id not in qualify_items:
            continue
        uid = user_id2uid[user_id]
        iid = item_get(item_id)
        all_ratings[(uid, iid)] = rating

    all_ratings = [[k[0], k[1], v] for k,v in all_ratings.items()]
    return all_ratings, user_id2uid, item_id2iid, social_adj_lists
    
def read_epinions(args):
    social_list = defaultdict(list)
    rating_list = defaultdict(list)
    rated_list = defaultdict(list)

    for line in open(args.rdir/'epinions_raw'/'epinions.json', 'r'):
        line = line.split(', \'time\'')[0] + ', \'item\'' + line.split(', \'item\'')[1].split(', \'review\'')[0] + '}' 
        line = line.replace("\'", "\"")
        d = json.loads(line)
        rating_list[d['user']].append(d['item'])

    qualify_users = []
    for user_id in rating_list:
        if len(set(rating_list[user_id])) >= args.min_rating_degree:
            qualify_users.append(user_id)
    qualify_users = set(qualify_users)

    for line in open(args.rdir/'epinions_raw'/'network_trust.txt', 'r'):
        line = line[:-1]
        user_a, user_b = line.split(' trust ')
        if (user_a != user_b) and user_a in qualify_users and user_b in qualify_users:
            social_list[user_a].append(user_b)
            social_list[user_b].append(user_a)

    social_list = clean_up_social_list(social_list, args.min_user_degree)
    user_set = set(social_list.keys()) ### user_set fix ###
    user_id2uid = {user_id:i for i, user_id in enumerate(user_set)}
    item_id2iid = {}
    def item_get(item_id):
        if item_id not in item_id2iid:
            item_id2iid[item_id] = len(item_id2iid)
        return item_id2iid[item_id]

    social_adj_lists = defaultdict(list)
    for k,v in tqdm(social_list.items(), ncols=80, desc='load social_adj_lists'):
        for x in v:
            social_adj_lists[user_id2uid[k]].append(user_id2uid[x])
    for k in social_adj_lists:
        social_adj_lists[k] = list(set(social_adj_lists[k]))

    qualify_items = []

    for line in tqdm(open(args.rdir/'epinions_raw'/'epinions.json', 'r'), ncols=80, desc='process epinions.json'):
        # ['user', 'stars', 'time', 'paid', 'item', 'review'])
        line = line.split(', \'time\'')[0] + ', \'item\'' + line.split(', \'item\'')[1].split(', \'review\'')[0] + '}' 
        line = line.replace("\'", "\"")
        d = json.loads(line)
        user_id, item_id, rating = d['user'], d['item'], int(d['stars'])
        if user_id not in user_id2uid:
            continue
        rated_list[item_id].append(user_id2uid[user_id])

    qualify_items = []
    for item_id in tqdm(rated_list, desc='check min_rated', ncols=80):
        if len(set(rated_list[item_id])) >= args.min_item_degree:
            qualify_items.append(item_id)

    all_ratings = {}
    for line in tqdm(open(args.rdir/'epinions_raw'/'epinions.json', 'r'), ncols=80, desc='process epinions.json'):
        # ['user', 'stars', 'time', 'paid', 'item', 'review'])
        line = line.split(', \'time\'')[0] + ', \'item\'' + line.split(', \'item\'')[1].split(', \'review\'')[0] + '}' 
        line = line.replace("\'", "\"")
        d = json.loads(line)
        user_id, item_id, rating = d['user'], d['item'], int(d['stars'])
        if user_id not in user_id2uid or item_id not in qualify_items:
            continue
        uid = user_id2uid[user_id]
        iid = item_get(item_id)
        all_ratings[(uid, iid)] = rating

    all_ratings = [[k[0], k[1], v] for k,v in all_ratings.items()]
    return all_ratings, user_id2uid, item_id2iid, social_adj_lists

def package_data(args, all_ratings, user_id2uid, item_id2iid, social_adj_lists):
    npart = lambda l,n: ceil(len(l)/10*n)
    traindata = all_ratings[:npart(all_ratings, 6)]
    validdata = all_ratings[npart(all_ratings, 6): npart(all_ratings, 8)]
    testdata = all_ratings[npart(all_ratings, 8):]

    htry_u_lists, htry_ur_lists, htry_v_lists, htry_vr_lists = map(defaultdict, [list]*4)
    for uid, iid, rating in traindata+validdata:
        htry_u_lists[uid].append(iid)
        htry_ur_lists[uid].append(rating)
        htry_v_lists[iid].append(uid)
        htry_vr_lists[iid].append(rating)

    item_adj_lists = defaultdict(list)
    sorted_list = [(k, len(v)) for k, v in htry_v_lists.items()]
    sorted_list.sort(key = lambda x: x[1])
    sorted_list = [x[0] for x in sorted_list]
    traversed = set()
    for iid in tqdm(sorted_list, ncols=80, desc='building item adj'):
        traversed |= set([iid])
        two_hops = set()
        for uid in htry_v_lists[iid]:
            two_hops |= set(htry_u_lists[uid])
        for nid in two_hops:
            if nid in traversed or nid == iid:
                continue
            if len(set(htry_v_lists[iid]) & set(htry_v_lists[nid]))/len(set(htry_v_lists[iid]) | set(htry_v_lists[nid])) > 0.5:
                    item_adj_lists[iid].append(nid)
                    item_adj_lists[nid].append(iid)

    assert set(user_id2uid.values()) == set(range(len(user_id2uid)))
    assert set(item_id2iid.values()) == set(range(len(item_id2iid)))

    # 
    user_degrees = [len(social_adj_lists[u]) for u in range(len(user_id2uid))]
    high_degree_u_list = [i for i, d in enumerate(user_degrees) if d > args.max_social_degree]
    for i, u in enumerate(high_degree_u_list):
        for v in high_degree_u_list[i:]:
            if random.random()> 0.3 and len(social_adj_lists[u]) > args.max_social_degree and len(social_adj_lists[v])> args.max_social_degree and v in social_adj_lists[u]:
                social_adj_lists[u].remove(v)
                social_adj_lists[v].remove(u)

    pickle.dump([htry_u_lists, htry_ur_lists, htry_v_lists, htry_vr_lists, traindata, validdata, testdata, social_adj_lists, item_adj_lists, user_id2uid, item_id2iid], open(args.rdir/(args.dset+'.pkl'), 'wb'))

def clean_up_social_list(social_list, min_degree):
    prev_num = len(social_list)
    finished = False
    for I in tqdm(range(15), desc='clean_up_social_list', ncols=80):
        removers = []
        for user_id in social_list:
            if len(social_list[user_id]) < min_degree:
                for nid in social_list[user_id]:
                    social_list[nid].remove(user_id)
                removers.append(user_id)
        for user_id in removers:
            del social_list[user_id]
        if prev_num == len(social_list):
            finished = True
            break
        prev_num = len(social_list)
    if not finished:
        print('clean_up_social_list not finished')
    return social_list

def main():
    random.seed(0)
    parser = argparse.ArgumentParser(description='build ciao dataset')
    parser.add_argument('--dset', type=str)
    parser.add_argument('--rdir', type=str, default=Path('cache/'))
    parser.add_argument('--min_user_degree', type=int, default=15)
    parser.add_argument('--min_rating_degree', type=int, default=1)
    parser.add_argument('--min_item_degree', type=int, default=5)
    parser.add_argument('--max_social_degree', type=int, default=50)
    args = parser.parse_args()

    print(' >>> build {} dataset'.format(args.dset))
    if args.dset == 'ciao':
        all_ratings, user_id2uid, item_id2iid, social_adj_lists = read_ciao(args)
    elif args.dset == 'epinions':
        args.min_item_degree = 1
        all_ratings, user_id2uid, item_id2iid, social_adj_lists = read_epinions(args)
    elif args.dset == 'library':
        all_ratings, user_id2uid, item_id2iid, social_adj_lists = read_library(args)
    else:
        errmsg = "[args.dset not set]" if args.dset is None else args.dset+ " not recognized"
        raise Exception(errmsg)

    package_data(args, all_ratings, user_id2uid, item_id2iid, social_adj_lists)


if __name__ == '__main__':
    main()
