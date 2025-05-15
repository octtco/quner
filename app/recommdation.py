import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '去哪儿旅游数据分析推荐系统.settings')
django.setup()
from app.models import TravelInfo, UserRating
from collections import defaultdict


# user_ratings = {
#     "Edward": {"南山文化旅游区": 5},
#     "EdwardD": {"南山文化旅游区": 5, "三亚蜈支洲岛旅游区": 2},
#     "newEdward"
# }

def getOldUser_ratings():
    olduser_ratings = {}
    for travel in TravelInfo.objects.all():
        try:
            comments = json.loads(travel.comments)
        except json.JSONDecodeError:
            continue  # 跳过无效的JSON数据

        for com in comments:
            # 检查必要的字段是否存在
            if 'author' not in com or 'score' not in com:
                continue  # 跳过缺少关键字段的评论

            author = com['author']
            travel_title = travel.title
            score = com['score']

            # 初始化用户评分字典
            if author not in olduser_ratings:
                olduser_ratings[author] = {travel_title: score}
            else:
                olduser_ratings[author][travel_title] = score

    return olduser_ratings

def getUser_ratings():
    user_ratings = {}
    for rate in UserRating.objects.all():
        travelTitle = rate.TravelSpot.title
        try:
            userid = rate.user_id
        except:
            continue
        if user_ratings.get(userid, -1) == -1:
            user_ratings[userid] = {travelTitle: rate.rate}
        else:
            user_ratings[userid][travelTitle] = rate.rate
    return user_ratings

def build_hybrid_user_ratings(user_ratings, olduser_ratings, w1=0.7, w2=0.3):
    hybrid_ratings = {}
    # 处理高权重数据（user_ratings）
    for user, ratings in user_ratings.items():
        hybrid_ratings[user] = {item: score * w1 for item, score in ratings.items()}
    # 处理低权重数据（olduser_ratings）
    for user, ratings in olduser_ratings.items():
        for item, score in ratings.items():
            if user in hybrid_ratings:
                hybrid_ratings[user][item] = hybrid_ratings[user].get(item, 0) + score * w2
            else:
                hybrid_ratings[user] = {item: score * w2}
    return hybrid_ratings


def compute_user_similarity(hybrid_ratings):
    # 获取所有景点
    all_items = set()
    for ratings in hybrid_ratings.values():
        all_items.update(ratings.keys())
    all_items = list(all_items)

    # 构建用户-景点矩阵
    user_matrix = []
    for user, ratings in hybrid_ratings.items():
        row = [ratings.get(item, 0) for item in all_items]
        user_matrix.append(row)

    # 计算用户余弦相似度
    user_sim = cosine_similarity(user_matrix)
    return {user: sim for user, sim in zip(hybrid_ratings.keys(), user_sim)}


def hybrid_user_recommendation(target_user, hybrid_ratings, user_sim, top_n=5):
    # 获取目标用户的评分和相似用户
    target_ratings = hybrid_ratings.get(target_user, {})
    sim_users = user_sim[target_user]
    # 按相似度排序其他用户
    sorted_users = sorted(
        zip(hybrid_ratings.keys(), sim_users),
        key=lambda x: x[1],
        reverse=True
    )
    # 收集候选景点评分
    candidate_scores = defaultdict(float)
    for other_user, sim in sorted_users:
        if other_user == target_user:
            continue
        for item, score in hybrid_ratings[other_user].items():
            if item not in target_ratings:
                candidate_scores[item] += sim * score

    # 返回Top-N推荐
    sorted_items = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    return [item for item, _ in sorted_items[:top_n]]

# def user_bases_collaborative_filtering(user_id, user_ratings, top_n=3):
#     # 获取目标用户的评分数据
#     target_user_ratings = user_ratings[user_id]
#     # print(target_user_ratings)
#     # 初始化一个字段，用于保存其他用户与目标用户的相似度得分
#     user_similarity_scores = {}
#
#     # 将目标用户的评分转化为numpy数组
#     target_user_ratings_list = np.array([
#         rating for _, rating in target_user_ratings.items()
#     ])
#
#     # print(target_user_ratings_list)
#     # 计算目标用户与其他用户之间的相似度得分
#     for user, ratings in user_ratings.items():
#         if user == user_id:
#             continue
#         # 将其他用户的评分转化为numpy数组
#         user_ratings_list = np.array([ratings.get(item, 0) for item in target_user_ratings])
#         print(user_ratings_list)
#         # 计算余弦相似度
#         similarity_score = cosine_similarity([user_ratings_list], [target_user_ratings_list])[0][0]
#         user_similarity_scores[user] = similarity_score
#
#     # 对用户相似度得分进行降序排序
#     sorted_similar_user = sorted(user_similarity_scores.items(), key=lambda x: x[1], reverse=True)
#     # print(sorted_similar_user)
#
#     # 选择 TOP N 个相似用户喜欢的景点 作为推荐结果
#     recommended_items = set()
#     for similar_user, _ in sorted_similar_user[:top_n]:
#         recommended_items.update(user_ratings[similar_user].keys())
#
#     # print(recommended_items)
#     # 过滤掉目标用户已经评分过的景点
#     # recommended_items = [item for item in recommended_items if item not in target_user_ratings]
#
#
#     return recommended_items


if __name__ == '__main__':
    user_id = 1
    user_ratings = getUser_ratings()
    recommended_items = user_bases_collaborative_filtering(user_id, user_ratings)
