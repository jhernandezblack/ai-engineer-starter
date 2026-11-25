import tempfile
import unittest
from pathlib import Path
from starter.core import run_agent, tool, propose, decide, retrieve, answer, safe_path

class StartersTest(unittest.TestCase):
    def test_allowlisted_tool_and_argument_types(self):
        self.assertEqual(tool({'tool':'stock','arguments':{'item':'notebook'}}), {'item':'notebook','quantity':12})
        for request in [{'tool':'shell','arguments':{}}, {'tool':'stock','arguments':{'item':12}}, {'tool':'stock','arguments':{'item':'notebook','extra':True}}]:
            with self.assertRaises(ValueError): tool(request)

    def test_agent_observes_result_and_stops(self):
        requests = iter([{'tool':'stock','arguments':{'item':'notebook'}}, {'answer':'12 notebooks'}])
        history=[]
        def model(messages, timeout):
            history.append(list(messages))
            return next(requests)
        self.assertEqual(run_agent(model,'stock?'), '12 notebooks')
        self.assertIn('12', history[1][-1]['content'])

    def test_steps_and_deadline_stop_model_calls(self):
        calls=[]
        def model(messages, timeout):
            calls.append(timeout)
            return {'tool':'stock','arguments':{'item':'notebook'}}
        with self.assertRaises(ValueError): run_agent(model,'x',max_steps=2)
        self.assertEqual(len(calls),2)
        times=iter([0,4])
        with self.assertRaises(TimeoutError): run_agent(model,'x',seconds=3,clock=lambda:next(times))
        self.assertEqual(len(calls),2)

    def test_approval_survives_reload_and_is_required_for_effect(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            state=propose(root,'Draft reply')
            self.assertEqual(state['status'],'pending')
            self.assertFalse((root/'reply.txt').exists())
            with self.assertRaises(ValueError): decide(root,'yes')
            self.assertFalse((root/'reply.txt').exists())
            self.assertEqual(decide(root,'APPROVE')['status'],'approved')
            self.assertEqual((root/'reply.txt').read_text(),'Draft reply')
            with self.assertRaises(ValueError): decide(root,'APPROVE')

    def test_reject_and_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            propose(root,'Draft')
            self.assertEqual(decide(root,'REJECT')['status'],'rejected')
            self.assertFalse((root/'reply.txt').exists())
            for name in ['../escape','/tmp/escape']:
                with self.assertRaises(ValueError): safe_path(root,name)
            (root/'link').symlink_to('/tmp')
            with self.assertRaises(ValueError): safe_path(root,'link/escape')

    def test_retrieval_citations_and_unknown_abstention(self):
        docs={'policy.txt':'Returns accepted within 30 days.', 'shipping.txt':'Shipping takes 5 days.'}
        self.assertEqual([x['source'] for x in retrieve('returns',docs)],['policy.txt'])
        def good(messages,timeout): return {'answer':'30 days [policy.txt]','sources':['policy.txt']}
        self.assertEqual(answer('returns',docs,good)['sources'],['policy.txt'])
        def bad(messages,timeout): return {'answer':'90 days [fake.txt]','sources':['fake.txt']}
        self.assertTrue(answer('returns',docs,bad)['abstained'])
        self.assertTrue(answer('volcano',docs,good)['abstained'])
        def missing(messages,timeout): return {'answer':'30 days','sources':['policy.txt']}
        self.assertTrue(answer('returns',docs,missing)['abstained'])

if __name__=='__main__': unittest.main()

class BoundsTest(unittest.TestCase):
    def test_model_text_output_bound(self):
        with self.assertRaises(ValueError): run_agent(lambda *_:{'answer':'a'*4001},'x')
        with self.assertRaises(ValueError): propose(Path('/tmp/unused-starter-test'),'a'*4001)

    def test_state_cannot_redirect_output(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'state.json').write_text(json.dumps({'status':'pending','draft':'x','output':'../escape'}))
            with self.assertRaises(ValueError): decide(root,'APPROVE')
            self.assertFalse((root/'reply.txt').exists())
