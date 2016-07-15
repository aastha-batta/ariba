import os
import pickle
import sys
import pyfastaq
from ariba import reference_data


class Error (Exception): pass

class RefdataQuery:
    def __init__(self,
        prepareref_dir
    ):
        if not os.path.exists(prepareref_dir):
            raise Error('Error querying refdata. Input directory "' + prepareref_dir + '" not found.')

        self.prepareref_dir = prepareref_dir
        self.refdata_fa = os.path.join(self.prepareref_dir, '02.cdhit.all.fa')
        self.refdata_tsv = os.path.join(self.prepareref_dir, '01.filter.check_metadata.tsv')
        self.clusters_pickle = os.path.join(self.prepareref_dir, '02.cdhit.clusters.pickle')


    @staticmethod
    def _load_clusters(pickle_file):
        with open(pickle_file, 'rb') as f:
            clusters = pickle.load(f)
        return clusters


    def _cluster2seqs(self, cluster_name):
        clusters = self._load_clusters(self.clusters_pickle)
        if cluster_name not in clusters:
            return ['Cluster name ' + cluster_name + ' not found']
        else:
            return ['Sequences belonging to cluster ' + cluster_name + ':'] + sorted(list(clusters[cluster_name]))


    def _seqinfo(self, seqname):
        refdata = reference_data.ReferenceData([self.refdata_fa], [self.refdata_tsv])
        if seqname not in refdata.sequences:
            return ['Sequence ' + seqname + ' not found']

        assert seqname in refdata.metadata

        return [
            'Name\t' + seqname,
            'Sequence\t' + refdata.sequences[seqname].seq
        ]


    def query(self, query_type, query_string):
        queries = {
            'cluster2seqs': self._cluster2seqs,
            'seqinfo': self._seqinfo,
        }

        if query_type not in queries:
            raise Error('Unknown query type "' + query_type + '". Choices are:\n' + ','.join(sorted(queries.keys())) + '\n')

        lines = queries[query_type](query_string)
        print(*lines, sep='\n')

