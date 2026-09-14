import tempfile, unittest
from pathlib import Path
from app.db import get_connection, init_db
from app.service import FeedbackInput, add_feedback, create_business, create_location, dashboard

class ReviewPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"test.db"
        init_db(self.path)
        self.conn=get_connection(self.path)
    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()
    def test_create_workspace(self):
        b=create_business(self.conn,"Northside Coffee")
        l,t=create_location(self.conn,b,"Main")
        self.assertGreater(b,0); self.assertGreater(l,0); self.assertTrue(t)
    def test_trial_location_limit(self):
        b=create_business(self.conn,"Cafe")
        create_location(self.conn,b,"Main")
        with self.assertRaisesRegex(ValueError,"Location limit"):
            create_location(self.conn,b,"Second")
    def test_dashboard_metrics(self):
        b=create_business(self.conn,"Clinic")
        _,t=create_location(self.conn,b,"Downtown")
        add_feedback(self.conn,t,FeedbackInput(5,"service","Great"))
        add_feedback(self.conn,t,FeedbackInput(2,"speed","Slow"))
        d=dashboard(self.conn,b)
        self.assertEqual(d["metrics"]["total_feedback"],2)
        self.assertEqual(d["metrics"]["average_rating"],3.5)
        self.assertEqual(d["metrics"]["low_rating_count"],1)
    def test_invalid_rating(self):
        b=create_business(self.conn,"Shop")
        _,t=create_location(self.conn,b,"Main")
        with self.assertRaisesRegex(ValueError,"Rating"):
            add_feedback(self.conn,t,FeedbackInput(8,"service",""))
    def test_invalid_category(self):
        b=create_business(self.conn,"Shop Two")
        _,t=create_location(self.conn,b,"Main")
        with self.assertRaisesRegex(ValueError,"Invalid category"):
            add_feedback(self.conn,t,FeedbackInput(5,"unknown",""))

if __name__=="__main__":
    unittest.main()
