import unittest, hashlib
import main

class RetrieveRankTest(unittest.TestCase):
    def setUp(self):
        self.retran = main.hnsGame()

    def test_watson_classification_true(self):
        self.assertTrue(self.retran.isWatsonQuery("hey watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("help watson! how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("watson. How can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("yo watson how can i talk him down"))
        self.assertTrue(self.retran.isWatsonQuery("yo   watson how can i talk him down"))

    def test_watson_classification_false(self):
        self.assertFalse(self.retran.isWatsonQuery("how can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery("     how can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery("how can i talk him down, Watson?"))
        self.assertFalse(self.retran.isWatsonQuery("How can i talk him down"))
        self.assertFalse(self.retran.isWatsonQuery(""))


    def test_failed_retrieve_rank(self):
        m = hashlib.md5()
        m.update("no one expects the spanish inquisition".encode('utf-8'))
        reply = self.retran.watson(m.digest())
        self.assertEqual(reply, "I'm sorry, they don't teach that at the academy")

if __name__ == '__main__':
    unittest.main()
