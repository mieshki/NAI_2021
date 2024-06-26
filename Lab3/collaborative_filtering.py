"""
Movie recommendation
Authors:
Reiter, Aleksander <https://github.com/block439>
Dziadowiec, Mieszko <https://github.com/mieshki>
How to run:
(optional): `pip install -r requirements.txt`
`collaborative_filtering.py` --user <user_fullName>
"""
import argparse
import json
import numpy as np

from compute_scores import euclidean_score


def build_arg_parser():
    """
    Function parses arguments from cmd
    :return: parser object
    """
    parser = argparse.ArgumentParser(description='Find users who are similar to the input user')
    parser.add_argument('--user', dest='user', required=True,
                        help='Input user')
    return parser


# Finds users in the dataset that are similar to the input user
def find_similar_users(dataset, user, num_users):
    """
    Function returns list of similar users to input user. Similarity is based on movies rates.
    :param dataset: Raw dataset with movies, rates and users
    :param user: The user we are looking for a similarity to
    :param num_users: How many similar users return
    :return: List with similar users to input user
    """
    if user not in dataset:
        raise TypeError('Cannot find ' + user + ' in the dataset')

    # Compute Pearson score between input user 
    # and all the users in the dataset
    scores = np.array([[x, euclidean_score(dataset, user,
                                           x)] for x in dataset if x != user])

    # Sort the scores in decreasing order
    scores_sorted = np.argsort(scores[:, 1])[::-1]

    # Extract the top 'num_users' scores
    top_users = scores_sorted[:num_users]

    return scores[top_users]


def predict_movie_rate(similar_users, dataset):
    """
    Function predicts movie rate basing on similar users ratings.
    :param similar_users: List with similar users
    :param dataset: Raw dataset with movies, rates and users
    :return: List of movies with predicted rate
    """
    similar_ratings = {}
    prediction_movies = {}

    weight = 0
    for person in similar_users:
        weight = float(person[1])
        for movie in dataset[person[0]]:
            rate = dataset[person[0]][movie]
            if movie in similar_ratings.keys():
                _rate, _weight, _counter = similar_ratings[movie]
                _rate += rate * weight
                _weight += weight
                _counter += 1
                similar_ratings[movie] = _rate, _weight, _counter
            else:
                similar_ratings[movie] = rate * weight, weight, 1

    for movie in similar_ratings:
        _rate, _weight, _counter = similar_ratings[movie]
        if _counter != 1:
            prediction_movies[movie] = _rate / _weight

    return prediction_movies


def recommended_movie(_user, dataset, movies, number, sign="can"):
    """
    Function prints recommended movies
    :param _user: User to whom we recommend videos
    :param dataset: Raw dataset with movies, rates and users
    :param movies: Dataset with movies and predictions.
    :param number: Int value how many recommendation print
    :param sign: String value, it tells you whether to recommend or not.
    """
    for movie in movies:
        if movie not in dataset[_user] and number > 0:
            number -= 1
            print(f"This movie {sign} intrest you {movie}, our rate: {movies[movie]}")


if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    user = args.user

    ratings_file = 'history.json'

    with open(ratings_file, 'r') as f:
        data = json.loads(f.read())

    print('\nUsers similar to ' + user + ':\n')
    similar_users = find_similar_users(data, user, 10)

    print('User\t\t\tSimilarity score')
    print('-' * 41)
    for item in similar_users:
        print(item[0], '\t\t', round(float(item[1]), 2))

    print('-' * 41)
    unsorted_movies = predict_movie_rate(similar_users, data)
    sorted_desc_movies = {k: v for k, v in sorted(unsorted_movies.items(), key=lambda item: item[1], reverse=True)}
    sorted_asc_movies = {k: v for k, v in sorted(unsorted_movies.items(), key=lambda item: item[1])}

    recommended_movie(user, data, sorted_desc_movies, 5)
    print('-' * 41)
    recommended_movie(user, data, sorted_asc_movies, 5, "can't")
