import pandas as pd
import os
from path_utils import Path_Handler as ph


def truncate_data(
    movies,
    movies_genres,
    movies_directors,
    directors,
    directors_genres,
    roles,
    actors,
    movie_sample_size=2000,
    roles_per_movie=2,
    random_state=42,
):
    # Filter movies present in all three link tables
    movies_in_genres = set(movies_genres["movie_id"])
    movies_in_directors = set(movies_directors["movie_id"])
    movies_in_roles = set(roles["movie_id"])

    connected_movies = movies_in_genres & movies_in_directors & movies_in_roles

    # Sample connected movies
    sampled_movies = movies[movies["id"].isin(connected_movies)].sample(
        n=movie_sample_size, random_state=random_state
    )

    # Filter related tables
    filtered_movies_genres = movies_genres[
        movies_genres["movie_id"].isin(sampled_movies["id"])
    ]
    filtered_movies_directors = movies_directors[
        movies_directors["movie_id"].isin(sampled_movies["id"])
    ]

    # Get valid director_ids from selected movies
    relevant_directors = set(filtered_movies_directors["director_id"])
    filtered_directors = directors[directors["id"].isin(relevant_directors)]

    # Filter directors_genres
    filtered_directors_genres = directors_genres[
        directors_genres["director_id"].isin(relevant_directors)
    ]

    # Limit roles to those within sampled movies (max roles_per_movie per movie)
    filtered_roles = roles[roles["movie_id"].isin(sampled_movies["id"])]
    filtered_roles = (
        filtered_roles.groupby("movie_id")
        .head(roles_per_movie)
        .reset_index(drop=True)
    )

    # Get valid actor_ids
    relevant_actors = set(filtered_roles["actor_id"])
    filtered_actors = actors[actors["id"].isin(relevant_actors)]

    return {
        "movies": sampled_movies.reset_index(drop=True),
        "movies_genres": filtered_movies_genres.reset_index(drop=True),
        "movies_directors": filtered_movies_directors.reset_index(drop=True),
        "directors": filtered_directors.reset_index(drop=True),
        "directors_genres": filtered_directors_genres.reset_index(drop=True),
        "roles": filtered_roles,
        "actors": filtered_actors.reset_index(drop=True),
    }


imdb_dir_PATH: str = ph.imdb_csv_folder_PATH

movies = pd.read_csv(os.path.join(imdb_dir_PATH, "movies.csv"))
movies_genres = pd.read_csv(os.path.join(imdb_dir_PATH, "movies_genres.csv"))
movies_directors = pd.read_csv(
    os.path.join(imdb_dir_PATH, "movies_directors.csv")
)
directors = pd.read_csv(os.path.join(imdb_dir_PATH, "directors.csv"))
directors_genres = pd.read_csv(
    os.path.join(imdb_dir_PATH, "directors_genres.csv")
)
roles = pd.read_csv(os.path.join(imdb_dir_PATH, "roles.csv"))
actors = pd.read_csv(os.path.join(imdb_dir_PATH, "actors.csv"))

reduced_data = truncate_data(
    movies,
    movies_genres,
    movies_directors,
    directors,
    directors_genres,
    roles,
    actors,
)

# Access individual dataframes
reduced_movies: pd.DataFrame = reduced_data["movies"]
reduced_movies_genres: pd.DataFrame = reduced_data["movies_genres"]
reduced_movies_directors: pd.DataFrame = reduced_data["movies_directors"]
reduced_directors: pd.DataFrame = reduced_data["directors"]
reduced_directors_genres: pd.DataFrame = reduced_data["directors_genres"]
reduced_actors: pd.DataFrame = reduced_data["actors"]
reduced_roles: pd.DataFrame = reduced_data["roles"]

truncated_imdb_folder_PATH = os.path.join(
    ph.project_root_PATH, "imdb_ijs_truc_csv"
)

reduced_movies.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "movies.csv"), index=False
)
reduced_movies_genres.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "movies_genres.csv"), index=False
)
reduced_movies_directors.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "movies_directors.csv"),
    index=False,
)
reduced_directors.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "directors.csv"), index=False
)
reduced_directors_genres.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "directors_genres.csv"),
    index=False,
)
reduced_actors.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "actors.csv"), index=False
)
reduced_roles.to_csv(
    os.path.join(truncated_imdb_folder_PATH, "roles.csv"), index=False
)
# etc.
