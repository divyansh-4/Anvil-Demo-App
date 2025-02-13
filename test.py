import anvil.server
import unittest
from wrapper import app_tables
import anvil.tables.query as q
from anvil.tables import app_tables as anvil_app_tables

anvil.server.connect("server_EUULOP6PWUBMCRVWHL6SUTVD-LYUQJELFCMQWM33V")

class TestAppTablesSearch(unittest.TestCase):
    def row_to_dict(self,anvil_movies):
        anvil_movies_list=[]
        for i in range(len(list(anvil_movies))):
            temp={}
            for k,v in list(anvil_movies)[i]:
                temp[k]=v
            anvil_movies_list.append(temp)
        return anvil_movies_list

    def test_search_results(self):
        try:
            movies = app_tables.movies.search()
            anvil_movies = anvil_app_tables.movies.search()

            movies_list = self.row_to_dict(movies)
            anvil_movies_list = self.row_to_dict(anvil_movies)
            # print(movies_list)
            # print("Search Successful")
            self.assertEqual(movies_list, anvil_movies_list, "Mismatch found in complete search")
            # print("Search Successful")
        except Exception as e:
            print("\n⚠️ Test-> Search failed: ", str(e))
            self.fail("Test-> Search failed: ") 

    def test_search_onColumn(self):
        """Test search with a specific filter (movie_name="The Matrix")."""
        try:
            movies = app_tables.movies.search(movie_name="The Matrix")
            anvil_movies = anvil_app_tables.movies.search(movie_name="The Matrix")

            movies_list = self.row_to_dict(movies)
            anvil_movies_list = self.row_to_dict(anvil_movies)
            # print(movies_list)
            # print("Search with Filter Successful")
            self.assertEqual(movies_list, anvil_movies_list, "Mismatch found when filtering by movie_name")
        except Exception as e:
            print("\n⚠️ Test-> Search with filter failed: ", str(e))
            self.fail("Test-> Search with filter failed: ") 


    def test_search_onColumn(self):
        """Test search with a specific filter (movie_name="The Matrix")."""
        try:
            movies = app_tables.movies.search(movie_name="The Matrix")
            anvil_movies = anvil_app_tables.movies.search(movie_name="The Matrix")

            movies_list = self.row_to_dict(movies)
            anvil_movies_list = self.row_to_dict(anvil_movies)
            # print(movies_list)
            # print("Search with Filter Successful")
            self.assertEqual(movies_list, anvil_movies_list, "Mismatch found when filtering by movie_name")
        except Exception as e:
            print("\n⚠️ Test-> Search with filter failed: ", str(e))
            self.fail("Test-> Search with filter failed: ") 
    def test_search_Between(self):
        """Test search with a specific filter (movie_name="The Matrix")."""
        try:
            movies = app_tables.movies.search(year=q.greater_than(2008))
            anvil_movies = anvil_app_tables.movies.search(year=q.greater_than(2008))

            movies_list = self.row_to_dict(movies)
            anvil_movies_list = self.row_to_dict(anvil_movies)
            # print(movies_list)
            print("Search with Filter Successful")
            self.assertEqual(movies_list, anvil_movies_list, "Mismatch found when filtering using query operator")
        except Exception as e:
            print("\n⚠️ Test-> Search with between filter failed: ", str(e))
            self.fail("Test-> Search with between filter failed: ") 


if __name__ == "__main__":
    unittest.main()