import argparse
import json
import numpy as np

from compute_scores import euclidean_score

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Find users who are similar to the input user')
    parser.add_argument('--user', dest='user', required=True,
            help='Input user')
    return parser

# Finds users in the dataset that are similar to the input user 
def find_similar_users(dataset, user, num_users):
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

if __name__=='__main__':
    args = build_arg_parser().parse_args()
    user = args.user

    ratings_file = 'history.json'

    with open(ratings_file, 'r') as f:
        data = json.loads(f.read())

    print('\nUsers similar to ' + user + ':\n')
    similar_users = find_similar_users(data, user, 3) 
    print('User\t\t\tSimilarity score')
    print('-'*41)
    for item in similar_users:
        print(f'{item[0]}\t\t{round(float(item[1]), 2)}')

    searched_user_common_1_filmes = []

    user_films = []

    print(f'User {user} films: ')
    for film in data[user]:
        print(f'\t{film} - {data[user][film]}')
        user_films.append(film)

    similar1_films = []
    similar2_films = []
    similar3_films = []
    i = 0

    for _user in data:
        # print(user)
        for similar_user_name, similar_user_score in similar_users:
            #print(similar_user_name)
            if _user == similar_user_name:
                print(f'Common films with {similar_user_name}:')
                for film in data[_user]:
                    if film not in data[user]:
                        continue
                    print(f'\t{film} - {data[user][film]}')

                    if i == 0:
                        similar1_films.append(film)
                    elif i == 1:
                        similar2_films.append(film)
                    elif i == 2:
                        similar3_films.append(film)
                    i += 1

    common_films_of_all_users = []

    for i in range(0, 3):
        user = similar_users[i][0]
        print(f'{user}\'s films:')
        for film in data[user]:
            print(f'\t{film} - {data[user][film]}')

    for film1 in data[similar_users[0][0]]:
        for film2 in data[similar_users[1][0]]:
            for film3 in data[similar_users[2][0]]:
                if film1 == film2 or film1 == film3:
                    common_films_of_all_users.append(film1)
                elif film2 == film3:
                    common_films_of_all_users.append(film3)

    print(f'All commons films:')
    for film in common_films_of_all_users:
        print(f'\t{film}')