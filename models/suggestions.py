def get_skill_suggestions(weak_skills):
    suggestion_map = {
        "Python": [
            "Practice OOP concepts like inheritance, polymorphism, and encapsulation.",
            "Revise functions, lists, dictionaries, file handling, and exception handling.",
            "Solve beginner-to-intermediate coding problems in Python."
        ],
        "SQL": [
            "Practice joins, subqueries, GROUP BY, HAVING, and aggregate functions.",
            "Revise normalization, primary key, foreign key, and indexing concepts.",
            "Write 15–20 SQL queries on sample employee/student datasets."
        ],
        "DBMS": [
            "Revise normalization, ACID properties, transactions, keys, and indexing.",
            "Understand difference between DBMS and RDBMS.",
            "Practice ER diagrams and SQL-based DBMS questions."
        ],
        "Machine Learning": [
            "Revise supervised vs unsupervised learning.",
            "Understand regression, classification, train-test split, overfitting, and evaluation metrics.",
            "Practice small projects using scikit-learn."
        ],
        "Flask": [
            "Practice routes, templates, request handling, forms, and project structure.",
            "Build small CRUD apps to strengthen backend fundamentals."
        ],
        "Data Structures": [
            "Revise arrays, strings, stacks, queues, linked lists, trees, and hash maps.",
            "Practice time complexity and common coding problems."
        ],
        "NLP": [
            "Revise tokenization, stemming, lemmatization, stopwords, and vectorization.",
            "Practice text classification and sentiment analysis mini-projects."
        ]
    }

    suggestions = []

    for skill in weak_skills:
        if skill in suggestion_map:
            suggestions.append({
                "skill": skill,
                "tips": suggestion_map[skill]
            })
        else:
            suggestions.append({
                "skill": skill,
                "tips": [f"Practice core concepts and interview questions in {skill}."]
            })

    return suggestions