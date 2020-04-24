from unittest import mock, TestCase
from unittest.mock import call

from bs4 import BeautifulSoup

import ffq.ffq as ffq
from tests.mixins import TestMixin


class TestFfq(TestMixin, TestCase):

    def test_parse_run(self):
        with mock.patch('ffq.ffq.cached_get') as cached_get:
            with open(self.fastqs_path, 'r') as f:
                cached_get.return_value = f.read()
            with open(self.run_path, 'r') as f:
                soup = BeautifulSoup(f.read(), 'xml')

            self.assertEqual({
                'accession':
                    'SRR8426358',
                'experiment':
                    'SRX5234128',
                'study':
                    'SRP178136',
                'sample':
                    'SRS4237519',
                'title':
                    'Illumina HiSeq 4000 paired end sequencing; GSM3557675: old_Dropseq_1; Mus musculus; RNA-Seq',
                'files': [{
                    'url':
                        'ftp.sra.ebi.ac.uk/vol1/fastq/SRR842/008/SRR8426358/SRR8426358_1.fastq.gz',
                    'md5':
                        'be7e88cf6f6fd90f1b1170f1cb367123',
                    'size':
                        '5507959060'
                }, {
                    'url':
                        'ftp.sra.ebi.ac.uk/vol1/fastq/SRR842/008/SRR8426358/SRR8426358_2.fastq.gz',
                    'md5':
                        '2124da22644d876c4caa92ffd9e2402e',
                    'size':
                        '7194107512'
                }]
            }, ffq.parse_run(soup))

    def test_parse_run_bam(self):
        with mock.patch('ffq.ffq.cached_get') as cached_get:
            with open(self.fastqs2_path, 'r') as f1, open(self.bam2_path,
                                                          'r') as f2:
                cached_get.side_effect = [f1.read(), f2.read()]
            with open(self.run2_path, 'r') as f:
                soup = BeautifulSoup(f.read(), 'xml')

            with self.assertRaises(Exception):
                ffq.parse_run(soup)

    def test_parse_run_exception(self):
        with mock.patch('ffq.ffq.cached_get') as cached_get:
            with open(self.fastqs2_path, 'r') as f1, open(self.bam_path,
                                                          'r') as f2:
                cached_get.side_effect = [f1.read(), f2.read()]
            with open(self.run2_path, 'r') as f:
                soup = BeautifulSoup(f.read(), 'xml')

            self.assertEqual({
                'accession':
                    'SRR6835844',
                'experiment':
                    'SRX3791763',
                'study':
                    'SRP131661',
                'sample':
                    'SRS3044236',
                'title':
                    'Illumina NovaSeq 6000 sequencing; GSM3040890: library 10X_P4_0; Mus musculus; RNA-Seq',
                'files': [{
                    'url':
                        'ftp.sra.ebi.ac.uk/vol1/SRA653/SRA653146/bam/10X_P4_0.bam',
                    'md5':
                        '5355fe6a07155026085ce46631268ab1',
                    'size':
                        '17093057664'
                }, {
                    'url':
                        'ftp.sra.ebi.ac.uk/vol1/run/SRR683/SRR6835844/10X_P4_0.bam.bai',
                    'md5':
                        'c9396c2596254831470a9138ae86ded7',
                    'size':
                        '7163216'
                }]
            }, ffq.parse_run(soup))

    def test_parse_sample(self):
        with open(self.sample_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'xml')

        self.assertEqual({
            'accession': 'SRS4237519',
            'title': 'old_Dropseq_1',
            'organism': 'Mus musculus',
            'attributes': {
                'source_name': 'Whole lung',
                'tissue': 'Whole lung',
                'age': '24 months',
                'number of cells': '799',
                'ENA-SPOT-COUNT': '109256158',
                'ENA-BASE-COUNT': '21984096610',
                'ENA-FIRST-PUBLIC': '2019-01-11',
                'ENA-LAST-UPDATE': '2019-01-11'
            }
        }, ffq.parse_sample(soup))

    def test_parse_experiment(self):
        with open(self.experiment_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'xml')

        self.assertEqual({
            'accession':
                'SRX5234128',
            'title':
                'Illumina HiSeq 4000 paired end sequencing; GSM3557675: old_Dropseq_1; Mus musculus; RNA-Seq',
            'platform':
                'ILLUMINA',
            'instrument':
                'Illumina HiSeq 4000'
        }, ffq.parse_experiment(soup))

    def test_parse_study(self):
        with open(self.study_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'xml')

        self.assertEqual({
            'accession':
                'SRP178136',
            'title':
                'Multi-modal analysis of the aging mouse lung at cellular resolution',
            'abstract': (
                'A) Whole lung tissue from 24 months (n=7) and 3 months old '
                '(n=8) mice was dissociated and single-cell mRNAseq libraries '
                'generated with Drop-Seq. B) Bulk RNA-seq data was generated '
                'from whole mouse lung tissue of old (n=3) and young (n=3) '
                'samples. C) Bulk RNA-seq data was generated from flow-sorted '
                'macrophages from old (n=7) and young (n=5) mice and '
                'flow-sorted epithelial cells from old (n=4) and young (n=4) '
                'mice. Overall design: Integration of bulk RNA-seq from whole '
                'mouse lung tissue and bulk RNA-seq from flow-sorted lung '
                'macrophages and epithelial cells was used to validate results '
                'obtained from single cell RNA-seq of whole lung tissue.'
            )
        }, ffq.parse_study(soup))

    def test_ffq(self):
        with mock.patch('ffq.ffq.get_xml') as get_xml,\
            mock.patch('ffq.ffq.parse_run') as parse_run,\
            mock.patch('ffq.ffq.parse_sample') as parse_sample,\
            mock.patch('ffq.ffq.parse_experiment') as parse_experiment,\
            mock.patch('ffq.ffq.parse_study') as parse_study:

            run = mock.MagicMock()
            sample = mock.MagicMock()
            experiment = mock.MagicMock()
            study = mock.MagicMock()
            parse_run.return_value = run
            parse_sample.return_value = sample
            parse_experiment.return_value = experiment
            parse_study.return_value = study

            self.assertEqual([run], ffq.ffq(['SRR8426358']))
            self.assertEqual(4, get_xml.call_count)
            get_xml.assert_has_calls([
                call('SRR8426358'),
                call(parse_run()['sample']),
                call(parse_run()['experiment']),
                call(parse_run()['study'])
            ])