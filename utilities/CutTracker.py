import collections
from prettytable import PrettyTable

class Cut(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name
    def evaluate(self, rtrow):
        return self.function(rtrow) 
    def getName(self):
        return self.name
class CutSequence(object):
    '''
    A class for defining cut orders for preselection.
    '''
    def __init__(self):
        self.cut_sequence = []
    def add(self, cut_function, name):
        cut = Cut(cut_function, name)
        self.cut_sequence.append(cut)
        self.num_cuts = len(self.cut_sequence)
    def addCut(self, cut):
        self.cut_sequence.append(cut)
        self.num_cuts = len(self.cut_sequence)
    def evaluate(self, rtrow):
        cut_history = collections.OrderedDict()
        for cut in self.cut_sequence:
            passed = cut.evaluate(rtrow)
            cut_history[cut.getName()] =  passed
        return cut_history

    def getCuts(self):
        return self.cut_sequence

    def addSequence(self, sequence):
        for cut in sequence.getCuts():
            self.cut_sequence.append(cut)
        self.num_cuts += len(sequence)

class CutTracker(object):
    def __init__(self, sequence = CutSequence()):
        self.sequence = sequence
        self.num_events = 0
        self.event_record = {}
        self.cutflow = collections.OrderedDict([ (x.getName(), 0) 
                                        for x in self.sequence.getCuts()])
    def add_sequence(self, sequence):
        sequence.addSequence(sequence)
        self.cutflow = collections.OrderedDict([ (x.getName(), 0) 
                                        for x in self.sequence.getCuts()])
    def track_event(self, rtrow, event_id):
        if event_id in self.event_record:
            new_record = self.sequence.evaluate(rtrow)
            old_record = self.event_record[event_id]
            for name in old_record:
                if not old_record[name] or not new_record[name]:
                    if not old_record[name] and new_record[name]:
                        self.event_record[event_id] = new_record
                    break
        else:
            self.event_record.update({event_id : self.sequence.evaluate(rtrow)})
        return False in self.event_record[event_id].values()
    def store_cutflow(self):
        for event_id, record in self.event_record.iteritems():
            for cut_name, passed in record.iteritems():
                self.num_events += 1
                if passed:
                    self.cutflow[cut_name] += 1
                else:
                    break
        self.event_record = {}
    def make_cutflow(self):
        cutflow_hist = rt.TH1F('cutflow','cutflow',len(sequence),0,len(sequence))
        cutflow_hist.SetBinContent(1, self.num_events)
        for i, cut_name in enumerate(self.cutflow):
            cutflowHist.SetBinContent(i + 1, self.cutflow[cut_name])
            cutflowHist.SetBinLabel(i + 1, cut_name)
        return cutflow_hist
    def Print(self):
        table = PrettyTable(["Cut", "Events Passing" ])
        for name, number in self.cutflow.iteritems():
            print "Name is %s number is %i" % (name, number)
            table.add_row([name, number])
        print table
