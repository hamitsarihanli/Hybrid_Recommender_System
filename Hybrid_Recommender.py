import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
movie = pd.read_csv('D:/DSMLBC4/Dersler/Hafta_10/movie.csv')
movie.head()
rating = pd.read_csv('D:/DSMLBC4/Dersler/Hafta_10/rating.csv')
rating.head()
df = movie.merge(rating, how="left", on="movieId") # movie ve verilen puanlari birlestirdik.
df.head()
df.shape
rating.shape
movie.shape

#############
# USER-BASED
#############


def create_user_movie_df():
    df['title'] = df.title.str.replace('(\(\d\d\d\d\))', '') #yili boslukla degistir
    df['title'] = df['title'].apply(lambda x: x.strip()) #bosluklari sil
    a = pd.DataFrame(df["title"].value_counts())
    rare_movies = a[a["title"] <= 1000].index #1000'den az yorum alan filmleri filtrele
    common_movies = df[~df["title"].isin(rare_movies)]
    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
    return user_movie_df

user_movie_df = create_user_movie_df()
user_movie_df.shape
user_movie = user_movie_df[user_movie_df.index == 108170]
user_movie

movies_watched = user_movie.columns[user_movie.notna().any()].tolist()
movies_watched
#check wathced movie
user_movie_df.loc[108170, user_movie_df.columns == "Spider-Man 2"]
# # of watched movies
len(movies_watched)

movies_watched_df = user_movie_df[movies_watched]
movies_watched_df.head()
movies_watched_df.shape

user_movie_count = movies_watched_df.T.notnull().sum()
user_movie_count = user_movie_count.reset_index()
user_movie_count.columns = ["userId", "movie_count"]


perc = len(movies_watched) * 60 / 100
user_same_movies = user_movie_count[user_movie_count.movie_count > perc]["userId"]

user_same_movies.nunique() #2342

final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(user_same_movies.index)], user_movie[movies_watched]])
final_df.head()
final_df.T.corr()

# who_ls DataFrame
# alldfs = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ["user_id_1", "user_id_2"]
corr_df = corr_df.reset_index()
corr_df.head()

top_users = corr_df[(corr_df["user_id_1"] == 108170) & (corr_df["corr"] >= 0.65)][["user_id_2", "corr"]].reset_index(drop=True)
top_users = top_users.sort_values("corr", ascending=False)
top_users.rename(columns={"user_id_2":"userId"}, inplace=True)
top_users

top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how="inner")
top_users_ratings

top_users_ratings["weighted_rating"] = top_users_ratings["corr"] * top_users_ratings["rating"]
top_users_ratings.head()

temp = top_users_ratings.groupby("movieId").sum()[["corr", "weighted_rating"]]
temp.columns = ["sum_corr", "sum_weighted_rating"]
temp.head()

recommendation_df = pd.DataFrame()
recommendation_df["weighted_average_recommendation_score"] = temp["sum_weighted_rating"] / temp["sum_corr"]
recommendation_df["movieId"] = temp.index
recommendation_df = recommendation_df.sort_values("weighted_average_recommendation_score", ascending=False)
recommendation_df.head()

movie.loc[movie.movieId.isin(recommendation_df.head(10)["movieId"])]

top_5_ub_recom = recommendation_df.head().reset_index(drop=True)
movie.head()
top_5_ub_recom.head()
movies_from_user_based = top_5_ub_recom.merge(movie, how="inner")
movies_from_user_based = movies_from_user_based.title

#############
# ITEM-BASED
#############


def item_based_recommender(movie_name):
    # film umd'de yoksa önce ismi barındıran ilk filmi getir.
    # eger o da yoksa filmin isminin ilk iki harfini barındıran ilk filmi getir.
    if movie_name not in user_movie_df:
        # ismi barındıran ilk filmi getir.
        if [col for col in user_movie_df.columns if movie_name.capitalize() in col]:
            new_movie_name = [col for col in user_movie_df.columns if movie_name.capitalize() in col][0]
            movie = user_movie_df[new_movie_name]
            print(F"{movie_name}'i barındıran ilk  film: {new_movie_name}\n")
            print(F"{new_movie_name} için öneriler geliyor...\n")
            return user_movie_df.corrwith(movie).sort_values(ascending=False).head(10)
        # filmin ilk 2 harfini barındıran ilk filmi getir.
        else:
            new_movie_name = [col for col in user_movie_df.columns if col.startswith(movie_name.capitalize()[0:2])][0]
            movie = user_movie_df[new_movie_name]
            print(F"{movie_name}'nin ilk 2 harfini barındıran ilk film: {new_movie_name}\n")
            print(F"{new_movie_name} için öneriler geliyor...\n")
            return user_movie_df.corrwith(movie).sort_values(ascending=False).head(10)
    else:
        print(F"{movie_name} için öneriler geliyor...\n")
        movie = user_movie_df[movie_name]
        return user_movie_df.corrwith(movie).sort_values(ascending=False).head(10)

df.columns
movie_ib_user_df = df[df["userId"] == 108170]
movie_ib_user_df.sort_values(["rating", "timestamp"], ascending=False)#.iloc[0, 0]

movie_ib_user_df['title_new'] = movie_ib_user_df.title.str.replace('(\(\d\d\d\d\))', '')
movie_ib_user_df['title_new'] = movie_ib_user_df['title_new'].apply(lambda x: x.strip())
movie_ib_name = movie_ib_user_df.sort_values(["rating", "timestamp"], ascending=False).head(1)["title_new"]
movie_ib_name
movies_from_item_based = item_based_recommender("Wild at Heart")

movies_from_item_based[1:6].index
#Index(['My Science Project', 'Mediterraneo', 'National Lampoon's Senior Trip',
#       'Old Man and the Sea, The', 'Cashback'],
#      dtype='object', name='title')



movies_from_user_based
#                       African Queen, The (1951)
#                       North by Northwest (1959)
#             Mr. Smith Goes to Washington (1939)
#                                Baby Boom (1987)
#    My Neighbor Totoro (Tonari no Totoro) (1988)

