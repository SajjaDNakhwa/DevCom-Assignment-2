import random
import datetime
import uuid
_DATA_KEYS = ["a", "b", "c"]
class Device:
    def __init__(self, id):
        self._id = id
        self.records = []
        self.sent = []
    def obtainData(self) -> dict:
        if random.random() < 0.4:
            return {}
        rec = {
            'type': 'record',
            'timestamp': datetime.datetime.now().isoformat(),
            'dev_id': self._id,
            'data': {kee: str(uuid.uuid4()) for kee in _DATA_KEYS}}
        self.sent.append(rec)
        return rec
    def probe(self) -> dict:
        return {'type': 'probe', 'dev_id': self._id, 'from': len(self.records)}
    def onMessage(self, data: dict):
        if data is not None and 'type' in data and data['type'] == 'update':
            
            _from = data['from']
            if _from > len(self.records):
                return
            self.records += list(data['data'].values()) #changed since earlier it was appending a dictionary to a list
class SyncService:
    def __init__(self):
        self.data_to_send = {}

    def onMessage(self, data: dict):
        if 'type' in data and data['type'] == 'probe':
            dev_id = data['dev_id']
            from_index = data.get('from', 0)
            update_data = self.genUpdates(dev_id, from_index)
            return {'type': 'update', 'from': from_index, 'data': update_data}
        elif 'type' in data and data['type'] == 'record':
            return #record not to be returned
        else:
            return
    def genUpdates(self, dev_id: str, from_index: int) -> dict:
        #print({f'dev_{dev_id}_data_{i}': str(uuid.uuid4()) for i in range(from_index, from_index + 3)})
        return {f'dev_{dev_id}_data_{i}': str(uuid.uuid4()) for i in range(from_index, from_index + 3)}  # Generating 3 data points


def testSyncing():
    devices = [Device(f"dev_{i}") for i in range(10)]
    syn = SyncService()

    _N = int(1e2)
    for i in range(_N):
        for _dev in devices:
            data = _dev.obtainData()
            syn.onMessage(data)
            probe_response = syn.onMessage(_dev.probe())
            if probe_response is not None and 'data' in probe_response: #to check whether response has been created or not, evolved when responses not created due to the random simulation
                syn.data_to_send[_dev._id] = probe_response['data']
            _dev.onMessage(probe_response)
            if probe_response is not None:
                  _dev.onMessage(probe_response)
    done = False
    while not done:
        for _dev in devices:
            _dev.onMessage(syn.onMessage(_dev.probe()))
        num_recs = len(devices[0].records)
        done = all([len(_dev.records) == num_recs for _dev in devices])
        # print(done) #for debugging
    ver_start = [0] * len(devices)
    for i in devices[0].records:
        new_device = [(f"dev_{i}") for i in range(10)]
        for rec in new_device: #changed way to access `rec` since earlier it was targeting the uuid instead of the object
            #print(devices[0].records) #for debugging
            print(rec)
            _dev_idx = int(rec.split("_")[-1])
            print(_dev_idx)
            assertEquivalent(rec, devices[_dev_idx].sent[ver_start[_dev_idx]])
        for _dev in devices[1:]:
            assertEquivalent(rec, _dev.records[i])
        ver_start[_dev_idx] += 1
        
    
def assertEquivalent(d1: dict, d2: dict): #was getting a `string indices must be integers` error even though d1 and d2 are dictionaries
    assert (dict(d1))['dev_id'] == (dict(d2))['dev_id'] #tried manually converting d1 and d2 as dicts but getting `ValueError: dictionary update sequence element #0 has length 1; 2 is required`
    assert dict(d1)['timestamp'] == dict(d2)['timestamp']
    for kee in _DATA_KEYS:
        assert dict(d1)['data'][kee] == dict(d2)['data'][kee]
testSyncing()
print(f"Syncing Successful! oogabooga")