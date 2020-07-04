from das.routing.core.algorithms.strings import levenshtein_distance


class TestLevenshteinDistance(object):
    def test_same_string_distance_is_zero(self):
        string = "abcde"

        assert levenshtein_distance(string, string) == 0

    def test_one_substituton_distance_is_one(self):
        string = "abcde"

        assert levenshtein_distance(string, string.replace("c", "d")) == 1

    def test_two_substitutons_distance_is_two(self):
        string = "abcde"

        assert levenshtein_distance(string, string.replace("cd", "dc")) == 2

    def test_one_addition_distance_is_one(self):
        string = "abcde"

        assert levenshtein_distance(string, string + "f") == 1

    def test_same_zero_length_string_distance_is_zero(self):
        string = ""

        assert levenshtein_distance(string, string) == 0

    def test_zero_length_string_distance_to_one_char_string_is_one(self):
        string = ""

        assert levenshtein_distance(string, "a") == 1
