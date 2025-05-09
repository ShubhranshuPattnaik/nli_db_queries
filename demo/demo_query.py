# demo_query.py

DEMO_QUERIES = {
    "-list paper ids from cora database that are cited more than 3 times, sorted by the number of times they are cited (descending), showing only the top 10 results.": {
        "dbms_type": "sql",
        "db_name": "CORA",
        "query": "SELECT c.citing_paper_id AS paper_id FROM cites c GROUP BY c.citing_paper_id HAVING COUNT(*) > 3 ORDER BY COUNT(*) DESC LIMIT 10;",
    },
    "-list each client and the number of loans they have, but include only those clients who have at least one loan from financial database.": {
        "dbms_type": "sql",
        "db_name": "financial",
        "query": "SELECT c.client_id, COUNT(*) AS loan_count FROM client c JOIN disp d ON c.client_id = d.client_id JOIN loan l ON d.account_id = l.account_id GROUP BY c.client_id HAVING loan_count >= 1 ORDER BY loan_count DESC;",
    },
    "-list the next 10 clients after skipping the first 10, including their district names from financial database.": {
        "dbms_type": "sql",
        "db_name": "financial",
        "query": "SELECT c.client_id, d2.A2 AS district_name FROM client c JOIN district d2 ON c.district_id = d2.district_id ORDER BY c.client_id LIMIT 10 OFFSET 10;",
    },
    "-show the average loan payment for each loan status in the financial database.": {
        "dbms_type": "sql",
        "db_name": "financial",
        "query": "SELECT l.status, AVG(l.payments) AS avg_payment FROM loan l GROUP BY l.status;",
    },
    # // New entry: List tables in CORA
    "-What tables are there in the CORA database?": {
        "dbms_type": "sql",
        "db_name": "CORA",
        "query": "SHOW TABLES;",
    },
    # // New entry: Insert a new paper
    "-In MYSQL, Add a new paper with ID 2025 and class label AI to the CORA paper table.": {
        "dbms_type": "sql",
        "db_name": "CORA",
        "query": "INSERT INTO paper (paper_id, class_label) VALUES (2025, 'AI');",
    },
    # === Schema Exploration ===
    "-list collections in the imdb_ijs mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "imdb_ijs",
        "query": "show collections",
    },
    "-get 3 sample documents from the roles collection in the imdb_ijs mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "imdb_ijs",
        "query": "db.roles.find().limit(3)",
    },
    # === Querying ===
    "-list all male actors from the imdb_ijs mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "imdb_ijs",
        "query": "db.actors.find({ gender: 'M' })",
    },
    "-list all movies directed by Christopher Nolan from the imdb_ijs mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "imdb_ijs",
        "query": """db.movies_directors.aggregate([
            {
                $lookup: {
                    from: "directors",
                    localField: "director_id",
                    foreignField: "id",
                    as: "director_info"
                }
            },
            { $unwind: "$director_info" },
            { $match: {
                "director_info.first_name": "Christopher",
                "director_info.last_name": "Nolan"
            }},
            {
                $lookup: {
                    from: "movies",
                    localField: "movie_id",
                    foreignField: "id",
                    as: "movie_info"
                }
            },
            { $unwind: "$movie_info" },
            { $project: { _id: 0, "movie_info.name": 1 } }
        ])""",
    },
    "-list each genre and the number of movies in that genre from imdb_ijs mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "imdb_ijs",
        "query": """db.movies_genres.aggregate([
            { $group: { _id: "$genre", count: { $sum: 1 } }},
            { $sort: { count: -1 } }
        ])""",
    },
    "-list paper ids from cora mongodb database that are cited atleast once, sorted by citations descending, top 10 only.": {
        "dbms_type": "mongo",
        "db_name": "cora",
        "query": """db.cites.aggregate([
            { $group: { _id: "$cited_paper_id", count: { $sum: 1 } }},
            { $match: { count: { $gte: 1 }}},
            { $sort: { count: -1 }},
            { $limit: 10 }
        ])""",
    },
    "-list the average loan payment grouped by status in financial mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "financial",
        "query": """db.loan.aggregate([
            { $group: { _id: "$status", avg_payment: { $avg: "$payments" }}}
        ])""",
    },
    "-list 10 clients from financial mongodb database with their district names after skipping the first 10.": {
        "dbms_type": "mongo",
        "db_name": "financial",
        "query": """db.client.aggregate([
            {
                $lookup: {
                    from: "district",
                    localField: "district_id",
                    foreignField: "district_id",
                    as: "district"
                }
            },
            { $unwind: "$district" },
            { $project: { client_id: 1, district_name: "$district.A2" }},
            { $skip: 10 },
            { $limit: 10 }
        ])""",
    },
    "-add a new client named Jane Doe in district 10 to financial mogodb database.": {
        "dbms_type": "mongo",
        "db_name": "financial",
        "query": """db.client.insertOne({
            client_id: 99999,
            gender: "F",
            birth_date: "1990-01-01",
            district_id: 10
        })""",
    },
    "-update the gender of client Jane Doe to 'M' in financial mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "financial",
        "query": """db.client.updateOne(
            { client_id: 99999 },
            { $set: { gender: "M" }}
        )""",
    },
    "-delete the client Jane Doe from financial mongodb database.": {
        "dbms_type": "mongo",
        "db_name": "financial",
        "query": """db.client.deleteOne({ client_id: 99999 })""",
    },
}
