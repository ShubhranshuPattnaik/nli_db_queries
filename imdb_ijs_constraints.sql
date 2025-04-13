USE `imdb_ijs`;

-- Add Primary Keys
ALTER TABLE `actors`
ADD PRIMARY KEY (`id`);

ALTER TABLE `directors`
ADD PRIMARY KEY (`id`);

ALTER TABLE `movies`
ADD PRIMARY KEY (`id`);

-- Add Foreign Keys with CASCADE

-- roles → actors
ALTER TABLE `roles`
ADD CONSTRAINT `fk_roles_actor`
FOREIGN KEY (`actor_id`) REFERENCES `actors`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- roles → movies
ALTER TABLE `roles`
ADD CONSTRAINT `fk_roles_movie`
FOREIGN KEY (`movie_id`) REFERENCES `movies`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- movies_directors → movies
ALTER TABLE `movies_directors`
ADD CONSTRAINT `fk_movies_directors_movie`
FOREIGN KEY (`movie_id`) REFERENCES `movies`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- movies_directors → directors
ALTER TABLE `movies_directors`
ADD CONSTRAINT `fk_movies_directors_director`
FOREIGN KEY (`director_id`) REFERENCES `directors`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- movies_genres → movies
ALTER TABLE `movies_genres`
ADD CONSTRAINT `fk_movies_genres_movie`
FOREIGN KEY (`movie_id`) REFERENCES `movies`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- directors_genres → directors
ALTER TABLE `directors_genres`
ADD CONSTRAINT `fk_directors_genres_director`
FOREIGN KEY (`director_id`) REFERENCES `directors`(`id`)
ON DELETE CASCADE ON UPDATE CASCADE;
