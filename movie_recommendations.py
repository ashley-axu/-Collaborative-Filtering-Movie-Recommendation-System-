import math
import csv
from scipy.stats import pearsonr
class BadInputError(Exception):
    pass

class Movie_Recommendations:
    # Constructor
    def __init__(self, movie_filename, training_ratings_filename):
        """
        Initializes the Movie_Recommendations object from 
        the files containing movie names and training ratings.  
        The following instance variables should be initialized:
        self.movie_dict - A dictionary that maps a movie id to
               a movie objects (objects the class Movie)
        self.user_dict - A dictionary that maps user id's to a 
               a dictionary that maps a movie id to the rating
               that the user gave to the movie. 
        """   
        
        self.movie_dict = {}
        self.user_dict = {}

   
        f = open(movie_filename, 'r', encoding = 'utf8')
        f.readline()
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        for line in csv_reader:
            movieid = int(line[0])
            movietitle = line[1]
            self.movie_dict[movieid] = Movie(movieid, movietitle)


        f2 = open(training_ratings_filename, "r")
        f2.readline()
        csv_reader2 = csv.reader(f2, delimiter = ',', quotechar = '"')
        for line in csv_reader2:
            movieid = int(line[1])
            userid = int(line[0])
            movierating = float(line[2])
            movie = self.movie_dict[movieid]
            movie.users.append(userid) 
            if userid in self.user_dict:
                this_user_dict = self.user_dict[userid]
                this_user_dict[movieid] = movierating
            else:
                self.user_dict[userid] = {movieid : movierating}


    def predict_rating(self, user_id, movie_id):
        """
        Returns the predicted rating that user_id will give to the
        movie whose id is movie_id. 
        If user_id has already rated movie_id, return
        that rating.
        If either user_id or movie_id is not in the database,
        then BadInputError is raised.
        """
        try:
            if movie_id in self.user_dict[user_id]:
                return self.user_dict[user_id][movie_id]
            product_1 = 0
            sim = 0
            for movie in self.user_dict[user_id]:
                rating = self.user_dict[user_id][movie]
                similarity = self.movie_dict[movie].compute_similarity(movie_id, self.movie_dict, self.user_dict)
                product_1 += rating * similarity
                sim += similarity
            if sim == 0: 
                return 2.5
            product_1 /= sim
            return product_1

        except KeyError:
            raise BadInputError

    def predict_ratings(self, test_ratings_filename):
        """
        Returns a list of tuples, one tuple for each rating in the
        test ratings file.
        The tuple should contain
        (user id, movie title, predicted rating, actual rating)
        """

        tuples = []
        f = open(test_ratings_filename, "r")
        f.readline()
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        for rating in csv_reader:
            actual_rating = float(rating[2])
            predicted = self.predict_rating(int(rating[0]), int(rating[1]))
            tuples.append((int(rating[0]), self.movie_dict[int(rating[1])].title, predicted, actual_rating))
        return tuples

    def correlation(self, predicted_ratings, actual_ratings):
        """
        Returns the correlation between the values in the list predicted_ratings
        and the list actual_ratings.  The lengths of predicted_ratings and
        actual_ratings must be the same.
        """
        return pearsonr(predicted_ratings, actual_ratings)[0]
        
class Movie: 
    """
    Represents a movie from the movie database.
    """
    def __init__(self, id, title):
        """ 
        Constructor.
        Initializes the following instances variables.  You
        must use exactly the same names for your instance 
        variables.  (For testing purposes.)
        id: the id of the movie
        title: the title of the movie
        users: list of the id's of the users who have
            rated this movie.  Initially, this is
            an empty list, but will be filled in
            as the training ratings file is read.
        similarities: a dictionary where the key is the
            id of another movie, and the value is the similarity
            between the "self" movie and the movie with that id.
            This dictionary is initially empty.  It is filled
            in "on demand", as the file containing test ratings
            is read, and ratings predictions are made.
        """

        self.id = int(id)
        self.title = title
        self.users = []
        self.similarities = {}


    def __str__(self):
        """
        Returns string representation of the movie object.
        """
        #should return string of id and title
        return "id: " + str(self.id) + " title: " + self.title


    def __repr__(self):
        """
        Returns string representation of the movie object.
        """

        # turning list of users and dict of sim into string
        userStr = str(self.users)
        simStr = str(self.similarities)
        
        #should return string of id, title, user list and similarities
        return "id: " + str(self.id) + " title: " + self.title + " user list: " + userStr + " similarities: " + simStr

    def get_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        If the similarity has already been computed, return it.
        If not, compute the similarity (using the compute_similarity
        method), and store it in both
        the "self" movie object, and the other_movie_id movie object.
        Then return that computed similarity.
        If other_movie_id is not valid, raise BadInputError exception.
        """
        try:
            if other_movie_id in self.similarities:
                return self.similarities[other_movie_id]
            else:
                similarity = self.compute_similarity(other_movie_id, movie_dict, user_dict)
                self.similarities[other_movie_id] = similarity
                movie_dict[other_movie_id].similarities[self.id] = similarity
                return similarity
        except KeyError:
            raise BadInputError

    def compute_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Computes and returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        """

        # Users who have watched and rated both movies
        common_users = []
        for user in self.users:
            if user in movie_dict[other_movie_id].users:
                common_users.append(user)

        self_ratings = []
        another_ratings = []
        for i in range(len(common_users)):
            self_ratings.append(user_dict[common_users[i]].get(self.id))
            another_ratings.append(user_dict[common_users[i]].get(other_movie_id))

        #compute the average of those difference
        diff = 0
        diff_list = []
        if len(common_users) == 0:
            return 0
        else:
            for user in range(len(common_users)):
                diff = abs(self_ratings[user] - another_ratings[user]) 
                diff_list.append(diff)
        avg_diff = sum(diff_list) / len(common_users)
        similarity = 1 - (avg_diff / 4.5)
        self.similarities[other_movie_id] = similarity
        return similarity
        
       

if __name__ == "__main__":
    # Create movie recommendations object.
    movie_recs = Movie_Recommendations("movies.csv", "training_ratings.csv")
    
    # Predict ratings for user/movie combinations
    rating_predictions = movie_recs.predict_ratings("test_ratings.csv")
    print("Rating predictions: ")
    for prediction in rating_predictions:
        print(prediction)
    predicted = [rating[2] for rating in rating_predictions]
    actual = [rating[3] for rating in rating_predictions]
    correlation = movie_recs.correlation(predicted, actual)
    print(f"Correlation: {correlation}")  
