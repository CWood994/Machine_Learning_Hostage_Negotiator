import unittest, hashlib, sndhdr
import game_utils

class RetrieveRankTest(unittest.TestCase):
    def setUp(self):
        self.retran = game_utils.utils()

    #These test are for the identification of phrases that should trigger RR
    def test_watson_classification_true(self):
        self.assertTrue(self.retran.isWatsonQuery("hey watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("help watson! how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("watson. How can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("yo watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("yo   watson how can i talk him down"))

    #These test are for the identification of phrases that should not trigger RR
    def test_watson_classification_false(self):
        self.assertFalse(self.retran.isWatsonQuery("how can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery("     how can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery("how can i talk him down, Watson?"))
        self.assertFalse(self.retran.isWatsonQuery("How can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery(""))

    #Test that utter nonsense doesn't return an empty result
    def test_failed_retrieve_rank(self):
        m = hashlib.md5()
        m.update("no one expects the spanish inquisition".encode('utf-8'))
        reply = self.retran.rr_query_first_result(m.digest())
        self.assertEqual(reply, "I'm sorry, they don't teach that at the academy")

    def test_input_cleansing(self):
        self.assertTrue(self.retran.cleanse_rr_string("hey watson, hey watson.") == "hey watson.")
        self.assertTrue(self.retran.cleanse_rr_string("hey watson,                       hey watson.") == "hey watson.")
        self.assertTrue(self.retran.cleanse_rr_string("help WATSON! he's crazy") == "he's crazy")

    #Test that a valid wav is created by rr_process (shouldn't be a problem)
    def test_valid_wav_creation(self):
        self.retran.rr_process("beep")
        self.assertTrue(sndhdr.what('output.wav')[0]=='wav')

if __name__ == '__main__':
    unittest.main()
